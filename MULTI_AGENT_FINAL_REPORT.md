# Rapport final — système multi-agents autonome léger

Date : 2026-09-09  
Run expérimental de référence : `ma_20260909T154523Z_13604`

## Résultat général

Le noyau Logminer dispose désormais d'un protocole Contract Net léger réellement exécuté. Plusieurs agents évaluent le même appel, proposent une utilité ou refusent avec un motif explicite, puis l'un d'eux accepte et exécute le contrat. La mémoire intervient dans le calcul local, un mode OFF permet l'ablation, et une clé d'idempotence persistante empêche la répétition de l'effet dans le scénario contrôlé post-traitement/pré-ACK.

Cette validation reste locale. Elle ne transforme pas les anciennes campagnes Redis en campagnes Contract Net et ne démontre pas une exécution autonome entre les VM Debian et Ubuntu.

| Élément | Statut final | Preuve principale |
|---|---|---|
| Analyse d'écart préalable | RÉALISÉE | `docs/MULTI_AGENT_GAP_ANALYSIS.md` |
| Contrat `AgentMessage` à sept champs | PRÉSERVÉ ET TESTÉ | `src/logminer/agents/bus.py`, test unitaire |
| Contract Net à neuf messages | IMPLÉMENTÉ, TESTÉ, ÉVALUÉ LOCALEMENT | `contract_net.py`, logs JSONL du run |
| État local et refus explicites | IMPLÉMENTÉS ET TESTÉS | `intelligent_runtime.py`, test des six motifs |
| Mémoire ON/OFF | IMPLÉMENTÉE ET ÉVALUÉE | campagne A/B/C/D et adaptation |
| Idempotence persistante | IMPLÉMENTÉE ET ÉVALUÉE DANS UN HARNAIS CONTRÔLÉ | JSON et SQLite de reprise |
| Pipeline Logminer bout en bout | EXÉCUTÉ UNE FOIS AVEC SUCCÈS | six étapes, 6/6 réussies |
| CNP Redis inter-processus | NON ÉVALUÉ | aucune campagne correspondante |
| CNP multi-VM Debian/Ubuntu | NON ÉVALUÉ | aucune campagne correspondante |
| Environnement industriel | NON ÉVALUÉ | hors périmètre |

## Modifications apportées

- `src/logminer/agents/contract_net.py` implémente `CFP`, `PROPOSE`, `REFUSE`, `AWARD`, `REJECT`, `ACCEPT`, `RESULT`, `FAIL` et `FEEDBACK`.
- `src/logminer/agents/idempotency.py` fournit un registre SQLite transactionnel.
- `src/logminer/agents/intelligent_runtime.py` expose la perception, l'évaluation, le calcul d'offre, la proposition, le refus, l'acceptation, l'exécution et l'apprentissage.
- `experiments/phase_multi_agent/configs/agent_policy.json` fixe les poids 0,30 / 0,20 / 0,20 / 0,15 / 0,10 / 0,05. Ils ne sont pas présentés comme optimaux.
- `scripts/run_true_multi_agent_experiments.py` exécute les comparaisons, les expériences complémentaires, les agrégations, les figures et les manifestes.
- `tests/test_true_multi_agent.py` contrôle les invariants principaux.

`AgentMessage` n'a reçu aucun champ supplémentaire. Les identifiants de contrat, de tâche, d'idempotence et de pipeline restent dans `payload`.

## Validation logicielle

La commande `python -m unittest discover -s tests -p "test_*.py" -v` termine avec 7 tests réussis sur 7. Elle vérifie :

- la liste exacte des sept champs d'`AgentMessage`;
- la fiabilité de Laplace `(s+1)/(s+f+2)`;
- le cycle nominal avec proposition, refus, attribution, rejet, acceptation, résultat et feedback;
- le message `FAIL` en l'absence de proposition;
- les six motifs de refus;
- l'effet de la mémoire activée et sa neutralisation en mode OFF;
- la reprise par un second agent sans répétition de l'effet persistant.

