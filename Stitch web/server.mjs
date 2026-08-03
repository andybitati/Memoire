import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const processedDir = path.join(root, "data", "processed");
const picturesDir = path.join(root, "web", "pictures");
const preferredPort = Number(process.env.PORT || 5173);
const fastApiBase = process.env.LOGMINER_API_URL || "http://127.0.0.1:8000";
let activePort = preferredPort;

const dataFiles = {
  events: ["windows_copies_pipeline.csv"],
  anomalies: ["anomalies.csv"],
  incidents: ["incidents.csv"],
  messages: [
    "agent_messages.jsonl",
    "agent_messages_full_test.jsonl",
    "full_orchestrator_messages_test.jsonl",
    "agent_messages_corr_test.jsonl",
  ],
  validation: ["validation_summary.csv"],
};

const dynamicDataPatterns = {
  events: /^api_.+_parsed\.csv$/i,
  anomalies: /^api_.+_anomalies\.csv$/i,
  incidents: /^api_.+_incidents\.csv$/i,
};

const staticTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
};

function parseCsv(text, delimiter = ";") {
  const rows = [];
  let row = [];
  let value = "";
  let inQuotes = false;

  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    const next = text[index + 1];

    if (char === '"' && inQuotes && next === '"') {
      value += '"';
      index += 1;
      continue;
    }

    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }

    if (char === delimiter && !inQuotes) {
      row.push(value);
      value = "";
      continue;
    }

    if ((char === "\n" || char === "\r") && !inQuotes) {
      if (char === "\r" && next === "\n") index += 1;
      row.push(value);
      if (row.some((cell) => cell !== "")) rows.push(row);
      row = [];
      value = "";
      continue;
    }

    value += char;
  }

  row.push(value);
  if (row.some((cell) => cell !== "")) rows.push(row);
  if (rows.length === 0) return [];

  const headers = rows[0].map((header) => header.replace(/^\uFEFF/, ""));
  return rows.slice(1).map((cells) => {
    const item = {};
    headers.forEach((header, index) => {
      item[header] = cells[index] ?? "";
    });
    return item;
  });
}

function inferDelimiter(text) {
  const firstLine = text.split(/\r?\n/, 1)[0] || "";
  return [",", ";", "\t"].sort((a, b) => firstLine.split(b).length - firstLine.split(a).length)[0];
}

function sendJson(res, status, body) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(JSON.stringify(body));
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  let body = {};
  try {
    body = text ? JSON.parse(text) : {};
  } catch {
    body = { raw: text };
  }
  if (!response.ok) throw new Error(body.detail || body.error || `HTTP ${response.status}`);
  return body;
}

async function readJsonBody(req) {
  let body = "";
  for await (const chunk of req) body += chunk;
  if (!body.trim()) return {};
  return JSON.parse(body);
}

async function readLocalJsonLines(filename, limit = 100) {
  const raw = await fs.readFile(path.join(processedDir, filename), "utf8");
  const lines = raw.split(/\r?\n/).filter(Boolean);
  return lines
    .slice(Math.max(0, lines.length - Number(limit || 100)))
    .flatMap((line) => {
      try {
        return [JSON.parse(line)];
      } catch {
        return [];
      }
    });
}

function formatMetric(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(3) : "n/a";
}

function localExplanation(context) {
  const stats = context.stats || {};
  const incidents = context.incidents || [];
  const validation = context.validation || [];
  const messages = context.recentMessages || [];
  const bestModel = validation[0] || {};
  const topIncident = incidents[0] || {};

  const risk =
    Number(stats.criticalIncidents || 0) > 0
      ? "priorite elevee"
      : Number(stats.anomalies || 0) > 0
        ? "surveillance renforcee"
        : "situation stable";

  const lines = [
    `Synthese: le dashboard indique ${stats.events || 0} evenements, ${stats.anomalies || 0} anomalies candidates et ${stats.incidents || 0} incidents correles. Le niveau de lecture global est: ${risk}.`,
  ];

  if (topIncident.incident_id) {
    lines.push(
      `Incident principal: ${topIncident.incident_id} regroupe ${topIncident.event_count || "plusieurs"} evenements avec une severite ${topIncident.severity || "non renseignee"}. ${topIncident.summary || "Il faut ouvrir le detail des evenements lies pour confirmer la cause."}`,
    );
  }

  if (bestModel.model) {
    lines.push(
      `Validation modele: le meilleur resultat affiche concerne ${bestModel.dataset || "un dataset"} avec ${bestModel.model}. Les scores sont precision ${formatMetric(bestModel.precision)}, recall ${formatMetric(bestModel.recall)} et F1 ${formatMetric(bestModel.f1)}.`,
    );
  }

  if (messages.length) {
    const last = messages[messages.length - 1];
    lines.push(
      `Flux agents: le dernier message connu est ${last.message_type || "un message agent"} emis par ${last.source || "un agent"} vers ${last.target || "un autre agent"} avec le statut ${last.status || "inconnu"}.`,
    );
  }

  lines.push(
    "Lecture recommandee: verifier d'abord les incidents critiques, puis comparer les anomalies candidates avec les evenements normalises. Une anomalie isolee n'est pas forcement une attaque; la correlation et la repetition temporelle renforcent le signal.",
  );

  return lines.join("\n\n");
}

