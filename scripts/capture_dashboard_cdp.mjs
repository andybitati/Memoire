import fs from "node:fs/promises";
import { spawn } from "node:child_process";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..");
const edge = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const docsDir = path.join(root, "docs", "memoire", "captures");
const latexDir = path.join(root, "memoire_logminer_latex_overleaf", "captures");
const port = 9300 + Math.floor(Math.random() * 400);

const captures = [
  ["dashboard_vue_ensemble.png", "http://127.0.0.1:5173/?view=overview", 1600, 1100],
  ["dashboard_resultats_detail_incident.png", "http://127.0.0.1:5173/?view=results", 1600, 1200],
  ["dashboard_ressources_audit.png", "http://127.0.0.1:5173/?view=technical", 1600, 1300],
  ["dashboard_longue_vue.png", "http://127.0.0.1:5173/?view=overview", 1600, 1800],
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function requestJson(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs || 2500);
  const { timeoutMs, ...fetchOptions } = options;
  const response = await fetch(url, { ...fetchOptions, signal: controller.signal });
  clearTimeout(timeout);
  if (!response.ok) throw new Error(`${response.status} ${await response.text()}`);
  return response.json();
}

async function waitDebug() {
  for (let index = 0; index < 80; index += 1) {
    try {
      await requestJson(`http://127.0.0.1:${port}/json/version`);
      return;
    } catch {
      await delay(250);
    }
  }
  throw new Error("Edge DevTools endpoint unavailable");
}

async function newPage(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000);
  const response = await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`, { method: "PUT", signal: controller.signal });
  clearTimeout(timeout);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function connect(wsUrl) {
  const socket = new WebSocket(wsUrl);
  let seq = 0;
  const pending = new Map();

  socket.addEventListener("message", (event) => {
    const payload = JSON.parse(event.data);
    if (payload.id && pending.has(payload.id)) {
      const { resolve, reject } = pending.get(payload.id);
      pending.delete(payload.id);
      if (payload.error) reject(new Error(payload.error.message));
      else resolve(payload.result || {});
    }
  });

  return new Promise((resolve, reject) => {
    socket.addEventListener("open", () => {
      resolve({
        send(method, params = {}) {
          const id = ++seq;
          socket.send(JSON.stringify({ id, method, params }));
          return new Promise((sendResolve, sendReject) => {
            pending.set(id, { resolve: sendResolve, reject: sendReject });
          });
        },
        close() {
          socket.close();
        },
      });
    });
    socket.addEventListener("error", reject);
  });
}

async function captureOne(browser, filename, url, width, height) {
  const page = await newPage(url);
  const cdp = await connect(page.webSocketDebuggerUrl);
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width,
    height,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await cdp.send("Page.navigate", { url });
  for (let index = 0; index < 80; index += 1) {
    const result = await cdp.send("Runtime.evaluate", {
      expression: "document.body ? document.body.innerText : ''",
      returnByValue: true,
    });
    const text = String(result.result?.value || "");
    if (text.includes("Système Synchronisé") || text.includes("système synchronisé")) {
      break;
    }
    await delay(1000);
  }
  await cdp.send("Runtime.evaluate", {
    expression: "window.__logminerRefreshForCapture ? window.__logminerRefreshForCapture() : Promise.resolve()",
    awaitPromise: true,
  });
  for (let index = 0; index < 80; index += 1) {
    const result = await cdp.send("Runtime.evaluate", {
      expression: "document.body ? document.body.innerText : ''",
      returnByValue: true,
    });
    const text = String(result.result?.value || "");
    const servicesReady = !url.includes("technical") || (
      text.includes("FastAPI") &&
      text.includes("Redis Streams") &&
      text.includes("MQTT") &&
      !text.includes("fetch failed")
    );
    if (text.includes("Ariel Logminer") && servicesReady) {
      break;
    }
    await delay(1000);
  }
  await cdp.send("Runtime.evaluate", {
    expression: "document.fonts && document.fonts.ready",
    awaitPromise: true,
  });
  await delay(3000);
  const screenshot = await cdp.send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
    fromSurface: true,
  });
  cdp.close();

  const docsPath = path.join(docsDir, filename);
  const latexPath = path.join(latexDir, filename);
  const image = Buffer.from(screenshot.data, "base64");
  await fs.writeFile(docsPath, image);
  await fs.writeFile(latexPath, image);
  console.log(`${filename}: ${image.length} bytes`);
}

await fs.mkdir(docsDir, { recursive: true });
await fs.mkdir(latexDir, { recursive: true });

const profile = path.join(root, "data", "processed", "_edge_dashboard_cdp");
await fs.rm(profile, { recursive: true, force: true });
await fs.mkdir(profile, { recursive: true });

const browser = spawn(edge, [
  "--headless=new",
  "--disable-gpu",
  "--disable-crash-reporter",
  "--disable-breakpad",
  "--no-first-run",
  "--no-default-browser-check",
  `--user-data-dir=${profile}`,
  `--remote-debugging-port=${port}`,
  "about:blank",
], { stdio: "ignore" });

try {
  await waitDebug();
  for (const capture of captures) {
    await captureOne(browser, ...capture);
  }
} finally {
  browser.kill();
}
