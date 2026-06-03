# Diagrammes Pour Le Memoire

Ces diagrammes completent les figures SVG generees dans
`docs/memoire/figures`. Ils sont ecrits en Mermaid pour rester faciles a
modifier et exporter.

## Architecture Generale

```mermaid
flowchart LR
    A[Sources de logs<br/>Windows, Linux, Wazuh, HDFS, BGL, reseau] --> B[Agent collecteur]
    B --> C[Agent parseur]
    C --> D[Normalisation Logminer<br/>schema commun CSV]
    D --> E[Routeur multi-modeles]
    E --> F1[Modele Windows/Wazuh<br/>Isolation Forest]
    E --> F2[Modele Linux/auth<br/>RandomForest]
    E --> F3[Modele reseau<br/>CICIDS/UNSW]
    E --> F4[Modeles HDFS/BGL/fallback]
    F1 --> G[Anomalies candidates]
    F2 --> G
    F3 --> G
    F4 --> G
    G --> H[Agent correlateur<br/>incidents priorises]
    H --> I[Dashboard web/Streamlit]
    I --> J[Decision analyste<br/>validation, rejet, reclassement]
    J --> K[Audit trail]
```

## Sequence Du Workflow V2 FastAPI

```mermaid
sequenceDiagram
    participant U as Analyste/Dashboard
    participant API as FastAPI
    participant C as Collecteur
    participant P as Parseur
    participant R as Routeur
    participant D as Detecteur
    participant K as Correlateur
    participant A as Audit/Bus

    U->>API: POST /run/discovered
    API->>C: decouvrir une source locale
    C-->>API: candidat selectionne
    alt log brut
        API->>P: parsing + normalisation
        P-->>API: CSV normalise
    else CSV/Parquet deja structure
        API-->>API: reutilisation directe
    end
    API->>R: identifier famille de logs
    R-->>API: modele adapte
    API->>D: detection IA/statistique
    D-->>API: anomalies candidates
    API->>K: correlation temporelle/contextuelle
    K-->>API: incidents
    API->>A: workflow.completed + metriques
    API-->>U: chemins CSV, compteurs, latence
```

## Positionnement V1 / V2 / V3

```mermaid
flowchart TB
    V1[V1 CLI stable<br/>parsing, detection, correlation, CSV] --> V2[V2 FastAPI locale<br/>endpoints agents, dashboard web]
    V2 --> V3[V3 Redis/MQTT<br/>bus evenementiel, distribution future]
    V1 --> S[Socle defendable pour soutenance]
    V2 --> D[Demonstration interactive]
    V3 --> P[Perspective industrialisation]
```

## Cycle D'Evaluation

```mermaid
flowchart LR
    A[Datasets publics<br/>HDFS, BGL, CICIDS, UNSW] --> C[Preparation]
    B[Logs reels locaux<br/>Windows, Wazuh, Linux/auth] --> C
    C --> D[Parsing / normalisation]
    D --> E[Detection par modele adapte]
    E --> F[Metriques<br/>precision, rappel, F1]
    E --> G[Latence / memoire / robustesse]
    F --> H[Tableaux du memoire]
    G --> H
    H --> I[Discussion critique<br/>limites et perspectives]
```
