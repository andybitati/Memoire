import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Clock3,
  Database,
  Filter,
  RefreshCw,
  Search,
  Server,
  ShieldAlert,
  Workflow,
} from "lucide-react";
import "./styles.css";

const DATA_LIMIT = 8000;

async function fetchData(type, limit = DATA_LIMIT) {
  const response = await fetch(`/api/data?type=${type}&limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Impossible de charger ${type}`);
  }
  return response.json();
}

function uniqueValues(rows, key) {
  return Array.from(new Set(rows.map((row) => row[key]).filter(Boolean))).sort();
}

function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function severityClass(value) {
  const severity = String(value || "").toUpperCase();
  if (severity === "CRITICAL") return "danger";
  if (severity === "ERROR") return "error";
  if (severity === "WARNING") return "warning";
  if (severity === "INFO") return "info";
  return "muted";
}

function useDashboardData() {
  const [state, setState] = useState({
    loading: true,
    error: "",
    events: [],
    anomalies: [],
    incidents: [],
    messages: [],
    meta: {},
  });

  async function load() {
    setState((current) => ({ ...current, loading: true, error: "" }));
    try {
      const [events, anomalies, incidents, messages] = await Promise.all([
        fetchData("events"),
        fetchData("anomalies"),
        fetchData("incidents", 2000),
        fetchData("messages", 200),
      ]);

      setState({
        loading: false,
        error: "",
        events: events.data,
        anomalies: anomalies.data,
        incidents: incidents.data,
        messages: messages.data,
        meta: {
          events: events.count,
          anomalies: anomalies.count,
          incidents: incidents.count,
          messages: messages.count,
        },
      });
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message }));
    }
  }

  useEffect(() => {
    load();
  }, []);

  return { ...state, reload: load };
}

function Sidebar({ events, anomalies, filters, setFilters, reload, loading }) {
  const filterSource = anomalies.length ? anomalies : events;
  const options = {
    host: uniqueValues(filterSource, "host"),
    severity: uniqueValues(filterSource, "severity"),
    category: uniqueValues(filterSource, "category"),
    source: uniqueValues(filterSource, "source").slice(0, 200),
  };

  function setFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value }));
  }

  return (
    <aside className="sidebar">
      <div className="brand">
        <ShieldAlert size={26} />
        <div>
          <strong>Ariel Logminer</strong>
          <span>Agents IA</span>
        </div>
      </div>

      <button className="primaryAction" onClick={reload} disabled={loading}>
        <RefreshCw size={18} />
        Actualiser
      </button>

      <label className="search">
        <Search size={17} />
        <input
          value={filters.query}
          onChange={(event) => setFilter("query", event.target.value)}
          placeholder="Rechercher message, source, user"
        />
      </label>

      <div className="filterTitle">
        <Filter size={17} />
        Filtres
      </div>

      {Object.entries(options).map(([key, values]) => (
        <label className="field" key={key}>
          <span>{key}</span>
          <select value={filters[key]} onChange={(event) => setFilter(key, event.target.value)}>
            <option value="">Tous</option>
            {values.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      ))}
    </aside>
  );
}

function Stat({ icon: Icon, label, value, tone }) {
  return (
    <section className={`stat ${tone || ""}`}>
      <Icon size={21} />
      <div>
        <span>{label}</span>
        <strong>{value.toLocaleString("fr-FR")}</strong>
      </div>
    </section>
  );
}

