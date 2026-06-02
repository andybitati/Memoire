const DATA_LIMIT = 8000;
const AUTO_REFRESH_MS = 5 * 1000;

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
  services: { api: {}, redis: {}, models: [] },
  resources: {},
  collector: { loading: false, error: "", selected: null, candidates: [] },
  privilege: { loading: false, error: "", result: null },
  runtime: { loading: false, error: "", result: null },
  autoRun: { loading: false, error: "", result: null },
  explanation: { loading: false, provider: "", text: "", error: "" },
  meta: {},
  filters: { query: "", host: "", severity: "", category: "", source: "" },
  view: "overview",
  selectedIncidentId: "",
  alertDecisions: {},
  decisionAnimations: {},
  recentDecision: null,
  browserNotifications: false,
  lastRefreshAt: "",
  nextRefreshAt: "",
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
    timestamp_iso: row.timestamp_iso || row["_source.@timestamp"] || row.timestamp || "",
    severity: row.severity || row["_source.rule.level"] || "",
    event: row.event || row["_source.rule.description"] || row["_source.decoder.name"] || "",
    source: row.source || row["_source.location"] || row["_source.decoder.name"] || "",
    host: row.host || row["_source.agent.name"] || row["_source.predecoder.hostname"] || "",
    user: row.user || row["_source.data.dstuser"] || "",
    category: row.category || row["_source.rule.groups"] || row["_source.rule.mitre.tactic"] || "",
    message: row.message || row["_source.full_log"] || row["_source.rule.description"] || "",
  }));
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
  state = { ...state, view };
  render();
}

function selectIncident(incidentId) {
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

function dashboardSnapshot() {
  const anomalyCount = state.anomalies.filter((row) => row.is_anomaly === "1").length;
  const criticalIncidents = state.incidents.filter((row) => ["CRITICAL", "ERROR"].includes(row.severity)).length;
  const incidents = [...state.incidents].sort((a, b) => Number(b.event_count || 0) - Number(a.event_count || 0));

  // On envoie un resume compact au serveur pour limiter le cout LLM et eviter
  // d'exposer inutilement des logs bruts tres volumineux dans la requete.
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
        <img class="brandLogo" src="/ariel_logminer_mark.png" alt="Ariel Logminer" />
        <div><strong>Ariel Logminer</strong><span>Agents IA</span></div>
      </div>
      <button class="primaryAction" id="reloadBtn" ${state.loading ? "disabled" : ""}><span class="icon">↻</span>Actualiser</button>
      <button class="secondaryAction fullWidth" id="browserNotifBtn"><span class="icon">!</span>${state.browserNotifications ? "Notifications actives" : "Activer notifications"}</button>
      <button class="secondaryAction fullWidth" id="runtimeBtn" ${state.runtime.loading ? "disabled" : ""}><span class="icon">◉</span>${state.runtime.loading ? "Préparation" : "Préparer runtime"}</button>
      <button class="secondaryAction fullWidth" id="privilegedBtn" ${state.privilege.loading ? "disabled" : ""}><span class="icon">⌘</span>${state.privilege.loading ? "Demande" : "Autoriser journaux sensibles"}</button>
      <button class="secondaryAction fullWidth" id="discoverBtn" ${state.collector.loading ? "disabled" : ""}><span class="icon">⌕</span>${state.collector.loading ? "Recherche" : "Trouver les journaux"}</button>
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
    <div class="healthItem">
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

function percentBar(label, value, detail, tone = "") {
  const safeValue = Number.isFinite(Number(value)) ? Math.max(0, Math.min(100, Number(value))) : 0;
  return `
    <div class="resourceMetric ${tone}">
      <div><strong>${escapeHtml(label)}</strong><span>${escapeHtml(detail || "")}</span></div>
      <div class="meter"><span style="width:${safeValue}%"></span></div>
      <small>${Number.isFinite(Number(value)) ? `${safeValue.toFixed(1)}%` : "n/a"}</small>
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

function eventDate(row) {
  const date = new Date(row.timestamp_iso || row.start_time || row.end_time || "");
  return Number.isNaN(date.getTime()) ? null : date;
}

function temporalBuckets(rows) {
  const ordered = rows
    .map((row) => eventDate(row))
    .filter(Boolean)
    .sort((a, b) => a.getTime() - b.getTime());
  const map = new Map();
  ordered.forEach((date) => {
    const key = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}-${String(date.getUTCDate()).padStart(2, "0")} ${String(
      date.getUTCHours(),
    ).padStart(2, "0")}h`;
    map.set(key, (map.get(key) || 0) + 1);
  });
  return Array.from(map.entries()).slice(-24);
}

