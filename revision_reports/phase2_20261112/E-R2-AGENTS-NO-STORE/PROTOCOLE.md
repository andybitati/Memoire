# Protocole E-R2-AGENTS-NO-STORE (préenregistré)

Rédigé le 2026-11-12, versionné dans le dépôt **avant** l'exécution complète. Toute
modification ultérieure est consignée dans la section « Écarts » du registre
`revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md`.

## 1. Question

La reprise sans effet dupliqué (exigence R2) tient-elle au magasin d'idempotence ou à
l'organisation en agents ? La panne appariée A–D (`agent3_paired_failure_abcd_20261104T141803Z`)
a montré que A et B dupliquent l'effet et que A+I et B+I ne le dupliquent pas. Il manque
l'ablation symétrique : des agents Contract Net **privés** du magasin.

Prédictions : E2 (mécanismes simples) prédit que C−I et D−I dupliquent l'effet de la tâche
interrompue ; E1 (organisation en agents) prédit qu'ils ne le dupliquent pas.

## 2. Dispositif

- Runner : `revision_reports/phase2_20261112/E-R2-AGENTS-NO-STORE/run_e_r2_agents_no_store.py`,
  qui importe sans modification `revision_reports/agent_3/run_paired_failure_abcd.py`
  (charge de 40 tâches, panne à l'index 9 après l'effet durable et sa persistance éventuelle,
  avant RESULT ; une reprise sur un worker vivant).
- Architectures (8), même processus, mêmes graines : A, B, C, D, A+I, B+I (contrôles,
  identiques à la campagne d'origine) ; **C−I** (Contract Net, mémoire désactivée, sans
  magasin) ; **D−I** (Contract Net, mémoire activée, sans magasin).
- Graines : 42 à 51 (10 répétitions par architecture, 80 exécutions).
- Transport : en processus (pas de Redis), comme la campagne d'origine.

## 3. Mesures

Par exécution : tâches perdues, effets dupliqués, effets de la tâche interrompue, reprise
confirmée, rejeu par le magasin, réattributions, latence de reprise.

## 4. Règle de décision (fixée avant exécution)

Pour chacune de C−I et D−I :
- au moins une tâche perdue → `invalide_perte_de_tache` (le dispositif ne mesure plus R2) ;
- sinon, effet dupliqué sur au moins 9 graines sur 10 → `doublon_sans_magasin` ;
- aucun effet dupliqué sur les 10 graines → `pas_de_doublon_sans_magasin` ;
- sinon → `indetermine`.

Conclusion : si C−I et D−I sont `doublon_sans_magasin` → **l'absence de doublon est due au
magasin** (soutient E2 pour R2) ; si tous deux sont `pas_de_doublon_sans_magasin` → les
agents évitent le doublon sans magasin (soutient E1) ; sinon non tranché.

Contrôle de validité : les six architectures de contrôle doivent reproduire la campagne
d'origine (A et B : 10 doublons ; C, D, A+I, B+I : 0 doublon ; aucune perte). Un écart rend
l'exécution non concluante ; il sera rapporté tel quel.

## 5. Conséquences préfixées sur le manuscrit

- `absence_de_doublon_due_au_magasin` : la phrase « l'effet tient au magasin d'idempotence,
  non aux agents » passe d'une inférence à un résultat d'ablation complet ; R2 reste
  satisfaite ; la limite « ablation agents sans magasin non exécutée » est retirée.
- `les_agents_evitent_le_doublon_sans_magasin` : corriger toutes les affirmations
  attribuant l'effet au seul magasin.
- `non_tranche` : rapporter tel quel.

## 6. Déclaration préalable

Un test à blanc (`--smoke`, graine 42, aucun artefact écrit) a été lancé avant ce
protocole pour vérifier le fonctionnement du runner. Sa sortie a été tronquée à
l'affichage avant les lignes C−I et D−I : les résultats de ces deux architectures n'ont
pas été lus. Les architectures de contrôle A à D affichées reproduisent la campagne
d'origine sur cette graine.
