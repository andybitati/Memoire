const DATA_LIMIT = 8000;
const AUTO_REFRESH_MS = 5 * 1000;
const VALID_VIEWS = new Set(["overview", "results", "technical"]);

function initialView() {
  const view = new URLSearchParams(window.location.search).get("view");
  return VALID_VIEWS.has(view) ? view : "overview";
}

function captureFocusSelector() {
  const focus = new URLSearchParams(window.location.search).get("capture");
  return {
    resources: ".resourcesPanel",
    audit: ".auditPanel",
    validation: ".validationPanel",
    results: ".detailPanel",
  }[focus] || "";
}

let state = {
  loading: true,
  error: "",
  events: [],
  anomalies: [],
  incidents: [],
  messages: [],
  redisMessages: [],
  audit: [],
  validation: [],
  services: { api: {}, redis: {}, redisPending: {}, mqtt: {}, models: [] },
  resources: {},
  collector: { loading: false, error: "", selected: null, candidates: [] },
  privilege: { loading: false, error: "", result: null },
  runtime: { loading: false, error: "", result: null },
  mqttTest: { loading: false, error: "", result: null },
  autoRun: { loading: false, error: "", result: null },
  explanation: { loading: false, provider: "", text: "", error: "" },
  meta: {},
  filters: { query: "", host: "", severity: "", category: "", source: "" },
  view: initialView(),
  selectedIncidentId: "",
  alertDecisions: {},
  decisionAnimations: {},
  recentDecision: null,
  browserNotifications: false,
  lastRefreshAt: "",
  nextRefreshAt: "",
  realtimeHistory: [],
  autoRefreshEnabled: true,
  autoAnalysisEnabled: true,
  lastAutoAnalysisAt: "",
  refreshMode: "initial",
};

const root = document.getElementById("root");
let autoRefreshTimer = null;
let refreshClockTimer = null;
let refreshInFlight = false;
let analysisInFlight = false;

async function fetchData(type, limit = DATA_LIMIT) {
  const response = await fetch(`/api/data?type=${type}&limit=${limit}`);
  if (!response.ok) throw new Error(`Impossible de charger ${type}`);
  return response.json();
}

async function fetchOptionalData(type, limit = DATA_LIMIT) {
  try {
    return await fetchData(type, limit);
  } catch {
    return { count: 0, data: [] };
  }
}