function temporalAnalysisModule(rows) {
  const buckets = temporalBuckets(rows);
  const max = Math.max(...buckets.map(([, count]) => count), 1);
  const latestLabel = buckets.length ? buckets[buckets.length - 1][0] : "Aucune donnée";
  const peak = buckets.reduce((best, item) => (item[1] > best[1] ? item : best), ["", 0]);

  return `
    <div class="temporalModule">
      <div class="temporalHeader">
        <span class="eyebrow">Analyse temporelle</span>
        <strong>Timeline & heatmap</strong>
        <small>${escapeHtml(latestLabel)} · pic ${escapeHtml(String(peak[1] || 0))}</small>
      </div>
      <div class="miniTimeline">
        ${
          buckets.length
            ? buckets
                .map(
                  ([label, count]) => `
                    <div class="miniBarColumn" title="${escapeHtml(label)}: ${count}">
                      <div class="miniBar" style="height:${Math.max(8, (count / max) * 100)}%"></div>
                    </div>
                  `,
                )
                .join("")
            : `<div class="emptyState">Aucun timestamp exploitable.</div>`
        }
      </div>
      <div class="heatmapGrid">
        ${
          buckets.length
            ? buckets
                .map(([label, count]) => {
                  const level = Math.ceil((count / max) * 5);
                  return `<span class="heatCell heat${level}" title="${escapeHtml(label)}: ${count}"></span>`;
                })
                .join("")
            : ""
        }
      </div>
      <div class="temporalLegend">
        <span>Faible</span>
        <span>Activité horaire</span>
        <span>Forte</span>
      </div>
    </div>
  `;
}

function servicePanel() {
  const { api, redis, models } = state.services;
  const runtime = state.runtime.result || state.services.runtime || {};
  const modelCount = (models || []).filter((model) => model.exists).length;
  const selected = state.collector.selected;
  const result = state.autoRun.result;
  const privilege = state.privilege.result;

  return `
    <section class="panel servicePanel">
      <div class="panelHeader">
        <div><h2>Services V2</h2><p>${escapeHtml(state.services.apiBase || "FastAPI locale")}</p></div>
        <span class="icon">◎</span>
      </div>
      <div class="serviceGrid">
        <div class="serviceItem"><span class="dot ${api?.status === "ok" ? "" : "errorDot"}"></span><div><strong>FastAPI</strong><small>${escapeHtml(api?.status || "inconnu")}</small></div></div>
        <div class="serviceItem"><span class="dot ${redis?.status === "ok" ? "" : "errorDot"}"></span><div><strong>Redis Streams</strong><small>${escapeHtml(redis?.stream || redis?.error || "non vérifié")}</small></div></div>
        <div class="serviceItem"><span class="dot ${runtime?.docker_engine ? "" : "errorDot"}"></span><div><strong>Docker</strong><small>${escapeHtml(runtime?.message || "état non vérifié")}</small></div></div>
        <div class="serviceItem"><span class="dot"></span><div><strong>Modèles</strong><small>${modelCount}/${(models || []).length} artefacts disponibles</small></div></div>
      </div>
      <div class="collectorBox">
        <strong>Collecteur autonome</strong>
        <span>${selected ? escapeHtml(selected.path) : "Aucun fichier sélectionné par le collecteur."}</span>
        ${result ? `<small>Dernier run: ${escapeHtml(result.run_id)} · ${escapeHtml(result.anomalies_rows ?? "0")} anomalies · ${escapeHtml(result.incidents_rows ?? "0")} incidents</small>` : ""}
        ${privilege ? `<small>Accès sensible: ${escapeHtml(privilege.message || (privilege.launched ? "demande lancée" : "non autorisé"))}</small>` : ""}
        ${privilege?.launcher_path ? `<small>Lanceur admin: ${escapeHtml(privilege.launcher_path)}</small>` : ""}
        ${state.collector.error || state.autoRun.error || state.runtime.error || state.privilege.error ? `<small class="inlineError">${escapeHtml(state.collector.error || state.autoRun.error || state.runtime.error || state.privilege.error)}</small>` : ""}
      </div>
    </section>
  `;
}

