# HANDOFF — Révision finale du mémoire Ariel Logminer

Dernière mise à jour : 2026-11-05, reprise du chantier (heure locale, UTC+1). À lire en premier par tout agent qui reprend ce travail.

## 1. Mission

Cahier de révision de l'auteur (orchestrateur + 7 agents, puis intégration). Texte intégral : `C:\Users\aoliv\.codex\attachments\77e525f3-98c7-4be5-b6a2-23a32125224c\Pasted text.txt` ; les 20 remarques du jury : `C:\Users\aoliv\.codex\attachments\57d28dce-8353-41d2-b310-3166dab4a349\Pasted text.txt`.

Règles impératives (à respecter aussi pendant l'intégration) :
1. Aucun chiffre inventé : chaque nombre cité vient d'un CSV/JSON avec run_id et chemin.
2. Si une expérience contredit le mémoire, corriger l'affirmation, jamais le résultat.
3. Français soutenu, sobre ; limites formulées une seule fois (chapitre « 5 » du PDF = `chapitre6_approfondissements_scientifiques.tex`), renvois ailleurs.
4. L'auteur ne veut aucune référence à plusieurs versions du travail ou des agents dans la rédaction : présenter un seul travail, sans hésitation.

## 2. État

| Étape | État |
|---|---|
| Phase 1, agents 1 à 7 | **Terminée.** Chaque agent a produit `revision_reports/agent_<N>/PATCH_NOTES.md` + artefacts |
| Phase 2.1, conflits | **Rédigé** : `revision_reports/INTEGRATION_CONFLICTS.md` (arbitrages proposés) |
| Décisions de l'auteur D1–D4 | **Tranchées** : autonomie donnée pour finaliser ; décisions consignées au §4 |
| Phase 2.2–2.5, application aux `.tex`, matrice A.2, compilation, contrôle grep | **Terminée** : lots L1–L20 appliqués et contrôlés |
| Commit git | Aucun. Dernier commit : `35da3a9` ; `revision_reports/` non suivi |

## 3. Résultats nouveaux à intégrer (tous vérifiés)

| Sujet | run_id | Résultat | Notes |
|---|---|---|---|
| HDFS test complet, 5 graines | `agent2_hdfs_full_20261104T131314Z` (+ réplique identique `…134240Z`) | F1 0,868373, IC [0,856771 ; 0,879493] ; TP 1 679, FP 509, FN 0 ; variance nulle entre graines | Remplace 0,892308 (hors IC). Prévalence train/val/test 3,23/3,48/1,46 % : due à la partition chronologique |
| Histogram formel | — | Score par événement : moyenne des −log fréquences (template, source, sévérité) sur le normal du train | BGL = événement, **pas fenêtre** (ch. 4 l. 78, ch. 5 l. 35 faux) |
| HDFS via CNP sur 2 VM | `hdfs_multivm_cnp_20261104T135345Z` | 2 000/2 000 ; F1 0,892308 identique au centralisé ; **Debian 2 000, Ubuntu 0** | Utilités égales (0,845), départage alphabétique `redis_contract_net.py:234` |
| Répartition endurance 451/1 349 | `cnp_endurance_multivm_20260918T130822Z` | Expliquée par les profils de confiance (`scripts/logminer_redis_cnp_agent.py:28-32`) ; ni Python ni charge | 0,499 t/s = charge offerte |
| Saturation 2 VM | `agent3_saturation_multivm_20261104T142325Z` | Coude 8–16 t/s ; plafond 8,4–15,0 t/s ; 3 échecs / 11 430 (corrigé le 2026-11-05 ; l'ancien « 10 080 » était faux) | 3 répétitions au lieu de 10 |
| Panne appariée A/B/C/D | `agent3_paired_failure_abcd_20261104T141803Z` | Doublons A 10, B 10, C 0, D 0 ; ablation A+I, B+I : 0 | Gain = idempotence, pas Contract Net ; in-process |
| BGL second protocole | `agent4_bgl_*` | 0,913698 = règle « sévérité absente du train » ; protocole contigu G : F1 0,941927 (conçu a posteriori) | |
| IDS2018 | `agent4_csecic_shortcut_20261104T144738Z` | Dst Port < 1024 seul : 0,999720 ; sens 16→15 : LR 0,234 ; RF 0,40 = SlowHTTPTest port 21 jamais vu | Seuls 15 et 16 février locaux ; fichiers probablement tronqués |
| Routeur open-set | `agent5_router_open_set_20261104T145601Z` | Rejet inconnus 20/20, faux rejet 3/46 ; IC Clopper-Pearson | Retirer « couverture 0,903 » |
| Corrélation | `agent5_correlation_20261104T141916Z` | Original TP 13 FP 4 FN 2 ; agrandi P 0,9884, R 0,5973 ; fenêtre seule P ≤ 0,23 | Corpus synthétique |
| Multi-format | `agent5_multiformat_20261104T150111Z` | 7 001 = test d'intégration ; champs 0/7 pour flux tabulaires | Pas de corpus Apache réel local |
| Isolation Forest CICIDS2017 | `agent6_cicids_iforest_20261104T141904Z` | F1 0,116 (seuil bénin) / 0,521 (seuil F1 val) vs LR 0,557 | Évaluation réseau = classification supervisée |
| Bibliographie | — | 28 → 39 références vérifiées : `agent_6/references_proposees.bib` | |
| Utilité, IA, publication | — | `agent_7/latex/spec_utilite.tex`, `declaration_ia.tex`, `limites_consolidees.tex`, `public_release/` | `limites_consolidees.tex` contient d'**anciens chiffres** : à mettre à jour (conflit A6) |

## 4. Décisions finales

- **D1 Titre** : titre ajusté adopté : « Architecture multi-agents légère pour l'analyse de journaux système et réseau hétérogènes — Conception et évaluation en laboratoire d'Ariel Logminer ».
- **D2 Emplacement des preuves** : artefacts publics copiés dans `experiments/phase_revision_20261104/` ; manifeste SHA-256 de 54 fichiers vérifié sans erreur.
- **D3 Lingala** : chiffres et formulations directement vérifiables mis à jour, sans réécriture linguistique extensive non validée.
- **D4 Déclaration IA** : déclaration factuelle complétée dans `frontmatter/declaration_ia.tex`, sans champ en attente ni donnée personnelle ajoutée aux preuves publiques.

## 5. Procédure d'intégration (une fois D1–D3 tranchées)

1. Appliquer les arbitrages de `INTEGRATION_CONFLICTS.md` §A et §B. Ordre du cahier : chapitres 4 et 5 du PDF (fichiers `chapitre4_implementation.tex`, `chapitre5_resultats.tex`), puis 1, 2, 3, 6, 7, introduction, résumés (`main.tex`), annexes.
2. Correspondance fichiers / numérotation PDF : voir `agent_7/PATCH_NOTES.md`, section « Correspondance fichiers / numérotation du PDF ». La conclusion (`chapitre6_conclusion.tex`) est incluse après le chapitre 7 : d'où 7.11–7.17 (correctif de l'agent 1, §11).
3. Échapper chaque `%` après un nombre (`89,8081\,\%`, `main.tex:328` et équivalents EN/lingala).
4. Bibliographie : fusionner `agent_6/references_proposees.bib` dans `ARIEL_LOGMINER_MEMOIRE_FINAL/references.bib` (style `plain`, bibtex).
5. Matrice A.2 (`chapters/annexes.tex`) : une ligne par run_id du §3.
6. Compiler dans `ARIEL_LOGMINER_MEMOIRE_FINAL/` : `pdflatex main` → `bibtex main` → `pdflatex main` ×2 (MiKTeX installé). Corriger références non résolues, labels dupliqués, débordements.
7. Contrôle : grep de chaque nombre clé (0,868373, 0,892308, 0,913698, 0,157744, 0,233670, 451, 1 349, 0,499291, 20/20, 3/46…) dans `main.tex` et `chapters/*.tex` ; tout doit être identique et rattaché à un artefact.
8. PR-AUC HistGradientBoosting tracée vers `table_cicids_model_candidates.md` et harmonisée à 0,569002.
9. Après modification de code éventuelle : `graphify update .`.
10. Livrable final pour l'auteur : rapport court (modifications, expériences et résultats y compris contradictoires, points ouverts, questions).

## 5bis. Suivi de l'intégration (cocher au fil de l'eau)

Chaque ligne = un lot appliqué, compilable. Après chaque lot : compiler (`pdflatex -interaction=nonstopmode main`), cocher ici, noter le dernier fichier touché.

- [x] L1 Échappement des `%` après un nombre (trois résumés + chapitres)
- [x] L2 Conclusion : sections étoilées + `\addcontentsline` (agent 1 §11)
- [x] L3 BGL « fenêtre » → « événement » (ch. 4 l. 78, ch. 5 l. 35 et l. 167)
- [x] L4 Sous-section formelle Histogram (agent 2 §1)
- [x] L5 Section HDFS du ch. 5 avec le test complet (agent 2 §3) ; run_id cités sans chemin
- [x] L6 BGL : règle de sévérité + second protocole (agent 4 P-5.2 à P-5.4, agent 6 P13)
- [x] L7 IDS2018 : raccourci Dst Port, RF 0,40 (agent 4 P-5.5 à P-5.8)
- [x] L8 Routeur, corrélation, multi-format (agent 5 D.8 à D.16)
- [x] L9 Distribution : HDFS 2 VM, endurance, saturation, panne appariée (agent 3)
- [x] L10 Isolation Forest et baselines publiées (agent 6 P16, P17 avec 0,868373) ; ajout de la référence `le2022logbased`, compilation LaTeX en trois passes sans citation ni référence indéfinie
- [x] L11 Chapitres 1–2 : hypothèses falsifiables (agent 1 §9), références et Contract Net/FIPA (agent 6 P1–P12, P19) ; H2 reformulée autour de l'idempotence, H3 conserve son comparateur sans routage ; correspondance FIPA explicitée sans revendication de conformité
- [x] L12 Chapitre 3 : spécification de l'utilité (agent 7 C.1–C.4) ; définition des six composantes, règles de refus, simplification de la formule, rôle de classement, score de poursuite d'objectif et correction de la sémantique de `FEEDBACK`
- [x] L13 Section unique des limites mise à jour + renvois (agent 7 B, conflit A6) ; chiffres HDFS complet, routeur étendu, saturation et panne appariée consolidés
- [x] L14 Tableau 7.1 des hypothèses (arbitrages A2, A3) ; structure à quatre colonnes, H2 partiellement soutenue par l'idempotence, H3 et H5 non tranchées
- [x] L15 Résumés FR/EN/lingala harmonisés avec HDFS complet, routeur étendu et PR-AUC tracée
- [x] L16 Titre ajusté adopté et propagé aux métadonnées PDF
- [x] L17 Bibliographie fusionnée (39 références) et déclaration IA factuelle complétée
- [x] L18 Matrice A.2 actualisée ; preuves publiques et manifeste SHA-256 ajoutés
- [x] L19 Compilation complète (`pdflatex`, `bibtex`, deux passes `pdflatex`) puis passes de finition ; PDF de 165 pages, sans référence/citation indéfinie, erreur fatale, avertissement de relance ni débordement horizontal
- [x] L20 Rapport final remis à l'auteur

État final : `ARIEL_LOGMINER_MEMOIRE_FINAL/main.pdf` contient 165 pages. Les trois résumés, le titre, la déclaration IA, la matrice de traçabilité, la spécification de l'utilité, les limites consolidées et les résultats expérimentaux sont harmonisés. `git diff --check` passe ; le journal LaTeX ne contient ni référence/citation indéfinie ni débordement horizontal. Les 54 entrées du manifeste public correspondent aux fichiers et à leurs empreintes SHA-256.

## 5quinquies. Nouveau chantier de révision (2026-11-05) — PRIORITAIRE

Un nouveau chantier, à huit agents, a été lancé par l'auteur après le retour de trois lecteurs. **Son état fait foi : `revision_reports/chantier_20261105/ETAT_CHANTIER.md`**, et sa mission est dans `MISSION.md`, au même endroit. Les agents ne modifient pas les `.tex` directement (décision C1).

Reprise Codex du 2026-11-05 : les livrables des Agents 1 et 2 ont été retrouvés ; le lot A2-a (question centrale et QR, nature des preuves, hypothèses et règles de décision, objectif, réponses QR, tableau 7.1 et alignements du chapitre 2) a été intégré. Compilation complète réussie : `main.pdf`, 170 pages, aucune erreur, référence/citation indéfinie ni boîte horizontale débordante. Les Agents 3, 4 et 6 ont été réactivés en parallèle ; l'Agent 5 reste séquencé après le livrable 4. Le détail courant reste dans `chantier_20261105/ETAT_CHANTIER.md`.

Reprise du 2026-11-05 : E-H3b est terminé et son manifeste valide 17 entrées ; la non-infériorité des modèles spécialisés n'est pas établie sur `linux_auth` (borne inférieure de l'IC à 95 % : −0,012326, marge : −0,01). E-H3 n'est pas faisable avec les sources locales : les 68 chemins du test open-set ont déjà été utilisés, et les candidats indépendants restants sont au plus 45 pour les 90 requis. E-H4 est terminé ; le manifeste complet valide 8 entrées. Histogram obtient un F1 moyen de 0,868373, sous la baseline de surprise moyenne des templates (0,872434) ; le critère préenregistré n'est pas satisfait et le résultat est dominé par la règle simple. Les écarts techniques des tentatives intermédiaires sont consignés dans `PROTOCOLES_PREENREGISTRES.md`, sans métrique issue d'une tentative échouée. Les résultats et leurs limites ont été intégrés aux chapitres 5 à 7, à la conclusion, aux annexes et au livrable de l'Agent 4. La déclaration IA est actualisée. Le cycle `pdflatex`–`bibtex`–`pdflatex` × 2 réussit ; le PDF final compte 175 pages, sans citation/référence indéfinie ni boîte horizontale débordante. `latexmk` n'est pas utilisable dans cet environnement faute de Perl ; la compilation directe fonctionne. `graphify update .` a également été exécuté après la correction du runner. L'état et la suite du chantier sont suivis dans `chantier_20261105/ETAT_CHANTIER.md` ; l'Agent 5 est actif pour préparer E-H5 et E-CNP.

