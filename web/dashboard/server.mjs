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
