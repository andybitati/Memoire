# Contrat Des Messages Agents

Ce contrat rattache l'architecture Logminer a l'objectif 3 du document
directeur: les agents specialises doivent cooperer avec un format stable,
lisible et reutilisable en local comme en mode distribue.

## Format Canonique

Le message canonique est `AgentMessage` dans `src/logminer/agents/bus.py`.
Il est transporte en JSONL pour le prototype local et en Redis Streams pour la
version distribuee.

| Champ | Type | Obligatoire | Role |
| --- | --- | --- | --- |
| `run_id` | string | oui | Identifie un cycle d'analyse complet. |
| `source` | string | oui | Agent emetteur: `collector`, `parser`, `detector`, `correlator`, `dashboard`, `runtime`, `privilege`, `orchestrator`. |
| `target` | string | oui | Agent destinataire ou etape suivante. |
| `message_type` | string | oui | Evenement fonctionnel publie par l'agent. |
| `payload` | object | non | Donnees utiles: chemins, compteurs, durees, erreurs, identifiants. |
| `status` | string | oui | `ok`, `warning` ou `error`. |
| `timestamp` | string ISO 8601 UTC | oui | Date d'emission du message. |

Exemple:

```json
{
  "run_id": "20260602_103336",
  "source": "detector",
  "target": "correlator",
  "message_type": "detection.completed",
  "payload": {
    "input_csv": "data/processed/events.csv",
    "output_csv": "data/processed/anomalies.csv",
    "anomalies": 37
  },
  "status": "ok",
  "timestamp": "2026-06-02T10:33:36+00:00"
}
```

## Types De Messages Attendues

| Agent source | Message | Cible | Contenu attendu |
| --- | --- | --- | --- |
| `runtime` | `runtime.prepare.started` / `runtime.prepare.completed` | `orchestrator` | Etat Docker/Redis, disponibilite du bus. |
| `collector` | `collector.discovery.started` / `collector.discovery.completed` | `parser` | Racines scannees, fichiers retenus, volume maximal. |
| `parser` | `parse.started` / `parse.completed` | `detector` | CSV normalise produit, nombre de lignes. |
| `detector` | `detection.started` / `detection.completed` | `correlator` | Modele choisi, anomalies candidates, duree. |
| `correlator` | `correlation.started` / `correlation.completed` | `dashboard` | Incidents, priorite, justification. |
| `dashboard` | `alert.decision` | `audit` | Validation, rejet ou reclassement analyste. |
| `privilege` | `privilege.request.started` / `privilege.request.completed` | `collector` | Demande d'acces aux journaux proteges Windows. |

## Regles De Fidélité Au Document Directeur

- La correlation est une responsabilite de l'agent `correlator`, rattachee a
  l'objectif 3, et non un objectif autonome.
- Les anomalies produites par l'agent `detector` sont des candidates; la
  validation finale peut etre confirmee, rejetee ou reclassee par l'analyste.
- Le meme contrat doit rester lisible dans le dashboard afin de montrer la
  cooperation entre agents.
- Le passage JSONL -> Redis Streams ne change pas le schema fonctionnel du
  message.