## Protocole expérimental principal

Les quatre architectures utilisent les mêmes tâches synthétiques et les mêmes graines pour chaque couple charge/répétition :

- A — monolithe séquentiel;
- B — trois workers avec attribution centralisée;
- C — trois agents Contract Net, mémoire OFF;
- D — trois agents Contract Net, mémoire ON.

Les charges sont 100, 500, 1 000 et 5 000 tâches. Chaque charge est répétée dix fois. L'ordre A/B/C/D est tournant afin de limiter un biais systématique d'ordre. Le run comprend 160 exécutions, soit 264 000 traitements répartis également : 66 000 par architecture. Aucun traitement principal n'a échoué.

Les tâches de cette comparaison sont des microcharges déterministes de douze entiers. Elles mesurent le coût du mécanisme d'allocation; elles ne reproduisent pas le coût d'une inférence complète sur un dataset de sécurité.

## Résultats principaux

### Charge de 5 000 tâches

| Architecture | Débit moyen (tâches/s) | IC 95 % du débit | p95 moyen (ms) | CPU machine moyen (%) | RSS maximale moyenne (MiB) | Messages/tâche | Jain moyen |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 79 251,580 | [66 789,961 ; 91 713,199] | 0,013702 | 11,668029 | 281,793360 | 0 | 1,000000 |
| B | 14 969,109 | [13 374,664 ; 16 563,554] | 0,019001 | 12,697017 | 283,496875 | 0 | 1,000000 |
| C | 1 240,881 | [1 195,945 ; 1 285,816] | 1,795485 | 12,751358 | 287,951953 | 9,998020 | 0,891725 |
| D | 1 187,320 | [1 159,508 ; 1 215,132] | 1,264055 | 12,581053 | 292,896875 | 9,999500 | 0,888888 |

Le protocole autonome réussit toutes les tâches mais introduit un coût important sur cette microcharge. À 5 000 tâches, A et B ont un débit nettement supérieur à C et D. Ce résultat ne mesure pas un gain métier; il quantifie surtout le prix des messages, des offres et de la traçabilité lorsque le calcul utile est très court.

L'indice de Jain de A vaut 1 par construction, puisqu'il n'existe qu'un exécutant; cette valeur n'est pas comparable à une équité entre trois agents. B approche 1 parce que le répartiteur applique un round-robin. C et D privilégient les agents dont les capacités déclarées correspondent le mieux au type de tâche, d'où une distribution moins uniforme.

### Ablation de la mémoire

| Charge | Débit C, mémoire OFF | Débit D, mémoire ON | p95 C (ms) | p95 D (ms) | Jain C | Jain D |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 1 287,107 | 1 301,296 | 1,403 | 3,170 | 0,860 | 0,888 |
| 500 | 1 116,624 | 1 107,330 | 2,524 | 3,158 | 0,917 | 0,900 |
| 1 000 | 1 007,350 | 984,157 | 1,822 | 2,192 | 0,890 | 0,889 |
| 5 000 | 1 240,881 | 1 187,320 | 1,795 | 1,264 | 0,892 | 0,889 |

La mémoire ne produit pas de gain systématique de débit, de latence ou d'équité dans cette comparaison. D dépasse légèrement C en débit à 100 tâches seulement; C est supérieur aux trois autres charges. La latence p95 de D est plus basse à 5 000 tâches, mais plus haute aux charges 100, 500 et 1 000. Toute affirmation générale de gain de performance dû à la mémoire serait donc incorrecte.

Les agents C ont émis 659 901 messages CNP et les agents D 659 918. Une négociation nominale consomme dix messages. Les faibles écarts proviennent des refus transitoires dus à la charge, qui changent le nombre de propositions et de rejets. Aucune réattribution après `AWARD` n'a été requise pendant les 160 runs principaux.