Reprise de l'Agent 5 : les fichiers de passation, la mission et les trois retours de lecteurs ont été relus. Aucun nouveau protocole ni aucune expérience n'est encore exécuté. Le code confirme que la mémoire utilise un lissage de Laplace et n'est mise à jour qu'en mode actif ; Contract Net trie les offres par utilité puis par identifiant d'agent, tandis que le benchmark fournit des charges appariables par graine et des profils de confiance pré-déclarés. La suite est de figer les runners et critères d'E-H5/E-CNP, puis de committer chaque protocole avec le registre conformément à C13-proc, avant exécution. Ne pas modifier les `.tex` ; déposer les propositions dans `agent_5/sections/`. Au contrôle final, vérifier le bloc de passation manquant et les fragments Agent 4.

Reprise Claude Code du 2026-11-05 : le travail de Copilot a été audité. Les expériences E-H3b et E-H4 sont fiables (manifestes valides, rejeux identiques à l'octet) ; le statut « Agent 4 COMPLET » était surévalué et quelques erreurs du manuscrit ont été corrigées. Agent 5 terminé : E-H5 (`658e639`) donne un gain de mémoire conditionnel (p = 0,9), d'où H5 NON TRANCHÉE par règle préfixée ; E-CNP (`472d5e7`) donne un avantage conditionnel, sans isoler la négociation de la prise en compte de la charge. Lot A5-a intégré ; `main.pdf` : 181 pages, compilation propre. **La suite, les restes de l'Agent 4 et les questions à l'auteur sont dans `chantier_20261105/ETAT_CHANTIER.md` : audit, « Prochain agent à activer » et « Questions à l'auteur ».** **Mise à jour : E-H3b a deux défauts découverts ensuite (fuite de l'étiquette sur UNSW, CICIDS réduit aux DDoS) et n'est plus retenue ; E-H3B-STRICT-HOLDOUT la remplace. E-CNP-LEAST-LOADED conclut à l'absence d'avantage de la négociation. Lot A5-b intégré.** Script source corrigé après coup ; pour rejouer E-H3b ou sa version stricte à l'identique, partir du commit `27deb22` (voir le registre). Prochain : restes de l'Agent 4, puis Agent 7, puis Agent 8. Dans les commandes Bash de cet environnement, éviter les heredocs de texte français contenant des apostrophes et écrire plutôt les fichiers avec l'outil dédié.