function extractOpenAiText(payload) {
  if (typeof payload.output_text === "string" && payload.output_text.trim()) return payload.output_text.trim();
  const parts = [];
  for (const item of payload.output || []) {
    for (const content of item.content || []) {
      if (typeof content.text === "string") parts.push(content.text);
    }
  }
  return parts.join("\n").trim();
}

async function callOpenAiExplanation(context) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return null;

  // Le LLM reste cote serveur: aucune cle API n'est exposee dans le navigateur.
  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL || "gpt-5.2",
      input: [
        {
          role: "system",
          content:
            "Tu es un analyste SOC francophone. Explique les resultats Ariel Logminer en langage clair, sans inventer de donnees. Donne une synthese, les risques, les points a verifier et une action prioritaire.",
        },
        {
          role: "user",
          content: `Voici un instantane JSON du dashboard Ariel Logminer. Explique-le pour un humain:\n${JSON.stringify(context).slice(0, 14000)}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`OpenAI ${response.status}: ${detail.slice(0, 240)}`);
  }

  return extractOpenAiText(await response.json());
}

async function handleExplain(req, res) {
  if (req.method !== "POST") {
    sendJson(res, 405, { error: "method not allowed" });
    return;
  }

  try {
    const context = await readJsonBody(req);
    const fallback = localExplanation(context);
    try {
      const explanation = await callOpenAiExplanation(context);
      sendJson(res, 200, { provider: explanation ? "openai" : "local", explanation: explanation || fallback });
    } catch (error) {
      sendJson(res, 200, { provider: "local", explanation: fallback, warning: error.message });
    }
  } catch (error) {
    sendJson(res, 400, { error: error.message });
  }
}

async function handleApi(req, res) {
  try {
    const url = new URL(req.url, `http://127.0.0.1:${activePort}`);
    const type = url.searchParams.get("type") || "";
    const limit = Number(url.searchParams.get("limit") || "0");
    const candidates = dataFiles[type];

    if (!candidates) {
      sendJson(res, 400, { error: "unknown data type" });
      return;
    }

    let file = "";
    let raw = "";
    let resolvedCandidates = [...candidates];
    const dynamicPattern = dynamicDataPatterns[type];
    if (dynamicPattern) {
      const entries = await fs.readdir(processedDir, { withFileTypes: true });
      const dynamic = await Promise.all(
        entries
          .filter((entry) => entry.isFile() && dynamicPattern.test(entry.name))
          .map(async (entry) => {
            const stat = await fs.stat(path.join(processedDir, entry.name));
            return { name: entry.name, mtimeMs: stat.mtimeMs };
          }),
      );
      resolvedCandidates = dynamic.sort((a, b) => b.mtimeMs - a.mtimeMs).map((entry) => entry.name).concat(resolvedCandidates);
    }

    for (const candidate of resolvedCandidates) {
      try {
        raw = await fs.readFile(path.join(processedDir, candidate), "utf8");
        file = candidate;
        break;
      } catch {
        // On essaie le fichier candidat suivant. Cela permet au dashboard de
        // rester lisible meme si un run n'a pas encore produit tous les CSV.
      }
    }

    if (!file) {
      sendJson(res, 200, { file: "", count: 0, data: [] });
      return;
    }

    const data =
      type === "messages"
        ? raw
            .split(/\r?\n/)
            .filter(Boolean)
            .flatMap((line) => {
              try {
                return [JSON.parse(line)];
              } catch {
                return [];
              }
            })
        : parseCsv(raw, inferDelimiter(raw));

    sendJson(res, 200, { file, count: data.length, data: limit > 0 ? data.slice(0, limit) : data });
  } catch (error) {
    sendJson(res, 404, { error: error.message });
  }
}