async function fetchJson(path, options = {}) {
  const response = await fetch(path, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || payload.detail || `Erreur HTTP ${response.status}`);
  return payload;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function uniqueValues(rows, key) {
  return Array.from(new Set(rows.map((row) => row[key]).filter(Boolean))).sort();
}

function normalizeRows(rows) {
  return rows.map((row) => ({
    ...row,
    timestamp_iso:
      row.timestamp_iso ||
      row["_source.@timestamp"] ||
      row.timestamp ||
      row["@timestamp"] ||
      row.TimeCreated ||
      row.time ||
      extractTimestampFromText(row.message || row["_source.full_log"] || row.raw || row.event || ""),
    severity: row.severity || row["_source.rule.level"] || "",
    event: row.event || row["_source.rule.description"] || row["_source.decoder.name"] || "",
    source: row.source || row["_source.location"] || row["_source.decoder.name"] || "",
    host: row.host || row["_source.agent.name"] || row["_source.predecoder.hostname"] || "",
    user: row.user || row["_source.data.dstuser"] || "",
    category: row.category || row["_source.rule.groups"] || row["_source.rule.mitre.tactic"] || "",
    message: row.message || row["_source.full_log"] || row["_source.rule.description"] || "",
  }));
}

function extractTimestampFromText(value) {
  const text = String(value || "");
  const apache = text.match(/\[(\d{1,2})\/([A-Za-z]{3})\/(\d{4}):(\d{2}):(\d{2}):(\d{2})\s+([+-]\d{4})\]/);
  if (apache) {
    const months = {
      Jan: "01", Feb: "02", Mar: "03", Apr: "04", May: "05", Jun: "06",
      Jul: "07", Aug: "08", Sep: "09", Oct: "10", Nov: "11", Dec: "12",
    };
    const [, day, month, year, hour, minute, second, offset] = apache;
    const timezone = `${offset.slice(0, 3)}:${offset.slice(3)}`;
    return `${year}-${months[month] || "01"}-${day.padStart(2, "0")}T${hour}:${minute}:${second}${timezone}`;
  }

  const iso = text.match(/\b\d{4}-\d{2}-\d{2}[T ][\d:.]+(?:Z|[+-]\d{2}:?\d{2})?\b/);
  return iso ? iso[0].replace(" ", "T") : "";
}

function severityClass(value) {
  const severity = String(value || "").toUpperCase();
  if (severity === "CRITICAL") return "danger";
  if (severity === "ERROR") return "error";
  if (severity === "WARNING") return "warning";
  if (severity === "INFO") return "info";
  return "muted";
}

function severityValue(value) {
  const numeric = Number(String(value || "").replace(",", "."));
  if (Number.isFinite(numeric)) return numeric;
  const severity = String(value || "").toUpperCase();
  if (severity === "CRITICAL") return 10;
  if (severity === "ERROR") return 8;
  if (severity === "WARNING") return 5;
  return 0;
}

function numeric(value, fallback = 0) {
  const parsed = Number(String(value ?? "").replace(",", "."));
  return Number.isFinite(parsed) ? parsed : fallback;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function createRealtimeSample(snapshot) {
  const agents = snapshot.resources?.agents || [];
  const cpuCore = numeric(snapshot.resources?.cpu_logminer_core_percent, agents.reduce((total, agent) => total + numeric(agent.cpu_percent), 0));
  const cpuMachine = numeric(snapshot.resources?.cpu_logminer_machine_percent, agents.reduce((total, agent) => total + numeric(agent.cpu_machine_percent), 0));
  const memory = agents.reduce((total, agent) => total + numeric(agent.memory_mb), 0);
  const workflowSec = numeric(snapshot.autoRun?.result?.timings?.workflow_sec, 0);
  const anomalies = pendingAnomalies(snapshot.anomalies || []).filter((row) => row.is_anomaly === "1").length;
  const events = snapshot.meta?.events || snapshot.events?.length || 0;
  const previous = snapshot.realtimeHistory?.[snapshot.realtimeHistory.length - 1];
  const eventDelta = previous ? events - numeric(previous.events) : 0;

  return {
    timestamp: new Date().toISOString(),
    events,
    eventDelta,
    loadedEvents: snapshot.events?.length || 0,
    anomalies,
    incidents: snapshot.incidents?.length || 0,
    workflowSec,
    cpu: cpuMachine,
    cpuCore,
    cpuMachine,
    memory,
  };
}

function worryingKeyword(row) {
  const text = `${row.event || ""} ${row.category || ""} ${row.message || ""}`.toLowerCase();
  return ["sql injection", "xss", "brute force", "attack", "authentication failure", "failed login", "privilege", "malware"].find((keyword) =>
    text.includes(keyword),
  );
}

function urgentAlerts() {
  const incidentAlerts = state.incidents
    .filter((incident) => severityValue(incident.severity) >= 8)
    .map((incident) => ({
      type: "Incident",
      title: incident.summary || incident.incident_id || "Incident critique",
      detail: `${incident.event_count || 0} événements · ${incident.category || "catégorie inconnue"}`,
      severity: incident.severity || "CRITICAL",
      score: severityValue(incident.severity) + Number(incident.event_count || 0) / 10,
    }));

  const anomalyAlerts = pendingAnomalies(state.anomalies)
    .filter((row) => row.is_anomaly === "1" || severityValue(row.severity) >= 7 || worryingKeyword(row))
    .map((row) => {
      const keyword = worryingKeyword(row);
      return {
        type: "Alerte",
        title: row.event || keyword || "Anomalie inquiétante",
        detail: row.message || row.source || row.category || "Signal à vérifier",
        severity: row.severity || (keyword ? "WARNING" : "N/A"),
        score: severityValue(row.severity) + (keyword ? 3 : 0) + Number(row.is_anomaly === "1" ? 2 : 0),
      };
    });

  return [...incidentAlerts, ...anomalyAlerts].sort((a, b) => b.score - a.score).slice(0, 6);
}

function filterRows(rows) {
  const filters = state.filters;
  const query = filters.query.trim().toLowerCase();
  return rows.filter((row) => {
    for (const key of ["host", "severity", "category", "source"]) {
      if (filters[key] && row[key] !== filters[key]) return false;
    }
    if (!query) return true;
    return ["message", "source", "user", "host", "event", "summary"].some((key) =>
      String(row[key] || "").toLowerCase().includes(query),
    );
  });
}

function setFilter(key, value) {
  state = { ...state, filters: { ...state.filters, [key]: value } };
  render();
}

function setView(view) {
  if (!VALID_VIEWS.has(view)) return;
  const url = new URL(window.location.href);
  url.searchParams.set("view", view);
  window.history.replaceState({}, "", url);
  state = { ...state, view };
  render();
}

function selectIncident(incidentId) {
  const url = new URL(window.location.href);
  url.searchParams.set("view", "results");
  window.history.replaceState({}, "", url);
  state = { ...state, selectedIncidentId: incidentId, view: "results" };
  render();
}

function alertKey(row, fallback = "") {
  return String(
    row.alert_id ||
      row.incident_id ||
      row.recno ||
      [row.timestamp_iso, row.event, row.source, row.host, row.message].filter(Boolean).join("|") ||
      fallback,
  );
}

function auditDecisions(rows = state.audit) {
  return rows.reduce((decisions, entry) => {
    if (String(entry.action || "").startsWith("alert.") && entry.target) {
      decisions[String(entry.target)] = {
        action: entry.action,
        decision: String(entry.action).replace("alert.", ""),
        timestamp: entry.timestamp || "",
        actor: entry.actor || "dashboard",
      };
    }
    return decisions;
  }, {});
}

function effectiveAlertDecisions() {
  return { ...auditDecisions(), ...state.alertDecisions };
}

function pendingAnomalies(rows) {
  const decisions = effectiveAlertDecisions();
  return rows.filter((row, index) => !decisions[alertKey(row, `row-${index}`)]);
}

function decisionLabel(decision) {
  return {
    accept: "validée",
    reject: "rejetée",
    reclassify: "reclassée",
  }[decision] || "traitée";
}

function decisionActionLabel(decision) {
  return {
    accept: "Validation",
    reject: "Rejet",
    reclassify: "Reclassement",
  }[decision] || "Décision";
}

function exportRows(filename, rows) {
  if (!rows.length) return;
  const columns = Array.from(rows.reduce((set, row) => {
    Object.keys(row).forEach((key) => set.add(key));
    return set;
  }, new Set()));
  const escapeCsv = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const csv = [columns.join(";")]
    .concat(rows.map((row) => columns.map((column) => escapeCsv(row[column])).join(";")))
    .join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

async function enableBrowserNotifications() {
  if (!("Notification" in window)) {
    state = { ...state, error: "Notifications navigateur non supportées" };
    render();
    return;
  }
  const permission = await Notification.requestPermission();
  state = { ...state, browserNotifications: permission === "granted" };
  render();
}

function maybeNotify(alerts) {
  if (!state.browserNotifications || !alerts.length || !("Notification" in window) || Notification.permission !== "granted") return;
  const latestKey = `${alerts[0].title}|${alerts[0].detail}`;
  if (state.lastNotificationKey === latestKey) return;
  state.lastNotificationKey = latestKey;
  new Notification("Ariel Logminer: alerte prioritaire", {
    body: `${alerts[0].type}: ${alerts[0].title}`,
    silent: false,
  });
}

async function loadData(options = {}) {
  const { mode = "manual", silent = false, skipAutoAnalysis = false } = options;
  if (refreshInFlight) return;
  refreshInFlight = true;
  let shouldRunAutoAnalysis = false;
  state = {
    ...state,
    loading: true,
    error: "",
    refreshMode: mode,
    explanation: silent ? state.explanation : { loading: false, provider: "", text: "", error: "" },
  };
  render();
  try {
    const [events, anomalies, incidents, messages, services, redisEvents, audit, resources] = await Promise.all([
      fetchData("events"),
      fetchData("anomalies"),
      fetchData("incidents", 2000),
      fetchOptionalData("messages", 200),
      fetchJson("/api/services"),
      fetchJson("/api/redis-events?count=100"),
      fetchJson("/api/audit?limit=1000"),
      fetchJson("/api/resources"),
    ]);
    const validation = await fetchOptionalData("validation", 50);
    state = {
      ...state,
      loading: false,
      error: "",
      events: normalizeRows(events.data),
      anomalies: normalizeRows(anomalies.data),
      incidents: normalizeRows(incidents.data),
      messages: messages.data,
      redisMessages: redisEvents.events || [],
      audit: audit.events || [],
      validation: validation.data,
      services,
      resources,
      meta: {
        events: events.count,
        anomalies: anomalies.count,
        incidents: incidents.count,
        messages: messages.count,
        redisMessages: redisEvents.count,
        audit: audit.count,
        validation: validation.count,
      },
      lastRefreshAt: new Date().toISOString(),
      refreshMode: mode,
    };
    state = {
      ...state,
      realtimeHistory: [...state.realtimeHistory, createRealtimeSample(state)].slice(-36),
    };
    shouldRunAutoAnalysis = state.autoAnalysisEnabled && !skipAutoAnalysis && !analysisInFlight;
    scheduleAutoRefresh();
  } catch (error) {
    state = { ...state, loading: false, error: error.message, refreshMode: mode };
    scheduleAutoRefresh();
  } finally {
    refreshInFlight = false;
  }
  render();
  if (shouldRunAutoAnalysis) {
    await runAutonomousScan({ source: "refresh", refreshAfter: true });
  }
}

async function discoverLogs() {
  state = { ...state, collector: { ...state.collector, loading: true, error: "" } };
  render();
  try {
    const result = await fetchJson("/api/collect-discover", { method: "POST" });
    state = {
      ...state,
      collector: {
        loading: false,
        error: "",
        selected: result.selected,
        candidates: result.candidates || [],
      },
      redisMessages: result.run_id ? state.redisMessages : state.redisMessages,
    };
  } catch (error) {
    state = { ...state, collector: { ...state.collector, loading: false, error: error.message } };
  }
  render();
}

async function requestPrivilegedCollect() {
  state = { ...state, privilege: { loading: true, error: "", result: null } };
  render();
  try {
    const result = await fetchJson("/api/privileged-collect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ copy_logs: ["Application", "System", "Security"], days: 2 }),
    });
    state = { ...state, privilege: { loading: false, error: "", result } };
  } catch (error) {
    state = { ...state, privilege: { loading: false, error: error.message, result: null } };
  }
  render();
}

async function runAutonomousScan(options = {}) {
  const { source = "manual", refreshAfter = true } = options;
  if (analysisInFlight) return;
  analysisInFlight = true;
  state = { ...state, autoRun: { loading: true, error: "", result: null }, refreshMode: source === "refresh" ? "analysis" : state.refreshMode };
  render();
  try {
    const result = await fetchJson("/api/auto-run", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    state = { ...state, autoRun: { loading: false, error: "", result }, lastAutoAnalysisAt: new Date().toISOString() };
    if (refreshAfter) {
      await loadData({ mode: "analysis", silent: true, skipAutoAnalysis: true });
    }
    state = { ...state, autoRun: { loading: false, error: "", result } };
  } catch (error) {
    state = { ...state, autoRun: { loading: false, error: error.message, result: null } };
  } finally {
    analysisInFlight = false;
  }
  render();
}

async function decideAlert(alertId, decision, row = {}) {
  if (!alertId || state.decisionAnimations[alertId]?.status === "saving") return;
  state = {
    ...state,
    decisionAnimations: { ...state.decisionAnimations, [alertId]: { decision, status: "saving" } },
    recentDecision: {
      alertId,
      decision,
      status: "Enregistrement dans l'audit système...",
      row,
    },
  };
  render();
  try {
    const result = await fetchJson("/api/alert-decision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        alert_id: alertId,
        decision,
        severity: row.severity || "",
        category: row.category || "",
        reason: row.event || row.message || "",
        run_id: state.autoRun.result?.run_id || latestRun([...state.messages, ...state.redisMessages]) || "",
      }),
    });
    state = {
      ...state,
      decisionAnimations: { ...state.decisionAnimations, [alertId]: { decision, status: "done" } },
      recentDecision: {
        alertId,
        decision,
        status: `Anomalie ${decisionLabel(decision)}. Audit écrit: ${result.audit?.action || `alert.${decision}`}.`,
        row,
      },
    };
    render();
    window.setTimeout(async () => {
      state = {
        ...state,
        alertDecisions: {
          ...state.alertDecisions,
          [alertId]: {
            action: `alert.${decision}`,
            decision,
            timestamp: result.audit?.timestamp || new Date().toISOString(),
            actor: result.audit?.actor || "dashboard",
          },
        },
        decisionAnimations: Object.fromEntries(Object.entries(state.decisionAnimations).filter(([key]) => key !== alertId)),
      };
      render();
      await loadData({ mode: "decision", silent: true, skipAutoAnalysis: true });
    }, 700);
  } catch (error) {
    state = {
      ...state,
      error: error.message,
      decisionAnimations: Object.fromEntries(Object.entries(state.decisionAnimations).filter(([key]) => key !== alertId)),
      recentDecision: {
        alertId,
        decision,
        status: `Décision non enregistrée: ${error.message}`,
        row,
      },
    };
    render();
  }
}