## 5quater. Mise à jour des figures (2026-11-05)

Demande de l'auteur : « Mets à jour les graphiques qui sont dans la rédaction ». **Terminé et compilé** (165 pages, 0 erreur, 0 référence indéfinie, 0 débordement).

- Script : `ARIEL_LOGMINER_MEMOIRE_FINAL/revision_reports/generate_final_scientific_figures.py`. Fonctions `hdfs_bgl_figures` et `routing_and_pipeline_figures` réécrites pour lire `experiments/phase_revision_20261104/` ; option `--only <groupes>` ajoutée. **Ne pas relancer sans `--only`** : les schémas `fig_architecture_multi_agent_global.png` et `fig_contract_net_sequence.png` ont été retouchés à la main après la génération (22–23 sept.) et seraient écrasés.
- Commande : `.venv-hdfs-bgl\Scripts\python.exe ARIEL_LOGMINER_MEMOIRE_FINAL/revision_reports/generate_final_scientific_figures.py --only hdfs_bgl routing`
- Figures régénérées (6) : `fig_hdfs_event_vs_block` (test complet : événement 0,204 ; bloc max/ratio 0,719 ; moyenne 0,868), `fig_hdfs_bootstrap_distribution` (test complet 20 000 réplications contre échantillon 2 000 blocs ; le script reproduit l'IC publié et le vérifie par assertion), `fig_bgl_known_unknown`, `fig_bgl_histogram_vs_unknown_baseline` (ajout de la règle de sévérité), `fig_router_open_set_tradeoff` (66 fichiers, assertions 20/20 et 3/46), `fig_multiformat_coverage_by_source` (second panneau : champs complets sur 7).
- Légendes du ch. 5 et paragraphes de l'annexe A (figures) mis à jour ; la couverture 0,903 et le 0,892308 « bloc » ont disparu de l'annexe.
- Anciennes images : copie dans le scratchpad de la session (non pérenne) ; sinon `git show HEAD:ARIEL_LOGMINER_MEMOIRE_FINAL/figures/final/<nom>.png`.
- Figures inchangées car toujours cohérentes avec le texte : CICIDS2017, CSE-CIC-IDS2018 (protocole principal), A–D, E2E.
- **Ajout, sur demande de l'auteur** : groupe `--only revision_distribution` → `fig_paired_failure_abcd.png` (fig. 4.15, `fig:panne-appariee`, après le tableau de la panne appariée) et `fig_saturation_multivm.png` (fig. 4.18, `fig:saturation-multivm`, fin de la sous-section Saturation) ; paragraphes d'annexe ajoutés. PDF : 166 pages, compilation propre.
- **Corrections de chiffres faites en passant (règle 2)** : la saturation compte **11 430** tâches soumises (11 427 réussies, 3 échecs), et non 10 080 (erreur reprise du PATCH_NOTES de l'agent 3) — corrigé dans ch. 5, matrice A.2 et `limites_consolidees.tex`. Latence médiane ≤ 8 t/s : 0,06–0,22 s (le texte disait « < 0,2 s », faux pour r2_rate1 = 0,215 s). Ubuntu : 143 attributions, 140 réussies (1,23 %), les 3 échecs sont tous les siens.

## 5ter. Prompt de reprise pour Codex

> La révision finale est terminée. En cas de reprise, ne modifier le mémoire que pour une nouvelle demande explicite de l'auteur ; préserver les choix consignés au §4 et vérifier le PDF par une compilation complète après toute modification.

## 6. Environnement et pièges

- Python : `.venv\Scripts\python.exe` (général, redis) ; `.venv-hdfs-bgl\Scripts\python.exe` (drain3, scipy, pandas). Mettre `PYTHONIOENCODING=utf-8`.
- Redis : conteneur Docker `logminer-redis`, port 6379 sur l'hôte.
- VM VirtualBox `Debian` (agent `debian-alpha`, `/home/vboxuser/.venv-logminer/bin/python`, Python 3.13) et `Ubuntu` (agent `ubuntu-beta`, `python3` système 3.8 — le venv Ubuntu n'a pas `redis`). Identifiants chiffrés DPAPI dans `.secrets/*_vm.credential.json`.
- **Debian n'a que l'interface host-only** (192.168.56.102) : URL Redis invitée = `redis://192.168.56.1:6379/0`, jamais `10.0.2.2`.
- SSH (plink, ports 2222/2223) ne fonctionne pas ; utiliser `VBoxManage guestcontrol`. **`guestcontrol run` bloque sur un processus détaché** : lancer les agents avec `guestcontrol start` (`revision_reports/agent_3/start_hdfs_agents.ps1`, déjà corrigé). Sur Ubuntu, VBoxManage renvoie souvent un code de sortie anormal même en cas de succès : vérifier par `pgrep` et le registre Redis.
- Les sessions Codex d'origine : `C:\Users\aoliv\.codex\sessions\2026\11\04\` (orchestrateur : `rollout-2026-11-04T11-10-43-*.jsonl`).