async function handleServices(req, res) {
  try {
    const [health, redisHealth, redisPending, mqttHealth, models, runtime] = await Promise.allSettled([
      fetchJson(`${fastApiBase}/health`),
      fetchJson(`${fastApiBase}/redis/health`),
      fetchJson(`${fastApiBase}/redis/pending`),
      fetchJson(`${fastApiBase}/mqtt/health`),
      fetchJson(`${fastApiBase}/models`),
      fetchJson(`${fastApiBase}/runtime/status`),
    ]);

    sendJson(res, 200, {
      apiBase: fastApiBase,
      api: health.status === "fulfilled" ? health.value : { status: "down", error: health.reason.message },
      redis:
        redisHealth.status === "fulfilled"
          ? redisHealth.value
          : { status: "down", error: redisHealth.reason.message },
      redisPending:
        redisPending.status === "fulfilled"
          ? redisPending.value
          : { pending: { pending: 0 }, error: redisPending.reason.message },
      mqtt:
        mqttHealth.status === "fulfilled"
          ? mqttHealth.value
          : { status: "down", error: mqttHealth.reason.message },
      models: models.status === "fulfilled" ? models.value.models || [] : [],
      runtime: runtime.status === "fulfilled" ? runtime.value : { docker_cli: false, docker_engine: false, message: runtime.reason.message },
    });
  } catch (error) {
    sendJson(res, 200, { apiBase: fastApiBase, api: { status: "down", error: error.message }, redis: { status: "down" }, redisPending: {}, mqtt: { status: "down" }, models: [], runtime: {} });
  }
}

async function handleRuntimePrepare(req, res) {
  try {
    const body = req.method === "POST" ? await readJsonBody(req) : {};
    sendJson(
      res,
      200,
      await fetchJson(`${fastApiBase}/runtime/prepare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start_desktop: true, wait_seconds: 45, ...body }),
      }),
    );
  } catch (error) {
    sendJson(res, 502, { error: error.message });
  }
}

async function handleRedisEvents(req, res) {
  try {
    const url = new URL(req.url, `http://127.0.0.1:${activePort}`);
    const runId = url.searchParams.get("run_id");
    const count = url.searchParams.get("count") || "100";
    const target = new URL(`${fastApiBase}/events`);
    target.searchParams.set("count", count);
    if (runId) target.searchParams.set("run_id", runId);
    sendJson(res, 200, await fetchJson(target));
  } catch (error) {
    try {
      const events = await readLocalJsonLines("agent_messages.jsonl", 100);
      sendJson(res, 200, { stream: "local", count: events.length, events, warning: error.message });
    } catch {
      sendJson(res, 200, { stream: "", count: 0, events: [], error: error.message });
    }
  }
}

async function handleAgentsStatus(req, res) {
  try {
    const url = new URL(req.url, `http://127.0.0.1:${activePort}`);
    const count = url.searchParams.get("count") || "500";
    const runId = url.searchParams.get("run_id");
    const target = new URL(`${fastApiBase}/agents/status`);
    target.searchParams.set("count", count);
    if (runId) target.searchParams.set("run_id", runId);
    sendJson(res, 200, await fetchJson(target));
  } catch (error) {
    sendJson(res, 200, { agents: {}, totals: {}, error: error.message });
  }
}

async function handleMqttPublish(req, res) {
  if (req.method !== "POST") {
    sendJson(res, 405, { error: "method not allowed" });
    return;
  }

  try {
    const body = await readJsonBody(req);
    sendJson(
      res,
      200,
      await fetchJson(`${fastApiBase}/mqtt/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          run_id: `dashboard-mqtt-${Date.now()}`,
          source: "dashboard",
          target: "collector",
          message_type: "dashboard.mqtt.test",
          payload: { source: "web-dashboard", ...body },
        }),
      }),
    );
  } catch (error) {
    sendJson(res, 502, { error: error.message });
  }
}

async function handleAudit(req, res) {
  try {
    const url = new URL(req.url, `http://127.0.0.1:${activePort}`);
    const limit = url.searchParams.get("limit") || "100";
    sendJson(res, 200, await fetchJson(`${fastApiBase}/audit?limit=${encodeURIComponent(limit)}`));
  } catch (error) {
    try {
      const url = new URL(req.url, `http://127.0.0.1:${activePort}`);
      const limit = Number(url.searchParams.get("limit") || "100");
      const events = await readLocalJsonLines("dashboard_audit.jsonl", limit);
      sendJson(res, 200, { count: events.length, events, source: "local", warning: error.message });
    } catch {
      sendJson(res, 200, { count: 0, events: [], error: error.message });
    }
  }
}

async function handleResources(req, res) {
  try {
    sendJson(res, 200, await fetchJson(`${fastApiBase}/resources`));
  } catch (error) {
    try {
      const raw = await fs.readFile(path.join(processedDir, "dashboard_resources.json"), "utf8");
      sendJson(res, 200, { ...JSON.parse(raw), source: "local", warning: error.message });
    } catch {
      sendJson(res, 200, { available: false, message: error.message });
    }
  }
}

async function handleCollectDiscover(req, res) {
  try {
    sendJson(
      res,
      200,
      await fetchJson(`${fastApiBase}/collect/discover`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_redis: true, max_files: 25, max_mb: 100 }),
      }),
    );
  } catch (error) {
    sendJson(res, 502, { error: error.message });
  }
}

async function handlePrivilegedCollect(req, res) {
  try {
    const body = req.method === "POST" ? await readJsonBody(req) : {};
    sendJson(
      res,
      200,
      await fetchJson(`${fastApiBase}/collect/windows/privileged`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_redis: true, days: 2, ...body }),
      }),
    );
  } catch (error) {
    sendJson(res, 502, { error: error.message });
  }
}