## Adaptation en deux phases

L'expérience contrôlée comprend 120 tâches d'un même type. Pendant les 60 premières, `agent-alpha` est le spécialiste capable de réussir; pendant les 60 suivantes, cette propriété passe à `agent-gamma`.

| Phase | Tâches | Gagnant final alpha | Gagnant final gamma | Réattributions |
|---|---:|---:|---:|---:|
| 1 | 60 | 60 | 0 | 0 |
| 2 | 60 | 0 | 60 | 8 |

Au changement de phase, la mémoire favorise d'abord alpha. La première tâche exige deux réattributions, puis les offres se corrigent. À l'index 67, l'utilité de gamma atteint 0,947776 contre 0,946809 pour alpha; les tâches suivantes ne nécessitent plus de réattribution. Cette expérience démontre une adaptation du mécanisme à un changement conçu pour être observable. Elle ne démontre pas une amélioration prédictive sur des logs réels.

## Reprise post-traitement/pré-ACK

Le scénario contrôlé suit la séquence demandée : l'agent A prend la tâche, exécute l'effet, rend le résultat durable, puis aucun ACK n'est émis. La tâche reste pending, est attribuée à l'agent B, qui détecte la clé déjà terminée, relit le résultat et ACK la tâche sans réexécuter le handler.

| Mesure | Valeur |
|---|---:|
| Effets persistants observés | 1 |
| Effets dupliqués | 0 |
| Tâches récupérées | 1 |
| Latence de reprise | 0,003836 s |
| Pending final | 0 |
| Lag final | 0 |

Le transport de ce test est un harnais local nommé `controlled_pending_queue`. Ces valeurs ne doivent pas être attribuées à Redis, à une VM ni à un réseau réel. L'expérience valide la logique d'idempotence dans ce point de panne précis.

## Pipeline bout en bout

Le run `e2e-ma_20260909T154523Z_13604` a exécuté six étapes avec des handlers Logminer réels :

| Étape | Agent retenu | Statut | Messages CNP |
|---|---|---|---:|
| `discover.logs` | `e2e-alpha` | ok | 10 |
| `parse.logs` | `e2e-beta` | ok | 10 |
| `route.model` | `e2e-gamma` | ok | 10 |
| `detect.anomalies` | `e2e-alpha` | ok | 10 |
| `correlate.incidents` | `e2e-beta` | ok | 10 |
| `feedback.apply` | `e2e-gamma` | ok | 10 |

Le bilan est 6/6 étapes réussies. Cette exécution prouve que le protocole peut enchaîner le parsing de l'échantillon Windows, le routage, la détection, la corrélation et l'application de la mémoire de feedback. Il s'agit d'un seul run local sur un échantillon; aucune conclusion de robustesse statistique n'en découle.

## CPU, mémoire et latence

- `duration_sec` est un temps mural issu de `time.perf_counter()`.
- Le débit est le nombre de tâches réussies divisé par cette durée.
- Les latences A/B mesurent le service du handler; les latences C/D couvrent la négociation et l'exécution une fois la tâche prise par un thread du coordinateur. Le temps d'attente préalable dans l'exécuteur n'est pas inclus.
- `cpu_time_sec` additionne les temps utilisateur et système du processus Python.
- `cpu_core_equivalent_percent = cpu_time_sec / durée × 100`; 100 % correspond à un cœur occupé pendant toute la mesure.
- `cpu_machine_normalized_percent` divise cette valeur par les huit processeurs logiques observés.
- La RSS est la mémoire résidente du processus Python, en MiB, échantillonnée toutes les 5 ms. Elle n'est ni la RAM de la machine ni la somme de processus distribués.

Les mesures CPU des runs les plus courts sont sensibles à la résolution du compteur; les charges élevées sont plus interprétables. Les valeurs RSS sont absolues et incluent l'interpréteur, les bibliothèques, le workload courant et les traces maintenues pendant un run. Elles ne doivent pas être assimilées à la seule mémoire du protocole.

