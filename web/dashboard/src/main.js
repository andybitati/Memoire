const DATA_LIMIT = 8000;
let state = {
  loading: true,
  error: "",
  events: [],
  anomalies: [],
  incidents: [],
  messages: [],
  redisMessages: [],
  validation: [],
  services: { api: {}, redis: {}, models: [] },
  collector: { loading: false, error: "", selected: null, candidates: [] },
  privilege: { loading: false, error: "", result: null },
  runtime: { loading: false, error: "", result: null },
  autoRun: { loading: false, error: "", result: null },
  explanation: { loading: false, provider: "", text: "", error: "" },
  meta: {},
  filters: { query: "", host: "", severity: "", category: "", source: "" },
};

const root = document.getElementById("root");

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

async function loadData() {
  state = { ...state, loading: true, error: "", explanation: { loading: false, provider: "", text: "", error: "" } };
  render();
  try {
    const [events, anomalies, incidents, messages, services, redisEvents] = await Promise.all([
      fetchData("events"),
      fetchData("anomalies"),
      fetchData("incidents", 2000),
      fetchOptionalData("messages", 200),
      fetchJson("/api/services"),
      fetchJson("/api/redis-events?count=100"),
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
      validation: validation.data,
      services,
      meta: {
        events: events.count,
        anomalies: anomalies.count,
        incidents: incidents.count,
        messages: messages.count,
        redisMessages: redisEvents.count,
        validation: validation.count,
      },
    };
  } catch (error) {
    state = { ...state, loading: false, error: error.message };
  }
  render();
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

async function runAutonomousScan() {
  state = { ...state, autoRun: { loading: true, error: "", result: null } };
  render();
  try {
    const result = await fetchJson("/api/auto-run", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    state = { ...state, autoRun: { loading: false, error: "", result } };
    await loadData();
    state = { ...state, autoRun: { loading: false, error: "", result } };
  } catch (error) {
    state = { ...state, autoRun: { loading: false, error: error.message, result: null } };
  }
  render();
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
      <div class="brand"><span class="icon">◈</span><div><strong>Logminer</strong><span>Agents IA</span></div></div>
      <button class="primaryAction" id="reloadBtn" ${state.loading ? "disabled" : ""}><span class="icon">↻</span>Actualiser</button>
      <button class="secondaryAction fullWidth" id="runtimeBtn" ${state.runtime.loading ? "disabled" : ""}><span class="icon">◉</span>${state.runtime.loading ? "Préparation" : "Préparer runtime"}</button>
      <button class="secondaryAction fullWidth" id="privilegedBtn" ${state.privilege.loading ? "disabled" : ""}><span class="icon">⌘</span>${state.privilege.loading ? "Demande" : "Autoriser journaux sensibles"}</button>
      <button class="secondaryAction fullWidth" id="discoverBtn" ${state.collector.loading ? "disabled" : ""}><span class="icon">⌕</span>${state.collector.loading ? "Scan" : "Chercher logs"}</button>
      <button class="secondaryAction fullWidth" id="autoRunBtn" ${state.autoRun.loading ? "disabled" : ""}><span class="icon">▶</span>${state.autoRun.loading ? "Analyse" : "Analyse autonome"}</button>
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
        ${state.collector.error || state.autoRun.error || state.runtime.error || state.privilege.error ? `<small class="inlineError">${escapeHtml(state.collector.error || state.autoRun.error || state.runtime.error || state.privilege.error)}</small>` : ""}
      </div>
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
    <section class="panel">
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
                </div>
              </article>
            `,
          )
          .join("") || `<div class="emptyState">Aucun incident corrélé.</div>`}
      </div>
    </section>
  `;
}

function dataTable(title, rows, columns, icon) {
  return `
    <section class="panel tablePanel">
      <div class="panelHeader"><h2>${escapeHtml(title)}</h2><span class="icon">${icon}</span></div>
      <div class="tableWrap">
        <table>
          <thead><tr>${columns.map((column) => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead>
          <tbody>
            ${rows
              .slice(0, 120)
              .map(
                (row) => `
                  <tr>
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
                `,
              )
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
  const filteredAnomalies = filterRows(state.anomalies);
  const anomalyCount = state.anomalies.filter((row) => row.is_anomaly === "1").length;
  const criticalIncidents = state.incidents.filter((row) => ["CRITICAL", "ERROR"].includes(row.severity)).length;

  root.innerHTML = `
    <div class="app">
      ${sidebar()}
      <main class="content">
        <header class="topbar">
          <div><span>Surveillance multi-agents</span><h1>Centre d’analyse Logminer</h1></div>
          <div class="status"><span class="${state.error ? "dot errorDot" : "dot"}"></span>${escapeHtml(state.error || (state.loading ? "Chargement" : "Données synchronisées"))}</div>
        </header>
        <div class="statsGrid">
          ${stat("▣", "Événements", state.meta.events || state.events.length, "blue")}
          ${stat("⚠", "Anomalies", anomalyCount, "amber")}
          ${stat("⇄", "Incidents", state.incidents.length, "green")}
          ${stat("!", "Incidents critiques", criticalIncidents, "rose")}
        </div>
        ${servicePanel()}
        ${explanationPanel()}
        <div class="mainGrid">
          ${timeline(filteredEvents)}
          <div class="sideStack">
            ${agentFlowPanel([...state.messages, ...state.redisMessages])}
            ${validationPanel(state.validation)}
          </div>
        </div>
        ${incidentsPanel(state.incidents)}
        ${dataTable("Anomalies candidates", filteredAnomalies, ["timestamp_iso", "severity", "event", "source", "host", "category", "anomaly_score", "message"], "◆")}
        ${dataTable("Événements normalisés", filteredEvents, ["timestamp_iso", "severity", "event", "source", "host", "user", "category", "message"], "▤")}
        ${redisPanel(state.redisMessages)}
        ${messagesPanel(state.messages)}
      </main>
    </div>
  `;

  document.getElementById("reloadBtn")?.addEventListener("click", loadData);
  document.getElementById("runtimeBtn")?.addEventListener("click", prepareRuntime);
  document.getElementById("privilegedBtn")?.addEventListener("click", requestPrivilegedCollect);
  document.getElementById("discoverBtn")?.addEventListener("click", discoverLogs);
  document.getElementById("autoRunBtn")?.addEventListener("click", runAutonomousScan);
  document.getElementById("explainBtn")?.addEventListener("click", explainDashboard);
  document.getElementById("queryFilter")?.addEventListener("input", (event) => setFilter("query", event.target.value));
  document.querySelectorAll("[data-filter]").forEach((select) => {
    select.addEventListener("change", (event) => setFilter(event.target.dataset.filter, event.target.value));
  });
}

render();
loadData();