function operatorSummaryPanel() {
  const redisOk = state.services.redis?.status === "ok";
  const apiOk = state.services.api?.status === "ok";
  const latestAudit = state.audit[state.audit.length - 1];
  const result = state.autoRun.result;
  const selected = state.collector.selected;
  const nextAction = result
    ? "Consulter les résultats ou demander une explication analyste."
    : selected
      ? "Lancer l'analyse pour traiter les journaux trouvés."
      : "Trouver les journaux puis lancer l'analyse.";

  return `
    <section class="starkHero">
      ${temporalAnalysisModule(state.events.length ? state.events : state.anomalies)}
      <div class="missionBrief">
        <span class="eyebrow">Poste de pilotage</span>
        <h2>Que dois-je faire maintenant ?</h2>
        <p>${escapeHtml(nextAction)}</p>
        <div class="hudMiniGrid">
          ${hudRing("API", apiOk ? "ON" : "OFF", apiOk ? "Disponible" : "À vérifier", apiOk ? "ok" : "warn")}
          ${hudRing("REDIS", redisOk ? "ON" : "OFF", redisOk ? "Bus actif" : "Bus absent", redisOk ? "ok" : "warn")}
          ${hudRing("AUDIT", latestAudit ? "LOG" : "---", latestAudit ? latestAudit.action : "Aucune action", latestAudit ? "ok" : "idle")}
        </div>
      </div>
      <div class="healthGrid">
        ${statusBadge("API", apiOk, apiOk ? "Disponible" : state.services.api?.error)}
        ${statusBadge("Bus Redis", redisOk, redisOk ? "Messages agents actifs" : state.services.redis?.error)}
        ${statusBadge("Audit", Boolean(latestAudit), latestAudit ? latestAudit.action : "Aucune action enregistrée")}
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
        <span class="eyebrow">Attention administrateur</span>
        <h2>${escapeHtml(alerts.length)} signal${alerts.length > 1 ? "aux" : ""} à vérifier en priorité</h2>
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
      <button class="warningAction" id="openResultsBtn">Voir les résultats</button>
    </section>
  `;
}

function resourcesPanel() {
  const resources = state.resources || {};
  const agents = resources.agents || [];
  return `
    <section class="panel resourcesPanel hudPanel">
      <div class="panelHeader">
        <div><h2>Consommation par agent</h2><p>${escapeHtml(resources.message || "Mesure agents Ariel Logminer")}</p></div>
        <span class="icon">◷</span>
      </div>
      ${
        resources.available
          ? agents.length
            ? `<div class="agentResources">
                ${agents
                  .map(
                    (agent) => `
                      <article class="agentResource">
                        <div>
                          <strong>${escapeHtml(agent.agent || "Agent Ariel Logminer")}</strong>
                          <span>${escapeHtml(agent.role || "processus agent")}</span>
                          <small>PID ${escapeHtml(agent.pids || agent.pid || "")} · ${escapeHtml(agent.status || "unknown")}</small>
                        </div>
                        <div class="agentResourceMetrics">
                          <span><b>${escapeHtml(agent.cpu_percent ?? 0)}</b>% CPU</span>
                          <span><b>${escapeHtml(agent.memory_mb ?? 0)}</b> MB RAM</span>
                        </div>
                      </article>
                    `,
                  )
                  .join("")}
              </div>`
            : `<div class="emptyState">Aucun processus agent Ariel Logminer detecte pour le moment.</div>`
          : `<div class="emptyState">${escapeHtml(resources.message || "Mesure des ressources indisponible.")}</div>`
      }
    </section>
  `;
}