## Traçabilité

Les artefacts du run de référence sont répartis sous `experiments/phase_multi_agent/` :

- brut par run : `raw/ma_20260909T154523Z_13604__runs.csv`;
- latences brutes : `raw/ma_20260909T154523Z_13604__task_latencies.csv`;
- agrégats : `aggregated/ma_20260909T154523Z_13604__statistics.csv`;
- adaptation : `raw/ma_20260909T154523Z_13604__adaptation.csv`;
- reprise : `raw/ma_20260909T154523Z_13604__recovery.json` et base SQLite associée;
- pipeline : `raw/ma_20260909T154523Z_13604__end_to_end.json` et dossier de sorties;
- messages : `logs/ma_20260909T154523Z_13604__representative_cnp_messages.jsonl` et log bout en bout;
- figures : `figures/ma_20260909T154523Z_13604/01_...png` à `10_...png`;
- environnement : `manifests/ma_20260909T154523Z_13604__environment.json`;
- sommes : `manifests/ma_20260909T154523Z_13604__sha256.json`;
- journal append-only : `manifests/EXPERIMENT_LEDGER.csv`.

Le premier smoke test (`ma_20260909T153649Z_47552`) a échoué à l'étape de corrélation explicite en raison d'un séparateur `auto` non accepté à cet endroit. Son artefact bout en bout porte bien le statut `error`, même si la version initiale du ledger avait classé le run global `ok`. Cette incohérence de statut a été corrigée dans le script. Le run n'est pas retenu. Un second smoke test a validé la correction. Le premier run complet (`ma_20260909T153914Z_47116`) a ensuite mis en évidence que la conservation de toutes les latences en mémoire biaisait la RSS. Il reste conservé, mais le run `ma_20260909T154523Z_13604`, qui écrit ces latences progressivement, est le seul run principal retenu.

## Ce qui peut être affirmé

- Un Contract Net léger est implémenté et observable dans Logminer.
- Les agents calculent localement une utilité normalisée et peuvent refuser avec six motifs explicites.
- Le contrat `AgentMessage` reste inchangé.
- Les campagnes locales A/B/C/D totalisent 160 runs et 264 000 traitements sans échec sur la microcharge utilisée.
- La mémoire influence effectivement les offres et permet une adaptation dans le scénario contrôlé à deux phases.
- Aucun gain systématique de performance n'est observé avec la mémoire ON.
- Le scénario local post-traitement/pré-ACK termine avec zéro effet dupliqué et une tâche récupérée.
- Le pipeline local à six étapes termine avec 6/6 succès.

## Ce qui ne peut pas être affirmé

- Le protocole autonome n'a pas encore été évalué entre processus Redis distincts.
- Aucune nouvelle campagne CNP multi-VM Debian/Ubuntu n'a été exécutée.
- La reprise mesurée n'est pas une mesure Redis ou réseau.
- L'expérience d'adaptation ne prouve aucun gain prédictif sur un dataset de sécurité.
- La mémoire ON n'améliore pas systématiquement le débit, la latence ou l'équité.
- Les résultats ne justifient aucune extrapolation à un environnement industriel.
- Les poids de l'utilité ne sont pas optimaux.

## Conclusion

L'objectif architectural local est atteint : Logminer possède désormais des agents multi-capacités qui négocient, refusent, acceptent, exécutent et apprennent selon un protocole traçable. L'évaluation met toutefois en évidence un compromis net. Sur une microcharge, l'autonomie coûte environ dix messages par tâche et réduit fortement le débit. La mémoire est utile pour réorienter les offres après une rupture conçue, mais elle n'apporte pas de gain de performance général dans la campagne principale. La prochaine validation légitime est une exécution Redis inter-processus, suivie seulement ensuite d'une campagne CNP réellement distribuée sur Debian et Ubuntu.