async function prepareRuntime() {
  state = { ...state, runtime: { loading: true, error: "", result: null } };
  render();
  try {
    const result = await fetchJson("/api/runtime-prepare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    state = { ...state, runtime: { loading: false, error: "", result } };
    await loadData();
    state = { ...state, runtime: { loading: false, error: "", result } };
  } catch (error) {
    state = { ...state, runtime: { loading: false, error: error.message, result: null } };
  }
  render();
}

async function testMqttPublish() {
  state = { ...state, mqttTest: { loading: true, error: "", result: null } };
  render();
  try {
    const result = await fetchJson("/api/mqtt-publish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ at: new Date().toISOString() }),
    });
    state = { ...state, mqttTest: { loading: false, error: "", result } };
    await loadData({ mode: "mqtt", silent: true, skipAutoAnalysis: true });
    state = { ...state, mqttTest: { loading: false, error: "", result } };
  } catch (error) {
    state = { ...state, mqttTest: { loading: false, error: error.message, result: null } };
  }
  render();
}

function dashboardSnapshot() {
  const anomalyCount = state.anomalies.filter((row) => row.is_anomaly === "1").length;
  const criticalIncidents = state.incidents.filter((row) => ["CRITICAL", "ERROR"].includes(row.severity)).length;
  const incidents = [...state.incidents].sort((a, b) => Number(b.event_count || 0) - Number(a.event_count || 0));

  return {
    stats: {
      events: state.meta.events || state.events.length,
      anomalies: anomalyCount,
      incidents: state.incidents.length,
      criticalIncidents,
      validationRows: state.meta.validation || state.validation.length,
    },
    incidents: incidents.slice(0, 8),
    validation: state.validation.slice(0, 8),
    recentMessages: state.messages.slice(-10),
    topAnomalies: state.anomalies.slice(0, 8),
  };
}

async function explainDashboard() {
  state = { ...state, explanation: { loading: true, provider: "", text: "", error: "" } };
  render();

  try {
    const response = await fetch("/api/explain", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dashboardSnapshot()),
    });
    if (!response.ok) throw new Error("Impossible de produire l'explication");
    const payload = await response.json();
    state = {
      ...state,
      explanation: {
        loading: false,
        provider: payload.provider || "local",
        text: payload.explanation || "",
        error: payload.warning || "",
      },
    };
  } catch (error) {
    state = { ...state, explanation: { loading: false, provider: "", text: "", error: error.message } };
  }

  render();
}

function optionList(values, selected) {
  return [`<option value="">Tous</option>`]
    .concat(values.map((value) => `<option value="${escapeHtml(value)}" ${value === selected ? "selected" : ""}>${escapeHtml(value)}</option>`))
    .join("");
}

function sidebar() {
  const filterSource = state.anomalies.length ? state.anomalies : state.events;
  const options = {
    host: uniqueValues(filterSource, "host"),
    severity: uniqueValues(filterSource, "severity"),
    category: uniqueValues(filterSource, "category"),
    source: uniqueValues(filterSource, "source").slice(0, 200),
  };

  return `
    <aside class="sidebar">
      <div class="brand">
        <img class="brandLogo" src="/ariel_logminer_logo_text.png" alt="Ariel Logminer" />
        <span class="hudBadge">SOC V2</span>
      </div>
      <button class="primaryAction" id="reloadBtn" ${state.loading ? "disabled" : ""}><span class="icon">↻</span>Actualiser</button>
      <button class="secondaryAction" id="browserNotifBtn"><span class="icon">!</span>${state.browserNotifications ? "Notifications actives" : "Activer notifications"}</button>
      <button class="secondaryAction" id="runtimeBtn" ${state.runtime.loading ? "disabled" : ""}><span class="icon">◉</span>${state.runtime.loading ? "Préparation" : "Préparer runtime"}</button>
      <button class="secondaryAction" id="privilegedBtn" ${state.privilege.loading ? "disabled" : ""}><span class="icon">⌘</span>${state.privilege.loading ? "Demande" : "Autoriser journaux sensibles"}</button>
      <button class="secondaryAction" id="discoverBtn" ${state.collector.loading ? "disabled" : ""}><span class="icon">⌕</span>${state.collector.loading ? "Recherche" : "Trouver les journaux"}</button>
      <button class="primaryAction" id="autoRunBtn" ${state.autoRun.loading ? "disabled" : ""}><span class="icon">▶</span>${state.autoRun.loading ? "Analyse en cours" : "Lancer l'analyse"}</button>
      <div class="viewSwitch">
        <button data-view="overview" class="${state.view === "overview" ? "activeView" : ""}">Vue d'ensemble</button>
        <button data-view="results" class="${state.view === "results" ? "activeView" : ""}">Résultats</button>
        <button data-view="technical" class="${state.view === "technical" ? "activeView" : ""}">Technique</button>
      </div>
      <label class="search"><span class="icon">⌕</span><input id="queryFilter" value="${escapeHtml(state.filters.query)}" placeholder="Rechercher message, source, user" /></label>
      <div class="filterTitle"><span class="icon">≡</span>Filtres</div>
      ${Object.entries(options)
        .map(
          ([key, values]) => `
            <label class="field">
              <span>${escapeHtml(key)}</span>
              <select data-filter="${escapeHtml(key)}">${optionList(values, state.filters[key])}</select>
            </label>
          `,
        )
        .join("")}
    </aside>
  `;
}