function workflowPanel() {
  const runtime = state.runtime.result || state.services.runtime || {};
  const selected = state.collector.selected;
  const result = state.autoRun.result;
  const privilege = state.privilege.result;
  const redisOk = state.services.redis?.status === "ok";

  const steps = [
    {
      title: "Infrastructure",
      status: redisOk ? "Prêt" : runtime?.docker_engine ? "Docker prêt" : "À vérifier",
      detail: redisOk ? "Redis répond pour le bus agents." : runtime?.message || "Docker/Redis non confirmés.",
      tone: redisOk || runtime?.docker_engine ? "okStep" : "warnStep",
    },
    {
      title: "Accès sensible",
      status: privilege?.launched ? "Demande lancée" : "Optionnel",
      detail: privilege?.message || "Seulement nécessaire pour Security.evtx ou journaux protégés.",
      tone: privilege?.launched ? "okStep" : "idleStep",
    },
    {
      title: "Journaux",
      status: selected ? "Trouvés" : "En attente",
      detail: selected ? selected.path : "Le collecteur choisira une source locale accessible.",
      tone: selected ? "okStep" : "idleStep",
    },
    {
      title: "Analyse",
      status: result ? "Terminée" : "Prête",
      detail: result
        ? `${result.input_rows || 0} lignes examinées, ${result.anomalies_rows || 0} résultats scorés, ${result.timings?.workflow_sec || "n/a"} s.`
        : "Le bouton Lancer l'analyse lance collecte, routage et détection.",
      tone: result ? "okStep" : "idleStep",
    },
  ];

  return `
    <section class="panel workflowPanel hudPanel">
      <div class="panelHeader"><h2>Parcours d'analyse</h2><span class="icon">▶</span></div>
      <div class="workflowGrid">
        ${steps
          .map(
            (step, index) => `
              <article class="workflowStep ${step.tone}">
                <span class="stepNumber">${index + 1}</span>
                <div>
                  <strong>${escapeHtml(step.title)}</strong>
                  <span>${escapeHtml(step.status)}</span>
                  <small>${escapeHtml(step.detail)}</small>
                </div>
              </article>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function quickFindingsPanel() {
  const rows = pendingAnomalies(state.anomalies).filter((row) => row.is_anomaly === "1").slice(0, 5);
  return `
    <section class="panel hudPanel">
      <div class="panelHeader"><h2>Signaux à regarder</h2><span class="icon">◆</span></div>
      ${
        rows.length
          ? `<div class="signalList">
              ${rows
                .map(
                  (row) => `
                    <article class="signalItem">
                      <div>
                        <strong>${escapeHtml(row.event || row.category || "Signal détecté")}</strong>
                        <span>${escapeHtml(row.message || row.source || "")}</span>
                      </div>
                      <span class="pill ${severityClass(row.severity)}">${escapeHtml(row.severity || "N/A")}</span>
                    </article>
                  `,
                )
                .join("")}
            </div>`
          : `<div class="emptyState">Aucun signal prioritaire dans les résultats chargés.</div>`
      }
    </section>
  `;
}

function decisionFeedbackPanel() {
  if (!state.recentDecision) return "";
  const { alertId, decision, status, row } = state.recentDecision;
  return `
    <section class="panel decisionFeedback ${status.includes("non enregistrée") ? "decisionError" : ""}">
      <div>
        <strong>${escapeHtml(decisionActionLabel(decision))}: ${escapeHtml(String(alertId).slice(0, 56))}</strong>
        <span>${escapeHtml(status)}</span>
        <small>${escapeHtml(row.event || row.category || row.message || "Anomalie candidate")}</small>
      </div>
      <span class="decisionPulse"></span>
    </section>
  `;
}

function auditPanel(rows) {
  return `
    <section class="panel messages">
      <div class="panelHeader"><h2>Journal d'audit système</h2><span class="icon">▤</span></div>
      ${rows
        .slice(-16)
        .reverse()
        .map(
          (entry) => {
            const details = entry.details || {};
            const detailText = [details.category, details.severity, details.reason].filter(Boolean).join(" · ");
            return `
            <div class="auditRow ${String(entry.action || "").startsWith("alert.") ? "auditDecision" : ""}">
              <div>
                <strong>${escapeHtml(entry.action)}</strong>
                <span>${escapeHtml(entry.target || "système")}</span>
                ${detailText ? `<small>${escapeHtml(detailText)}</small>` : ""}
              </div>
              <small>${escapeHtml(entry.status || "ok")}</small>
            </div>
          `;
          },
        )
        .join("") || `<div class="emptyState">Aucune action auditée pour le moment.</div>`}
    </section>
  `;
}

function agentFlowPanel(messages) {
  const runId = latestRun(messages);
  const rows = runId ? messages.filter((message) => message.run_id === runId) : messages;
  const ordered = rows.slice(-12);

  return `
    <section class="panel agentFlow">
      <div class="panelHeader">
        <div><h2>Flux agents</h2><p>${runId ? `Run ${escapeHtml(runId.slice(0, 10))}` : "Aucun run actif"}</p></div>
        <span class="icon">↬</span>
      </div>
      ${
        ordered.length
          ? `<ol class="flowSteps">
              ${ordered
                .map(
                  (message) => `
                    <li class="${message.status === "error" ? "flowError" : ""}">
                      <span class="stepDot"></span>
                      <div>
                        <strong>${escapeHtml(messageTitle(message))}</strong>
                        <span>${escapeHtml(agentName(message.source))} → ${escapeHtml(agentName(message.target))}</span>
                        <small>${escapeHtml(formatDateTime(message.timestamp))}${payloadSummary(message.payload) ? ` · ${escapeHtml(payloadSummary(message.payload))}` : ""}</small>
                      </div>
                    </li>
                  `,
                )
                .join("")}
            </ol>`
          : `<div class="emptyState">Aucun message agent disponible pour le moment.</div>`
      }
    </section>
  `;
}

function validationPanel(rows) {
  return `
    <section class="panel validationPanel">
      <div class="panelHeader"><h2>Validation modèles</h2><span class="icon">✓</span></div>
      ${
        rows.length
          ? rows
              .slice(0, 6)
              .map(
                (row) => `
                  <article class="validationItem">
                    <div>
                      <strong>${escapeHtml(String(row.dataset || "").toUpperCase())} · ${escapeHtml(row.model)}</strong>
                      <span>F1 ${escapeHtml(row.f1)} · Recall ${escapeHtml(row.recall)} · Precision ${escapeHtml(row.precision)}</span>
                    </div>
                    <span class="pill info">${escapeHtml(row.events || "0")} lignes</span>
                  </article>
                `,
              )
              .join("")
          : `<div class="emptyState">Aucune synthèse de validation trouvée.</div>`
      }
    </section>
  `;
}

function explanationPanel() {
  const { loading, provider, text, error } = state.explanation;
  const providerLabel = provider === "openai" ? "LLM OpenAI" : provider === "local" ? "Explication locale" : "Pret";

  return `
    <section class="panel explanationPanel">
      <div class="panelHeader">
        <div><h2>Explication analyste</h2><p>${escapeHtml(providerLabel)}</p></div>
        <button class="secondaryAction" id="explainBtn" ${loading || state.loading ? "disabled" : ""}>
          <span class="icon">${loading ? "…" : "✦"}</span>${loading ? "Analyse en cours" : "Expliquer les resultats"}
        </button>
      </div>
      ${
        text
          ? `<div class="explanationText">${escapeHtml(text)}</div>`
          : `<div class="emptyState">Cliquez pour transformer les scores, incidents et messages agents en synthese lisible.</div>`
      }
      ${error ? `<div class="explanationWarning">${escapeHtml(error)}</div>` : ""}
    </section>
  `;
}

function timeline(rows) {
  const map = new Map();
  rows.forEach((row) => {
    const date = new Date(row.timestamp_iso || row.start_time);
    if (Number.isNaN(date.getTime())) return;
    const key = `${String(date.getUTCDate()).padStart(2, "0")} ${String(date.getUTCHours()).padStart(2, "0")}h`;
    map.set(key, (map.get(key) || 0) + 1);
  });
  const buckets = Array.from(map.entries()).slice(-36);
  const max = Math.max(...buckets.map(([, count]) => count), 1);

  return `
    <section class="panel timeline">
      <div class="panelHeader"><h2>Activité temporelle</h2><span class="icon">◷</span></div>
      <div class="bars">
        ${buckets
          .map(
            ([label, count]) => `
              <div class="barColumn" title="${escapeHtml(label)}: ${count}">
                <div class="bar" style="height:${Math.max(6, (count / max) * 100)}%"></div>
                <span>${escapeHtml(label.slice(-3))}</span>
              </div>
            `,
          )
          .join("")}
      </div>
    </section>
  `;
}

function incidentsPanel(rows) {
  const sorted = [...rows].sort((a, b) => Number(b.event_count || 0) - Number(a.event_count || 0));
  return `
    <section class="panel hudPanel">
      <div class="panelHeader"><h2>Incidents corrélés</h2><span class="icon">⇄</span></div>
      <div class="incidentList">
        ${sorted
          .slice(0, 8)
          .map(
            (incident) => `
              <article class="incident">
                <div>
                  <strong>${escapeHtml(incident.incident_id)}</strong>
                  <span>${escapeHtml(incident.summary)}</span>
                  <small>${escapeHtml(formatDateTime(incident.start_time))} → ${escapeHtml(formatDateTime(incident.end_time))}</small>
                </div>
                <div class="incidentMeta">
                  <span class="pill ${severityClass(incident.severity)}">${escapeHtml(incident.severity || "N/A")}</span>
                  <span>${escapeHtml(incident.event_count)} evt</span>
                  <small>${escapeHtml(incident.category || "catégorie inconnue")}</small>
                  <button class="miniAction" data-incident-id="${escapeHtml(incident.incident_id || "")}">Détail</button>
                </div>
              </article>
            `,
          )
          .join("") || `<div class="emptyState">Aucun incident corrélé.</div>`}
      </div>
    </section>
  `;
}

function incidentDetailPanel(incident, anomalies) {
  if (!incident) {
    return `
      <section class="panel detailPanel">
        <div class="panelHeader"><h2>Détail incident</h2><span class="icon">◎</span></div>
        <div class="emptyState">Sélectionnez un incident pour voir sa fenêtre, sa justification et les anomalies sources probables.</div>
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
      const sameSource = !incident.source || !row.source || row.source === incident.source;
      const sameEvent = !eventIds.size || eventIds.has(String(row.event || ""));
      return inWindow && sameHost && sameSource && sameEvent;
    })
    .slice(0, 12);

  return `
    <section class="panel detailPanel">
      <div class="panelHeader">
        <div><h2>Détail incident ${escapeHtml(incident.incident_id || "")}</h2><p>${escapeHtml(incident.summary || "Incident corrélé")}</p></div>
        <button class="secondaryAction" id="exportIncidentBtn"><span class="icon">⇩</span>Exporter détail</button>
      </div>
      <div class="detailGrid">
        <div><strong>Fenêtre</strong><span>${escapeHtml(formatDateTime(incident.start_time))} → ${escapeHtml(formatDateTime(incident.end_time))}</span></div>
        <div><strong>Contexte</strong><span>${escapeHtml(incident.host || "host inconnu")} · ${escapeHtml(incident.source || "source inconnue")}</span></div>
        <div><strong>Priorité</strong><span>${escapeHtml(incident.priority || incident.severity || "N/A")} · ${escapeHtml(incident.priority_score || "")}</span></div>
        <div><strong>Événements</strong><span>${escapeHtml(incident.events || "n/a")}</span></div>
      </div>
      <div class="rationaleBox">${escapeHtml(incident.rationale || "Aucune justification détaillée disponible pour ce fichier d'incidents.")}</div>
      <div class="detailList">
        ${
          related.length
            ? related
                .map(
                  (row) => `
                    <article>
                      <strong>${escapeHtml(row.event || row.category || "Anomalie")}</strong>
                      <span>${escapeHtml(formatDateTime(row.timestamp_iso))} · ${escapeHtml(row.host || "")} · ${escapeHtml(row.source || "")}</span>
                      <small>${escapeHtml(row.message || "")}</small>
                    </article>
                  `,
                )
                .join("")
            : `<div class="emptyState">Aucune anomalie source retrouvee par correspondance temporelle stricte.</div>`
        }
      </div>
    </section>
  `;
}

function dataTable(title, rows, columns, icon, options = {}) {
  const actionRows = options.alertActions ? rows.slice(0, 120) : [];
  return `
    <section class="panel tablePanel">
      <div class="panelHeader">
        <h2>${escapeHtml(title)}</h2>
        <div class="panelActions">
          ${options.exportName ? `<button class="secondaryAction" data-export="${escapeHtml(options.exportName)}"><span class="icon">⇩</span>Exporter</button>` : ""}
          <span class="icon">${icon}</span>
        </div>
      </div>
      <div class="tableWrap">
        <table>
          <thead><tr>${options.alertActions ? `<th class="decisionColumn">Décision</th>` : ""}${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead>
          <tbody>
            ${rows
              .slice(0, 120)
              .map((row, index) => {
                const alertId = alertKey(row, `row-${index}`);
                const animation = state.decisionAnimations[alertId] || {};
                actionRows[index] = row;
                return `
                  <tr class="${animation.status === "saving" ? "decisionSaving" : ""} ${animation.status === "done" ? "decisionDone" : ""}">
                    ${
                      options.alertActions
                        ? `<td class="decisionColumn">
                            <div class="decisionActions">
                              <button class="acceptDecision" data-alert-action="accept" data-alert-index="${index}" ${animation.status ? "disabled" : ""} title="Valider l'alerte">Valider</button>
                              <button class="rejectDecision" data-alert-action="reject" data-alert-index="${index}" ${animation.status ? "disabled" : ""} title="Rejeter l'alerte">Rejeter</button>
                              <button class="reclassifyDecision" data-alert-action="reclassify" data-alert-index="${index}" ${animation.status ? "disabled" : ""} title="Reclasser l'alerte">Reclasser</button>
                            </div>
                            <small>${escapeHtml(animation.status === "saving" ? "audit..." : animation.status === "done" ? decisionLabel(animation.decision) : String(alertId).slice(0, 24))}</small>
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

function messagesPanel(rows) {
  return `
    <section class="panel messages">
      <div class="panelHeader"><h2>Journal agents</h2><span class="icon">▤</span></div>
      ${rows
        .slice(-8)
        .map(
          (message) => `
            <div class="message">
              <span>${escapeHtml(messageTitle(message))}</span>
              <strong>${escapeHtml(agentName(message.source))} → ${escapeHtml(agentName(message.target))}</strong>
              <small>${escapeHtml(message.status || "ok")}</small>
            </div>
          `,
        )
        .join("") || `<div class="emptyState">Aucun message brut à afficher.</div>`}
    </section>
  `;
}

function redisPanel(rows) {
  return `
    <section class="panel messages">
      <div class="panelHeader"><h2>Redis events</h2><span class="icon">↬</span></div>
      ${rows
        .slice(-10)
        .map(
          (message) => `
            <div class="message">
              <span>${escapeHtml(messageTitle(message))}</span>
              <strong>${escapeHtml(agentName(message.source))} → ${escapeHtml(agentName(message.target))}</strong>
              <small>${escapeHtml(message.status || "ok")}</small>
            </div>
          `,
        )
        .join("") || `<div class="emptyState">Aucun événement Redis à afficher.</div>`}
    </section>
  `;
}

function render() {
  const filteredEvents = filterRows(state.events);
  const pending = pendingAnomalies(state.anomalies);
  const filteredAnomalies = filterRows(pending);
  const anomalyCount = pending.filter((row) => row.is_anomaly === "1").length;
  const criticalIncidents = state.incidents.filter((row) => ["CRITICAL", "ERROR"].includes(row.severity)).length;
  const alerts = urgentAlerts();
  const selectedIncident = state.incidents.find((incident) => incident.incident_id === state.selectedIncidentId) || state.incidents[0] || null;
  document.title = alerts.length ? `(${alerts.length}) Alertes Ariel Logminer` : "Ariel Logminer";
  maybeNotify(alerts);

  root.innerHTML = `
    <div class="app">
      ${sidebar()}
      <main class="content">
        <header class="topbar">
          <div><span>Surveillance multi-agents</span><h1>Centre d’analyse Ariel Logminer</h1></div>
          <div class="statusCluster">
            <div class="status"><span class="${state.error ? "dot errorDot" : "dot"}"></span>${escapeHtml(state.error || (state.loading ? "Synchronisation" : "Données synchronisées"))}</div>
            <div class="refreshHud ${state.loading ? "isRefreshing" : ""} ${state.autoRun.loading ? "isAnalyzing" : ""}">
              <span class="refreshSweep"></span>
              <strong>${state.autoRun.loading ? "Analyse en cours" : "Analyse temps réel"}</strong>
              <span><b id="nextRefreshClock">${escapeHtml(remainingRefreshLabel())}</b> · dernier <b id="lastRefreshClock">${escapeHtml(state.lastRefreshAt ? formatTime(state.lastRefreshAt) : "--:--")}</b></span>
              <small>Analyse ${state.lastAutoAnalysisAt ? `à ${escapeHtml(formatTime(state.lastAutoAnalysisAt))}` : "en attente"}</small>
            </div>
          </div>
        </header>
        ${warningNotificationPanel(alerts)}
        ${decisionFeedbackPanel()}
        <div class="statsGrid">
          ${stat("▣", "Événements", state.meta.events || state.events.length, "blue")}
          ${stat("⚠", "Anomalies", anomalyCount, "amber")}
          ${stat("⇄", "Incidents", state.incidents.length, "green")}
          ${stat("!", "Incidents critiques", criticalIncidents, "rose")}
        </div>
        ${
          state.view === "overview"
            ? `
              ${operatorSummaryPanel()}
              ${workflowPanel()}
              ${resourcesPanel()}
              <div class="mainGrid compactMain">
                ${quickFindingsPanel()}
                <div class="sideStack">
                  ${incidentsPanel(state.incidents)}
                  ${agentFlowPanel([...state.messages, ...state.redisMessages])}
                </div>
              </div>
              ${explanationPanel()}
            `
            : state.view === "results"
              ? `
                ${incidentsPanel(state.incidents)}
                ${incidentDetailPanel(selectedIncident, state.anomalies)}
                ${dataTable("Anomalies candidates", filteredAnomalies, ["timestamp_iso", "severity", "event", "source", "host", "category", "anomaly_score", "message"], "◆", { alertActions: true, exportName: "anomalies_logminer.csv" })}
                ${dataTable("Événements normalisés", filteredEvents, ["timestamp_iso", "severity", "event", "source", "host", "user", "category", "message"], "▤", { exportName: "evenements_logminer.csv" })}
              `
              : `
                ${servicePanel()}
                ${resourcesPanel()}
                <div class="mainGrid">
                  ${timeline(filteredEvents)}
                  <div class="sideStack">
                    ${agentFlowPanel([...state.messages, ...state.redisMessages])}
                    ${validationPanel(state.validation)}
                  </div>
                </div>
                ${redisPanel(state.redisMessages)}
                ${auditPanel(state.audit)}
                ${messagesPanel(state.messages)}
              `
        }
      </main>
    </div>
  `;

  document.getElementById("reloadBtn")?.addEventListener("click", loadData);
  document.getElementById("browserNotifBtn")?.addEventListener("click", enableBrowserNotifications);
  document.getElementById("runtimeBtn")?.addEventListener("click", prepareRuntime);
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
      const row = filteredAnomalies.slice(0, 120)[index] || {};
      const alertId = alertKey(row, `row-${index}`);
      await decideAlert(String(alertId), event.currentTarget.dataset.alertAction, row);
    });
  });
  updateRefreshClock();
}

render();
startRefreshClock();
loadData({ mode: "initial" });
