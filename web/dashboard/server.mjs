import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const processedDir = path.join(root, "data", "processed");
const preferredPort = Number(process.env.PORT || 5173);
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

const staticTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
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

function sendJson(res, status, body) {
  res.writeHead(status, { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" });
  res.end(JSON.stringify(body));
}

async function readJsonBody(req) {
  let body = "";
  for await (const chunk of req) body += chunk;
  if (!body.trim()) return {};
  return JSON.parse(body);
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
            "Tu es un analyste SOC francophone. Explique les resultats Logminer en langage clair, sans inventer de donnees. Donne une synthese, les risques, les points a verifier et une action prioritaire.",
        },
        {
          role: "user",
          content: `Voici un instantane JSON du dashboard Logminer. Explique-le pour un humain:\n${JSON.stringify(context).slice(0, 14000)}`,
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
    for (const candidate of candidates) {
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
        : parseCsv(raw);

    sendJson(res, 200, { file, count: data.length, data: limit > 0 ? data.slice(0, limit) : data });
  } catch (error) {
    sendJson(res, 404, { error: error.message });
  }
}

async function handleStatic(req, res) {
  const url = new URL(req.url, `http://127.0.0.1:${activePort}`);
  const requested = url.pathname === "/" ? "/index.html" : url.pathname;
  const filePath = path.normalize(path.join(here, requested));

  if (!filePath.startsWith(here)) {
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
    console.log(`Logminer React dashboard: http://127.0.0.1:${port}`);
  });
}

listen(preferredPort);