function filterRows(rows, filters) {
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

function Timeline({ rows }) {
  const buckets = useMemo(() => {
    const map = new Map();
    rows.forEach((row) => {
      const value = row.timestamp_iso || row.start_time;
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return;
      const key = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}-${String(
        date.getUTCDate(),
      ).padStart(2, "0")} ${String(date.getUTCHours()).padStart(2, "0")}h`;
      map.set(key, (map.get(key) || 0) + 1);
    });
    return Array.from(map.entries()).slice(-36);
  }, [rows]);

  const max = Math.max(...buckets.map(([, count]) => count), 1);

  return (
    <section className="panel timeline">
      <div className="panelHeader">
        <h2>Activité temporelle</h2>
        <Clock3 size={19} />
      </div>
      <div className="bars">
        {buckets.map(([label, count]) => (
          <div className="barColumn" key={label} title={`${label}: ${count}`}>
            <div className="bar" style={{ height: `${Math.max(6, (count / max) * 100)}%` }} />
            <span>{label.slice(-3)}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Incidents({ rows }) {
  return (
    <section className="panel">
      <div className="panelHeader">
        <h2>Incidents corrélés</h2>
        <Workflow size={19} />
      </div>
      <div className="incidentList">
        {rows.slice(0, 8).map((incident) => (
          <article className="incident" key={incident.incident_id}>
            <div>
              <strong>{incident.incident_id}</strong>
              <span>{incident.summary}</span>
            </div>
            <div className="incidentMeta">
              <span className={`pill ${severityClass(incident.severity)}`}>{incident.severity || "N/A"}</span>
              <span>{incident.event_count} evt</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function DataTable({ title, rows, columns, icon: Icon }) {
  return (
    <section className="panel tablePanel">
      <div className="panelHeader">
        <h2>{title}</h2>
        <Icon size={19} />
      </div>
      <div className="tableWrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column}>{column}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.slice(0, 120).map((row, index) => (
              <tr key={`${row.recno || row.incident_id || index}-${index}`}>
                {columns.map((column) => (
                  <td key={column}>
                    {column === "severity" ? (
                      <span className={`pill ${severityClass(row[column])}`}>{row[column] || "N/A"}</span>
                    ) : (
                      String(row[column] || "")
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Messages({ rows }) {
  return (
    <section className="panel messages">
      <div className="panelHeader">
        <h2>Communication agents</h2>
        <Activity size={19} />
      </div>
      {rows.slice(-8).map((message, index) => (
        <div className="message" key={`${message.timestamp}-${index}`}>
          <span>{message.message_type}</span>
          <strong>
            {message.source} → {message.target}
          </strong>
          <small>{message.status}</small>
        </div>
      ))}
    </section>
  );
}

function App() {
  const { loading, error, events, anomalies, incidents, messages, meta, reload } = useDashboardData();
  const [filters, setFilters] = useState({ query: "", host: "", severity: "", category: "", source: "" });

  const filteredEvents = useMemo(() => filterRows(events, filters), [events, filters]);
  const filteredAnomalies = useMemo(() => filterRows(anomalies, filters), [anomalies, filters]);
  const anomalyCount = anomalies.filter((row) => row.is_anomaly === "1").length;
  const criticalIncidents = incidents.filter((row) => ["CRITICAL", "ERROR"].includes(row.severity)).length;

  return (
    <div className="app">
      <Sidebar events={events} anomalies={anomalies} filters={filters} setFilters={setFilters} reload={reload} loading={loading} />
      <main className="content">
        <header className="topbar">
          <div>
            <span>Surveillance multi-agents</span>
            <h1>Centre d’analyse Ariel Logminer</h1>
          </div>
          <div className="status">
            <span className={error ? "dot errorDot" : "dot"} />
            {error || (loading ? "Chargement" : "Données synchronisées")}
          </div>
        </header>

        <div className="statsGrid">
          <Stat icon={Database} label="Événements" value={meta.events || events.length} tone="blue" />
          <Stat icon={AlertTriangle} label="Anomalies" value={anomalyCount} tone="amber" />
          <Stat icon={Workflow} label="Incidents" value={incidents.length} tone="green" />
          <Stat icon={Server} label="Incidents critiques" value={criticalIncidents} tone="rose" />
        </div>

        <div className="mainGrid">
          <Timeline rows={filteredEvents} />
          <Incidents rows={incidents} />
        </div>

        <DataTable
          title="Anomalies candidates"
          rows={filteredAnomalies}
          columns={["timestamp_iso", "severity", "event", "source", "host", "category", "anomaly_score", "message"]}
          icon={ShieldAlert}
        />

        <DataTable
          title="Événements normalisés"
          rows={filteredEvents}
          columns={["timestamp_iso", "severity", "event", "source", "host", "user", "category", "message"]}
          icon={BarChart3}
        />

        <Messages rows={messages} />
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