async function handleAutoRun(req, res) {
  try {
    const body = req.method === "POST" ? await readJsonBody(req) : {};
    sendJson(
      res,
      200,
      await fetchJson(`${fastApiBase}/run/discovered`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ use_redis: true, max_mb: 5, ...body }),
      }),
    );
  } catch (error) {
    sendJson(res, 502, { error: error.message });
  }
}

async function handleAlertDecision(req, res) {
  if (req.method !== "POST") {
    sendJson(res, 405, { error: "method not allowed" });
    return;
  }

  try {
    const body = await readJsonBody(req);
    sendJson(
      res,
      200,
      await fetchJson(`${fastApiBase}/alerts/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      }),
    );
  } catch (error) {
    sendJson(res, 502, { error: error.message });
  }
}

async function handleStatic(req, res) {
  const url = new URL(req.url, `http://127.0.0.1:${activePort}`);
  const requested = url.pathname === "/" ? "/index.html" : url.pathname;
  const baseDir = requested.startsWith("/pictures/") ? picturesDir : here;
  const localPath = requested.startsWith("/pictures/") ? requested.replace(/^\/pictures\//, "") : requested;
  const filePath = path.normalize(path.join(baseDir, localPath));

  if (!filePath.startsWith(baseDir)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  try {
    const content = await fs.readFile(filePath);
    res.writeHead(200, {
      "Content-Type": staticTypes[path.extname(filePath)] || "application/octet-stream",
      "Cache-Control": "no-store",
    });
    res.end(content);
  } catch {
    res.writeHead(404);
    res.end("Not found");
  }
}

const server = http.createServer((req, res) => {
  if (req.url?.startsWith("/api/data")) {
    handleApi(req, res);
  } else if (req.url?.startsWith("/api/services")) {
    handleServices(req, res);
  } else if (req.url?.startsWith("/api/runtime-prepare")) {
    handleRuntimePrepare(req, res);
  } else if (req.url?.startsWith("/api/redis-events")) {
    handleRedisEvents(req, res);
  } else if (req.url?.startsWith("/api/agents-status")) {
    handleAgentsStatus(req, res);
  } else if (req.url?.startsWith("/api/mqtt-publish")) {
    handleMqttPublish(req, res);
  } else if (req.url?.startsWith("/api/audit")) {
    handleAudit(req, res);
  } else if (req.url?.startsWith("/api/resources")) {
    handleResources(req, res);
  } else if (req.url?.startsWith("/api/collect-discover")) {
    handleCollectDiscover(req, res);
  } else if (req.url?.startsWith("/api/privileged-collect")) {
    handlePrivilegedCollect(req, res);
  } else if (req.url?.startsWith("/api/auto-run")) {
    handleAutoRun(req, res);
  } else if (req.url?.startsWith("/api/alert-decision")) {
    handleAlertDecision(req, res);
  } else if (req.url?.startsWith("/api/explain")) {
    handleExplain(req, res);
  } else {
    handleStatic(req, res);
  }
});

function listen(port, attemptsLeft = 10) {
  activePort = port;

  server.once("error", (error) => {
    if (error.code === "EADDRINUSE" && attemptsLeft > 0) {
      console.log(`Port ${port} occupe, essai sur ${port + 1}...`);
      listen(port + 1, attemptsLeft - 1);
      return;
    }
    throw error;
  });

  server.listen(port, "127.0.0.1", () => {
    console.log(`Ariel Logminer dashboard: http://127.0.0.1:${port}`);
  });
}

listen(preferredPort);
