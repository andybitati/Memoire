# Audit scientifique final du mémoire

| Domaine | Avant | Correction appliquée ou requise | Preuve finale | Statut |
| --- | --- | --- | --- | --- |
| Agents réels | Description centrée sur superviseur/workers | Architecture CNP avec agents à capacités, état, mémoire, refus et handlers multiples | `docs/TRUE_MULTI_AGENT_ARCHITECTURE.md`, code des agents | PARTIELLEMENT CORRIGÉ |
| Autonomie | Orchestration logicielle parfois formulée comme autonomie générale | Définition limitée aux décisions locales d’offre, refus et exécution | campagnes CNP et tests | CORRIGÉ |
| Mémoire | Présente ; bénéfice parfois suggéré | Influence décisionnelle conservée, aucun gain global revendiqué | benchmark mémoire ON/OFF | CORRIGÉ |
| Distribution | Anciennes campagnes 525 ACK mises en avant | Campagne `multivm_cnp_20260909T202632Z_37592`, 60/60, Debian/Ubuntu, Redis central | artefacts multi-VM | CORRIGÉ |
| HDFS | F1 événement `0,269307` utilisé comme résultat principal | F1 bloc `0,892308`, seuil gelé, bootstrap descriptif variable | P4 HDFS block robustness | CORRIGÉ |
| BGL | F1 `0,913698` sans baseline de nouveauté explicitée | 89,8081 % de templates inconnus et baseline `0,277885` ajoutés | protocole BGL strict | PARTIELLEMENT CORRIGÉ |
| CICIDS2017 | Protocoles random/holdout présents | Distinction random, scenario holdout et temporal maintenue | rapports CICIDS | CORRIGÉ |
| CSE-CIC | Résultat externe peu qualifié | LR `0,999212`, audit `Dst Port`, ablation top-10 et absence de fuite triviale seulement | audit P1 | CORRIGÉ |
| Routeur | 80/81 présenté comme preuve principale | Open-set calibré known-only : 3/3 rejetées, 0/28 faux rejet ; marge non probabiliste | P2 open-set | CORRIGÉ |
| Multiformat | 5001/7001 et voies HDFS/BGL à zéro | 7001/7001 lues, parsées et normalisées ; complétude des champs toujours limitée | artefact multiformat final | CORRIGÉ |
| E2E | Règle légère utilisée malgré les modèles recommandés | M : 1400/1401 inférences réelles, un fallback Apache, zéro erreur | P3 définitif | CORRIGÉ |
| Reproductibilité | Artefacts dispersés | manifest SHA-256, run_id, JUnit et figures 12–20 reliés au mémoire | manifeste final | CORRIGÉ |
| Industrialisation | Risque d’extrapolation | Haute disponibilité, multi-site, partitions et très grande échelle placées en perspectives | rapport final | HORS PÉRIMÈTRE |

## Points restant explicitement limités

- `0,999965` n’est pas un résultat scientifique du mémoire et ne doit pas réapparaître dans le résumé, les résultats ou la conclusion.
- Aucune accuracy globale multi-source n’est évaluée.
- Le F1 Linux/auth `0,390244` est descriptif sur une source sélectionnée et ne constitue pas une métrique globale.
- Les métriques CPU/RAM du benchmark monolithe/agents ne sont conservées que lorsque leur unité est documentée.
- Toute information non démontrable dans les artefacts doit rester marquée `INFORMATION À VÉRIFIER`.