function stat(icon, label, value, tone) {
  return `
    <section class="stat ${tone}">
      <span class="icon">${icon}</span>
      <div><span>${escapeHtml(label)}</span><strong>${Number(value || 0).toLocaleString("fr-FR")}</strong></div>
    </section>
  `;
}

function statusBadge(label, ok, detail) {
  return `
    <div class="serviceItem">
      <span class="dot ${ok ? "" : "errorDot"}"></span>
      <div><strong>${escapeHtml(label)}</strong><small>${escapeHtml(detail || (ok ? "OK" : "À vérifier"))}</small></div>
    </div>
  `;
}

function hudRing(label, value, detail, tone = "") {
  return `
    <div class="hudRing ${tone}">
      <div class="ringCore">
        <span>${escapeHtml(String(value))}</span>
      </div>
      <strong>${escapeHtml(label)}</strong>
      <small>${escapeHtml(detail || "")}</small>
    </div>
  `;
}

const AGENT_LABELS = {
  collector: "Collecteur",
  parser: "Parseur",
  normalizer: "Normaliseur",
  detector: "Détecteur IA",
  correlator: "Corrélateur",
  visualizer: "Visualiseur",
  orchestrator: "Orchestrateur",
  dashboard: "Dashboard",
  runtime: "Runtime Docker",
  privilege: "Autorisation admin",
};

const MESSAGE_LABELS = {
  "workflow.started": "Workflow lancé",
  "workflow.completed": "Workflow terminé",
  "collector.discovery.started": "Recherche des journaux",
  "collector.discovery.completed": "Journaux trouvés",
  "runtime.prepare.started": "Préparation runtime",
  "runtime.prepare.completed": "Runtime prêt",
  "privilege.request.started": "Autorisation demandée",
  "privilege.request.completed": "Autorisation traitée",
  "parse.started": "Parsing lancé",
  "parse.completed": "Parsing terminé",
  "detection.started": "Détection lancée",
  "detection.completed": "Détection terminée",
  "correlation.started": "Corrélation lancée",
  "correlation.completed": "Corrélation terminée",
};

function agentName(value) {
  return AGENT_LABELS[String(value || "").toLowerCase()] || String(value || "Agent inconnu");
}

function messageTitle(message) {
  return MESSAGE_LABELS[message.message_type] || String(message.message_type || "Message agent");
}

function formatDateTime(value) {
  const date = new Date(value || "");
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatTime(value) {
  const date = new Date(value || "");
  if (Number.isNaN(date.getTime())) return "--:--";
  return new Intl.DateTimeFormat("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

function remainingRefreshLabel() {
  if (!state.nextRefreshAt) return "Auto 5 s";
  const remaining = Math.max(0, new Date(state.nextRefreshAt).getTime() - Date.now());
  const minutes = Math.floor(remaining / 60000);
  const seconds = Math.floor((remaining % 60000) / 1000);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

function updateRefreshClock() {
  const nextNode = document.getElementById("nextRefreshClock");
  const lastNode = document.getElementById("lastRefreshClock");
  if (nextNode) nextNode.textContent = remainingRefreshLabel();
  if (lastNode) lastNode.textContent = state.lastRefreshAt ? formatTime(state.lastRefreshAt) : "--:--";
}

function scheduleAutoRefresh() {
  window.clearTimeout(autoRefreshTimer);
  const nextRefreshAt = new Date(Date.now() + AUTO_REFRESH_MS).toISOString();
  state = { ...state, nextRefreshAt };
  autoRefreshTimer = window.setTimeout(() => {
    loadData({ mode: "auto", silent: true });
  }, AUTO_REFRESH_MS);
  updateRefreshClock();
}

function startRefreshClock() {
  window.clearInterval(refreshClockTimer);
  refreshClockTimer = window.setInterval(updateRefreshClock, 1000);
  updateRefreshClock();
}

function payloadSummary(payload) {
  if (!payload || typeof payload !== "object") return "";
  const readableKeys = {
    input_csv: "entrée",
    output_csv: "sortie",
    events: "événements",
    anomalies: "anomalies",
    incidents: "incidents",
    files: "fichiers",
    window_minutes: "fenêtre",
  };
  return Object.entries(payload)
    .filter(([, value]) => value !== "" && value !== null && value !== undefined)
    .slice(0, 4)
    .map(([key, value]) => `${readableKeys[key] || key}: ${String(value)}`)
    .join(" · ");
}

function latestRun(messages) {
  return [...messages].reverse().find((message) => message.run_id)?.run_id || "";
}

function pipelineTopologyPanel() {
  const redisOk = state.services.redis?.status === "ok";
  const apiOk = state.services.api?.status === "ok";
  const result = state.autoRun.result;

  return `
    <section class="panel hudPanel">
      <div class="panelHeader">
        <div>
          <h2>Topologie du Pipeline Multi-Agents</h2>
          <p>Architecture distribuée et flux d'analyse autonome</p>
        </div>
        <span class="icon">↬</span>
      </div>
      <div class="pipelineTopology">
        <div class="agentNode active">
          <strong>Collecteur</strong>
          <small>${state.collector.selected ? "Source active" : "Scanner"}</small>
        </div>
        <div class="nodeConnector"></div>
        <div class="agentNode active">
          <strong>Parseur</strong>
          <small>Normalisation</small>
        </div>
        <div class="nodeConnector"></div>
        <div class="agentNode active">
          <strong>Détecteur IA</strong>
          <small>Scoring d'anomalies</small>
        </div>
        <div class="nodeConnector"></div>
        <div class="agentNode active">
          <strong>Corrélateur</strong>
          <small>Regroupement</small>
        </div>
        <div class="nodeConnector"></div>
        <div class="agentNode active">
          <strong>Visualiseur</strong>
          <small>Poste SOC HUD</small>
        </div>
      </div>
    </section>
  `;
}

function servicePanel() {
  const { api, redis, redisPending, mqtt, models } = state.services;
  const runtime = state.runtime.result || state.services.runtime || {};
  const modelCount = (models || []).filter((model) => model.exists).length;
  const selected = state.collector.selected;
  const result = state.autoRun.result;
  const privilege = state.privilege.result;
  const mqttTest = state.mqttTest || {};
  const pendingJobs = redisPending?.pending?.pending ?? redisPending?.pending_count ?? 0;

  return `
    <section class="panel servicePanel">
      <div class="panelHeader">
        <div><h2>Services V2</h2><p>${escapeHtml(state.services.apiBase || "FastAPI locale")}</p></div>
        <span class="icon">◎</span>
      </div>
      <div class="serviceGrid">
        <div class="serviceItem"><span class="dot ${api?.status === "ok" ? "" : "errorDot"}"></span><div><strong>FastAPI</strong><small>${escapeHtml(api?.status || "inconnu")}</small></div></div>
        <div class="serviceItem"><span class="dot ${redis?.status === "ok" ? "" : "errorDot"}"></span><div><strong>Redis Streams</strong><small>${escapeHtml(redis?.stream || redis?.error || "non vérifié")}</small></div></div>
        <div class="serviceItem"><span class="dot ${mqtt?.status === "ok" ? "" : "errorDot"}"></span><div><strong>MQTT</strong><small>${escapeHtml(mqtt?.status === "ok" ? `${mqtt.host || "localhost"}:${mqtt.port || 1883}` : mqtt?.error || "non vérifié")}</small></div></div>
        <div class="serviceItem"><span class="dot ${Number(pendingJobs) ? "warnDot" : ""}"></span><div><strong>Jobs pending</strong><small>${escapeHtml(pendingJobs)} job(s) Redis</small></div></div>
        <div class="serviceItem"><span class="dot ${runtime?.docker_engine ? "" : "errorDot"}"></span><div><strong>Docker</strong><small>${escapeHtml(runtime?.message || "état non vérifié")}</small></div></div>
        <div class="serviceItem"><span class="dot"></span><div><strong>Modèles IA</strong><small>${modelCount}/${(models || []).length} artefacts</small></div></div>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <button class="secondaryAction" id="mqttTestBtn" ${mqttTest.loading ? "disabled" : ""}>${mqttTest.loading ? "Test MQTT..." : "Tester MQTT"}</button>
        ${mqttTest.result ? `<small style="color:var(--emerald);">MQTT publié: ${escapeHtml(mqttTest.result.message?.message_type || "ok")}</small>` : ""}
        ${mqttTest.error ? `<small style="color:var(--crimson);">${escapeHtml(mqttTest.error)}</small>` : ""}
      </div>
      <div class="rationaleBox">
        <strong>Source & Collecte Active :</strong>
        <span>${selected ? escapeHtml(selected.path) : "Aucun fichier sélectionné par le collecteur."}</span>
        ${result ? `<br/><small style="color:var(--cyan);">Dernier run: ${escapeHtml(result.run_id)} · ${escapeHtml(result.anomalies_rows ?? "0")} anomalies · ${escapeHtml(result.incidents_rows ?? "0")} incidents</small>` : ""}
        ${privilege ? `<br/><small style="color:var(--gold);">Accès sensible: ${escapeHtml(privilege.message || (privilege.launched ? "demande lancée" : "non autorisé"))}</small>` : ""}
      </div>
    </section>
  `;
}

function operatorSummaryPanel() {
  const redisOk = state.services.redis?.status === "ok";
  const mqttOk = state.services.mqtt?.status === "ok";
  const apiOk = state.services.api?.status === "ok";
  const latestAudit = state.audit[state.audit.length - 1];
  const result = state.autoRun.result;
  const selected = state.collector.selected;
  const nextAction = result
    ? "Consulter les résultats d'incidents ou demander une explication synthétique par l'analyste."
    : selected
      ? "Lancer l'analyse autonome pour traiter les journaux détectés."
      : "Rechercher les journaux puis lancer l'analyse autonome.";

  return `
    <section class="starkHero">
      <div class="missionBrief">
        <span class="hudBadge">SOC COMMAND CENTER</span>
        <h2>Recommandation J.A.R.V.I.S.</h2>
        <p>${escapeHtml(nextAction)}</p>
        <div class="hudMiniGrid">
          ${hudRing("API", apiOk ? "ON" : "OFF", apiOk ? "Disponible" : "À vérifier", apiOk ? "ok" : "warn")}
          ${hudRing("REDIS", redisOk ? "ON" : "OFF", redisOk ? "Bus actif" : "Bus absent", redisOk ? "ok" : "warn")}
          ${hudRing("MQTT", mqttOk ? "ON" : "OFF", mqttOk ? "Pub/sub actif" : "Optionnel", mqttOk ? "ok" : "idle")}
          ${hudRing("AUDIT", latestAudit ? "LOG" : "---", latestAudit ? latestAudit.action : "Aucune action", latestAudit ? "ok" : "idle")}
        </div>
      </div>
      <div style="display:flex; flex-direction:column; gap:10px;">
        ${statusBadge("FastAPI Server", apiOk, apiOk ? "Disponible" : state.services.api?.error)}
        ${statusBadge("Bus Messages Redis", redisOk, redisOk ? "Canal agents actif" : state.services.redis?.error)}
        ${statusBadge("Broker MQTT", mqttOk, mqttOk ? "Pub/sub opérationnel" : state.services.mqtt?.error || "Optionnel")}
        ${statusBadge("Audit Système", Boolean(latestAudit), latestAudit ? latestAudit.action : "Aucune action enregistrée")}
      </div>
    </section>
  `;
}

function warningNotificationPanel(alerts) {
  if (!alerts.length) return "";
  const top = alerts[0];
  return `
    <section class="warningBanner" role="alert">
      <div class="warningIcon">!</div>
      <div class="warningContent">
        <span class="hudBadge" style="background:var(--crimson); color:#fff;">URGENT</span>
        <h2>${escapeHtml(alerts.length)} signalement${alerts.length > 1 ? "s" : ""} prioritaire${alerts.length > 1 ? "s" : ""} détecté${alerts.length > 1 ? "s" : ""}</h2>
        <p>${escapeHtml(top.type)}: ${escapeHtml(top.title)} · ${escapeHtml(top.detail)}</p>
        <div class="warningList">
          ${alerts
            .slice(0, 3)
            .map(
              (alert) => `
                <article>
                  <strong>${escapeHtml(alert.type)} · ${escapeHtml(alert.title)}</strong>
                  <span>${escapeHtml(alert.detail)}</span>
                </article>
              `,
            )
            .join("")}
        </div>
      </div>
      <button class="warningAction" id="openResultsBtn">Examiner l'incident</button>
    </section>
  `;
}

function resourcesPanel() {
  const resources = state.resources || {};
  const agents = resources.agents || [];
  const logicalCpus = resources.logical_cpus || "";
  return `
    <section class="panel resourcesPanel">
      <div class="panelHeader">
        <div><h2>Télémétrie Ressources par Agent</h2><p>${escapeHtml(resources.message || "Utilisation CPU et Mémoire normalisée")}${logicalCpus ? ` · ${escapeHtml(logicalCpus)} cœurs logiques` : ""}</p></div>
        <span class="icon">◷</span>
      </div>
      ${
        resources.available
          ? agents.length
            ? `<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:12px;">
                ${agents
                  .map(
                    (agent) => `
                      <article style="background:rgba(4,9,22,0.8); border:1px solid var(--panel-border); padding:12px; border-radius:8px;">
                        <strong>${escapeHtml(agent.agent || "Agent Ariel Logminer")}</strong>
                        <div style="font-size:11px; color:var(--text-muted); margin:4px 0 8px;">PID ${escapeHtml(agent.pids || agent.pid || "")} · ${escapeHtml(agent.status || "actif")}</div>
                        <div style="display:flex; justify-content:space-between; font-size:12px;">
                          <span>CPU Machine: <b style="color:var(--gold);">${escapeHtml(agent.cpu_machine_percent ?? 0)}%</b></span>
                          <span>RAM: <b style="color:var(--cyan);">${escapeHtml(agent.memory_mb ?? 0)} MB</b></span>
                        </div>
                      </article>
                    `,
                  )
                  .join("")}
              </div>`
            : `<div class="emptyState">Aucun agent actuellement en cours d'exécution.</div>`
          : `<div class="emptyState">${escapeHtml(resources.message || "Mesure des ressources indisponible.")}</div>`
      }
    </section>
  `;
}

function sparkline(points, key, options = {}) {
  const width = 420;
  const height = 120;
  const padX = 14;
  const padY = 16;
  const values = points.map((point) => numeric(point[key])).filter((value) => Number.isFinite(value));
  const max = Math.max(...values, options.minMax || 1);
  const min = options.forceZero ? 0 : Math.min(...values, 0);
  const range = Math.max(max - min, 1);
  const coords = points.map((point, index) => {
    const x = padX + (index / Math.max(1, points.length - 1)) * (width - padX * 2);
    const y = height - padY - ((numeric(point[key]) - min) / range) * (height - padY * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  const last = values.length ? values[values.length - 1] : 0;

  return `
    <svg class="realtimeSvg" viewBox="0 0 ${width} ${height}">
      <line x1="${padX}" y1="${height - padY}" x2="${width - padX}" y2="${height - padY}" class="chartAxis"></line>
      <polyline points="${coords.join(" ")}" class="chartLine ${options.tone || ""}"></polyline>
      <text x="${width - 16}" y="24" text-anchor="end" class="chartValue">${escapeHtml(options.format ? options.format(last) : last.toFixed(1))}</text>
      <text x="16" y="24" class="chartLabel">${escapeHtml(options.label || key)}</text>
    </svg>
  `;
}

function realtimeBars(points, key, options = {}) {
  const values = points.map((point) => numeric(point[key]));
  const max = Math.max(...values, 1);
  return `
    <div class="realtimeBars">
      ${points
        .map((point) => {
          const value = numeric(point[key]);
          const height = Math.max(6, (value / max) * 100);
          return `<span style="height:${height}%" title="${escapeHtml(formatTime(point.timestamp))}: ${escapeHtml(value)}"></span>`;
        })
        .join("")}
    </div>
  `;
}

function severityChart(rows) {
  const groups = rows.reduce((acc, row) => {
    const label = String(row.severity || "N/A").toUpperCase() || "N/A";
    acc[label] = (acc[label] || 0) + 1;
    return acc;
  }, {});
  const entries = Object.entries(groups).sort((a, b) => b[1] - a[1]).slice(0, 6);
  const max = Math.max(...entries.map(([, count]) => count), 1);

  return `
    <div style="display:flex; flex-direction:column; gap:8px;">
      ${
        entries.length
          ? entries
              .map(
                ([label, count]) => `
                  <div style="display:flex; align-items:center; gap:10px;">
                    <span class="pill ${severityClass(label)}">${escapeHtml(label)}</span>
                    <div style="flex:1; background:rgba(0,240,255,0.1); height:8px; border-radius:4px; overflow:hidden;">
                      <div style="width:${Math.max(4, (count / max) * 100)}%; background:var(--cyan); height:100%;"></div>
                    </div>
                    <strong style="font-size:12px; min-width:30px;">${count.toLocaleString("fr-FR")}</strong>
                  </div>
                `,
              )
              .join("")
          : `<div class="emptyState">Aucune sévérité disponible.</div>`
      }
    </div>
  `;
}

function realtimeChartsPanel(events, anomalies, incidents) {
  const history = state.realtimeHistory.length ? state.realtimeHistory : [createRealtimeSample(state)];
  const last = history[history.length - 1] || {};
  const visibleEvents = events.length;

  return `
    <section class="panel realtimePanel">
      <div class="panelHeader">
        <div>
          <h2>Télémétrie Temporelle & Performance</h2>
          <p>Mises à jour toutes les 5 secondes · Dernier échantillon ${escapeHtml(formatTime(last.timestamp))}</p>
        </div>
        <span class="icon">⌁</span>
      </div>
      <div class="realtimeGrid">
        <article class="realtimeCard wideRealtime">
          <div class="cardCaption">
            <strong>Durée d'Exécution Workflow</strong>
            <span>${last.workflowSec ? `${numeric(last.workflowSec).toFixed(2)} s` : "analysé en temps réel"}</span>
          </div>
          ${sparkline(history, "workflowSec", { label: "Temps Workflow", forceZero: true, format: (v) => `${v.toFixed(2)} s`, tone: "latencyLine" })}
        </article>
        <article class="realtimeCard">
          <div class="cardCaption">
            <strong>Volume d'Événements</strong>
            <span>${visibleEvents.toLocaleString("fr-FR")} événements filtrés</span>
          </div>
          ${realtimeBars(history, "events", { label: "Événements" })}
        </article>
        <article class="realtimeCard">
          <div class="cardCaption">
            <strong>Taux d'Anomalies</strong>
            <span>${anomalies.length.toLocaleString("fr-FR")} détections</span>
          </div>
          ${sparkline(history, "anomalies", { label: "Anomalies", forceZero: true, format: (v) => v.toLocaleString("fr-FR") })}
        </article>
        <article class="realtimeCard">
          <div class="cardCaption">
            <strong>Distribution Sévérités</strong>
            <span>Anomalies candidates</span>
          </div>
          ${severityChart(anomalies)}
        </article>
      </div>
    </section>
  `;
}

function auditPanel(rows) {
  return `
    <section class="panel">
      <div class="panelHeader"><h2>Journal d'Audit Système</h2><span class="icon">▤</span></div>
      ${rows
        .slice(-12)
        .reverse()
        .map(
          (entry) => `
            <div style="padding:8px 12px; border-bottom:1px solid var(--line); display:flex; justify-content:space-between; align-items:center;">
              <div>
                <strong style="color:var(--cyan);">${escapeHtml(entry.action)}</strong>
                <span style="font-size:12px; color:var(--text-muted); margin-left:8px;">Target: ${escapeHtml(entry.target || "système")}</span>
              </div>
              <small style="color:var(--emerald);">${escapeHtml(entry.status || "ok")}</small>
            </div>
          `,
        )
        .join("") || `<div class="emptyState">Aucune action d'audit récente.</div>`}
    </section>
  `;
}

function agentFlowPanel(messages) {
  const runId = latestRun(messages);
  const rows = runId ? messages.filter((message) => message.run_id === runId) : messages;
  const ordered = rows.slice(-10);

  return `
    <section class="panel">
      <div class="panelHeader">
        <div><h2>Flux des Messages Agents</h2><p>${runId ? `Run active ${escapeHtml(runId.slice(0, 14))}` : "Run en direct"}</p></div>
        <span class="icon">↬</span>
      </div>
      ${
        ordered.length
          ? `<div style="display:flex; flex-direction:column; gap:8px;">
              ${ordered
                .map(
                  (message) => `
                    <div style="background:rgba(4,9,22,0.8); border:1px solid var(--panel-border); padding:10px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
                      <div>
                        <strong style="color:var(--text-main);">${escapeHtml(messageTitle(message))}</strong>
                        <div style="font-size:11px; color:var(--cyan);">${escapeHtml(agentName(message.source))} ➔ ${escapeHtml(agentName(message.target))}</div>
                      </div>
                      <small style="color:var(--text-dim);">${escapeHtml(formatTime(message.timestamp))}</small>
                    </div>
                  `,
                )
                .join("")}
            </div>`
          : `<div class="emptyState">Aucun message agent disponible.</div>`
      }
    </section>
  `;
}

function validationPanel(rows) {
  return `
    <section class="panel">
      <div class="panelHeader"><h2>Validation Modèles IA</h2><span class="icon">✓</span></div>
      ${
        rows.length
          ? rows
              .slice(0, 5)
              .map(
                (row) => `
                  <div style="padding:10px; border-bottom:1px solid var(--line); display:flex; justify-content:space-between; align-items:center;">
                    <div>
                      <strong style="color:var(--cyan);">${escapeHtml(String(row.dataset || "").toUpperCase())} · ${escapeHtml(row.model)}</strong>
                      <div style="font-size:11px; color:var(--text-muted);">F1: ${escapeHtml(row.f1)} | Recall: ${escapeHtml(row.recall)} | Precision: ${escapeHtml(row.precision)}</div>
                    </div>
                    <span class="pill info">${escapeHtml(row.events || "0")} lignes</span>
                  </div>
                `,
              )
              .join("")
          : `<div class="emptyState">Aucune métrique de validation disponible.</div>`
      }
    </section>
  `;
}

function explanationPanel() {
  const { loading, provider, text, error } = state.explanation;
  const providerLabel = provider === "openai" ? "Synthèse LLM OpenAI" : provider === "local" ? "Synthèse Expert Locale" : "Prêt";

  return `
    <section class="panel">
      <div class="panelHeader">
        <div><h2>Explication Synthetique Analyste</h2><p>${escapeHtml(providerLabel)}</p></div>
        <button class="primaryAction" id="explainBtn" ${loading || state.loading ? "disabled" : ""} style="width:auto;">
          <span class="icon">${loading ? "…" : "✦"}</span>${loading ? "Génération en cours..." : "Expliquer les résultats"}
        </button>
      </div>
      ${
        text
          ? `<div class="explanationText">${escapeHtml(text)}</div>`
          : `<div class="emptyState">Cliquez sur "Expliquer les résultats" pour générer une synthèse opérationnelle des incidents et des signaux.</div>`
      }
      ${error ? `<div style="color:var(--crimson); font-size:12px; margin-top:8px;">${escapeHtml(error)}</div>` : ""}
    </section>
  `;
}

function incidentsPanel(rows) {
  const sorted = [...rows].sort((a, b) => Number(b.event_count || 0) - Number(a.event_count || 0));
  return `
    <section class="panel">
      <div class="panelHeader"><h2>Incidents Corrélés</h2><span class="icon">⇄</span></div>
      <div class="incidentList">
        ${sorted
          .slice(0, 8)
          .map(
            (incident) => `
              <article class="incident">
                <div>
                  <strong>${escapeHtml(incident.incident_id)}</strong>
                  <span>${escapeHtml(incident.summary)}</span>
                  <div style="font-size:11px; color:var(--text-muted); margin-top:4px;">${escapeHtml(formatDateTime(incident.start_time))} → ${escapeHtml(formatDateTime(incident.end_time))}</div>
                </div>
                <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
                  <span class="pill ${severityClass(incident.severity)}">${escapeHtml(incident.severity || "N/A")}</span>
                  <button class="miniAction" data-incident-id="${escapeHtml(incident.incident_id || "")}">Inspecter</button>
                </div>
              </article>
            `,
          )
          .join("") || `<div class="emptyState">Aucun incident corrélé pour le moment.</div>`}
      </div>
    </section>
  `;
}

function incidentDetailPanel(incident, anomalies) {
  if (!incident) {
    return `
      <section class="panel">
        <div class="panelHeader"><h2>Inspecteur d'Incident</h2><span class="icon">◎</span></div>
        <div class="emptyState">Sélectionnez un incident ci-dessus pour inspecter son détail et ses événements associés.</div>
      </section>
    `;
  }
  const start = new Date(incident.start_time || "");
  const end = new Date(incident.end_time || "");
  const eventIds = new Set(String(incident.events || "").split(",").filter(Boolean));
  const related = anomalies
    .filter((row) => {
      const date = new Date(row.timestamp_iso || "");
      const inWindow =
        !Number.isNaN(start.getTime()) &&
        !Number.isNaN(end.getTime()) &&
        !Number.isNaN(date.getTime()) &&
        date >= start &&
        date <= end;
      const sameHost = !incident.host || !row.host || row.host === incident.host;
      return inWindow && sameHost;
    })
    .slice(0, 10);

  return `
    <section class="panel">
      <div class="panelHeader">
        <div><h2>Détail Incident : ${escapeHtml(incident.incident_id || "")}</h2><p>${escapeHtml(incident.summary || "")}</p></div>
        <button class="secondaryAction" id="exportIncidentBtn" style="width:auto;"><span class="icon">⇩</span>Exporter Détail</button>
      </div>
      <div class="detailGrid">
        <div><strong>Fenêtre Temporelle</strong><span>${escapeHtml(formatDateTime(incident.start_time))} → ${escapeHtml(formatDateTime(incident.end_time))}</span></div>
        <div><strong>Hôte / Source</strong><span>${escapeHtml(incident.host || "host")} · ${escapeHtml(incident.source || "source")}</span></div>
        <div><strong>Sévérité</strong><span>${escapeHtml(incident.priority || incident.severity || "N/A")}</span></div>
        <div><strong>Événements Liés</strong><span>${escapeHtml(incident.event_count || "0")}</span></div>
      </div>
      <div class="rationaleBox">
        <strong>Justification & Cause Racine Probable :</strong><br/>
        ${escapeHtml(incident.rationale || "Analyse automatique basée sur la corrélation temporelle et la répétition des signatures d'anomalie.")}
      </div>
      <div style="display:flex; flex-direction:column; gap:6px;">
        <strong style="font-size:12px; color:var(--cyan); text-transform:uppercase;">Anomalies Sources Correspondantes :</strong>
        ${
          related.length
            ? related
                .map(
                  (row) => `
                    <div style="background:rgba(4,9,22,0.8); border:1px solid var(--panel-border); padding:8px 12px; border-radius:6px; font-size:12px;">
                      <strong>${escapeHtml(row.event || row.category || "Anomalie")}</strong>
                      <span style="color:var(--text-muted); margin-left:8px;">${escapeHtml(formatDateTime(row.timestamp_iso))}</span>
                      <div style="color:var(--text-dim); margin-top:2px;">${escapeHtml(row.message || "")}</div>
                    </div>
                  `,
                )
                .join("")
            : `<div class="emptyState">Aucune anomalie source isolée dans la fenêtre exacte.</div>`
        }
      </div>
    </section>
  `;
}

function dataTable(title, rows, columns, icon, options = {}) {
  return `
    <section class="panel">
      <div class="panelHeader">
        <h2>${escapeHtml(title)}</h2>
        <div style="display:flex; gap:10px; align-items:center;">
          ${options.exportName ? `<button class="secondaryAction" data-export="${escapeHtml(options.exportName)}" style="width:auto;"><span class="icon">⇩</span>Exporter CSV</button>` : ""}
          <span class="icon">${icon}</span>
        </div>
      </div>
      <div class="tableWrap">
        <table>
          <thead><tr>${options.alertActions ? `<th class="decisionColumn">Décision Analyste</th>` : ""}${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead>
          <tbody>
            ${rows
              .slice(0, 100)
              .map((row, index) => {
                const alertId = alertKey(row, `row-${index}`);
                const animation = state.decisionAnimations[alertId] || {};
                return `
                  <tr>
                    ${
                      options.alertActions
                        ? `<td class="decisionColumn">
                            <div class="decisionActions">
                              <button class="acceptDecision" data-alert-action="accept" data-alert-index="${index}" title="Valider l'alerte">Valider</button>
                              <button class="rejectDecision" data-alert-action="reject" data-alert-index="${index}" title="Rejeter l'alerte">Rejeter</button>
                              <button class="reclassifyDecision" data-alert-action="reclassify" data-alert-index="${index}" title="Reclasser l'alerte">Reclasser</button>
                            </div>
                          </td>`
                        : ""
                    }
                    ${columns
                      .map((column) => {
                        const value = row[column] || "";
                        if (column === "severity") {
                          return `<td><span class="pill ${severityClass(value)}">${escapeHtml(value || "N/A")}</span></td>`;
                        }
                        return `<td>${escapeHtml(value)}</td>`;
                      })
                      .join("")}
                  </tr>
                `;
              })
              .join("")}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function render() {
  const filteredEvents = filterRows(state.events);
  const pending = pendingAnomalies(state.anomalies);
  const filteredAnomalies = filterRows(pending);
  const anomalyCount = pending.filter((row) => row.is_anomaly === "1").length;
  const criticalIncidents = state.incidents.filter((row) => ["CRITICAL", "ERROR"].includes(row.severity)).length;
  const sourceEventCount = Math.max(
    numeric(state.meta.events),
    numeric(state.autoRun.result?.input_rows),
    state.events.length,
  );
  const alerts = urgentAlerts();
  const selectedIncident = state.incidents.find((incident) => incident.incident_id === state.selectedIncidentId) || state.incidents[0] || null;
  document.title = alerts.length ? `(${alerts.length}) Alertes Ariel Logminer` : "Ariel Logminer";
  maybeNotify(alerts);

  root.innerHTML = `
    <div class="app">
      ${sidebar()}
      <main class="content">
        <header class="topbar">
          <div><span>CENTRE DE COMMANDEMENT SOC</span><h1>Ariel Logminer HUD</h1></div>
          <div class="statusCluster">
            <div class="status"><span class="${state.error ? "dot errorDot" : "dot"}"></span>${escapeHtml(state.error || (state.loading ? "Synchronisation" : "Système Synchronisé"))}</div>
            <div class="refreshHud">
              <strong>${state.autoRun.loading ? "Analyse en cours..." : "Surveillance Temps Réel"}</strong>
              <span><b id="nextRefreshClock">${escapeHtml(remainingRefreshLabel())}</b> · dernier <b id="lastRefreshClock">${escapeHtml(state.lastRefreshAt ? formatTime(state.lastRefreshAt) : "--:--")}</b></span>
            </div>
          </div>
        </header>

        ${warningNotificationPanel(alerts)}

        <div class="statsGrid">
          ${stat("▣", "Événements Source", sourceEventCount, "blue")}
          ${stat("⚠", "Anomalies Candidates", anomalyCount, "amber")}
          ${stat("⇄", "Incidents Corrélés", state.incidents.length, "green")}
          ${stat("!", "Incidents Critiques", criticalIncidents, "rose")}
        </div>

        ${
          state.view === "overview"
            ? `
              ${operatorSummaryPanel()}
              ${pipelineTopologyPanel()}
              ${realtimeChartsPanel(filteredEvents, filteredAnomalies, state.incidents)}
              ${incidentsPanel(state.incidents)}
              ${explanationPanel()}
            `
            : state.view === "results"
              ? `
                ${incidentsPanel(state.incidents)}
                ${incidentDetailPanel(selectedIncident, state.anomalies)}
                ${dataTable("Anomalies Candidates", filteredAnomalies, ["timestamp_iso", "severity", "event", "source", "host", "category", "anomaly_score", "message"], "◆", { alertActions: true, exportName: "anomalies_logminer.csv" })}
                ${dataTable("Événements Normalisés", filteredEvents, ["timestamp_iso", "severity", "event", "source", "host", "user", "category", "message"], "▤", { exportName: "evenements_logminer.csv" })}
              `
              : `
                ${servicePanel()}
                ${pipelineTopologyPanel()}
                ${realtimeChartsPanel(filteredEvents, filteredAnomalies, state.incidents)}
                ${resourcesPanel()}
                ${agentFlowPanel([...state.messages, ...state.redisMessages])}
                ${validationPanel(state.validation)}
                ${auditPanel(state.audit)}
              `
        }
      </main>
    </div>
  `;

  document.getElementById("reloadBtn")?.addEventListener("click", loadData);
  document.getElementById("browserNotifBtn")?.addEventListener("click", enableBrowserNotifications);
  document.getElementById("runtimeBtn")?.addEventListener("click", prepareRuntime);
  document.getElementById("mqttTestBtn")?.addEventListener("click", testMqttPublish);
  document.getElementById("openResultsBtn")?.addEventListener("click", () => setView("results"));
  document.getElementById("privilegedBtn")?.addEventListener("click", requestPrivilegedCollect);
  document.getElementById("discoverBtn")?.addEventListener("click", discoverLogs);
  document.getElementById("autoRunBtn")?.addEventListener("click", runAutonomousScan);
  document.getElementById("explainBtn")?.addEventListener("click", explainDashboard);
  document.getElementById("queryFilter")?.addEventListener("input", (event) => setFilter("query", event.target.value));
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", (event) => setView(event.target.dataset.view));
  });
  document.querySelectorAll("[data-filter]").forEach((select) => {
    select.addEventListener("change", (event) => setFilter(event.target.dataset.filter, event.target.value));
  });
  document.querySelectorAll("[data-incident-id]").forEach((button) => {
    button.addEventListener("click", (event) => selectIncident(event.currentTarget.dataset.incidentId));
  });
  document.querySelectorAll("[data-export]").forEach((button) => {
    button.addEventListener("click", (event) => {
      const filename = event.currentTarget.dataset.export;
      if (filename.includes("anomalies")) exportRows(filename, filteredAnomalies);
      else exportRows(filename, filteredEvents);
    });
  });
  document.getElementById("exportIncidentBtn")?.addEventListener("click", () => exportRows("incident_detail_logminer.csv", selectedIncident ? [selectedIncident] : []));
  document.querySelectorAll("[data-alert-action]").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const index = Number(event.currentTarget.dataset.alertIndex);
      const row = filteredAnomalies.slice(0, 100)[index] || {};
      const alertId = alertKey(row, `row-${index}`);
      await decideAlert(String(alertId), event.currentTarget.dataset.alertAction, row);
    });
  });
  const focusSelector = captureFocusSelector();
  if (focusSelector) {
    window.setTimeout(() => document.querySelector(focusSelector)?.scrollIntoView({ block: "start" }), 250);
  }
  updateRefreshClock();
}

render();
startRefreshClock();
loadData({ mode: "initial" });
