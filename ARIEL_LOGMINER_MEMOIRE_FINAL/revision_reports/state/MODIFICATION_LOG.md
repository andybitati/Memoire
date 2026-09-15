# Modification log

## 2026-09-09 — Dataset strengthening, phase 0

- Cahier de mission dataset lu intégralement.
- Code, configurations, manifestes, sources locales et limitations existantes audités.
- `docs/DATASET_STRENGTHENING_GAP_ANALYSIS.md` créé.
- Aucun chapitre LaTeX et aucun ancien résultat modifiés.
- Aucune nouvelle expérience exécutée avant la clôture de l’audit.

## 2026-09-09 — Audit d'intégration dans le mémoire

- État des chapitres contrôlé sans réécriture du manuscrit.
- Écart confirmé entre l'ancienne campagne à 525 ACK / le benchmark à 60 tâches et les
  nouveaux résultats Contract Net.
- Stratégie d'intégration enregistrée dans
  `revision_reports/MULTI_AGENT_RESULTS_INTEGRATION_AUDIT.md`.
- Répertoire obligatoire des prochaines compilations fixé à
  `E:\Cours\TFE\ARIEL_LOGMINER_MEMOIRE_FINAL`, avec sortie sous `build/`.
- `COMPILATION.md` corrigé pour privilégier la chaîne directe MiKTeX tant que Perl n'est pas
  disponible pour `latexmk`.

## 2026-09-09 — Clôture Redis inter-processus et multi-VM

- `RedisContractNetTransport`, `RedisContractNetCoordinator` et `RedisIdempotencyStore` ajoutés.
- Trois processus agents locaux validés dans `redis_cnp_20260909T162814Z_47940` : 60/60 tâches et replay sans doublon.
- Mot de passe Ubuntu réinitialisé après création du snapshot `pre-password-reset-20260909`; accès `andy` vérifié.
- Identifiants Debian et Ubuntu stockés sous chiffrement DPAPI dans `.secrets/`, exclu de Git.
- Adaptateur host-only ajouté aux deux VM; Redis reste sur l'hôte Windows du laboratoire.
- Campagne définitive `multivm_cnp_20260909T202632Z_37592` : Debian et Ubuntu, 60/60 tâches, 30/30, 15 refus explicites, un échec contrôlé, une réattribution et zéro effet dupliqué.
- Rapport final et architecture mis à jour; aucune revendication de haute disponibilité ou d'usage industriel.

## 2026-09-09 — Compilation locale MiKTeX

- Détection de MiKTeX 25.12 et de `pdflatex.exe`, `latexmk.exe`, `bibtex.exe`.
- Mise à jour de l'index MiKTeX permettant la détection de `french.ldf`.
- Constat : `latexmk.exe` exige Perl, absent de la machine.
- Première compilation directe pdfLaTeX effectuée.
- Correction d'une référence d'image absente dans `chapters/annexes.tex`.
- PDF intermédiaire généré : 293 pages.
- Étape suivante enregistrée : BibTeX depuis `build/`, puis deux passes pdfLaTeX.
- Tous les processus de travail arrêtés à la demande de l'utilisateur.

## L0–L19

Copie autonome créée à partir du projet LaTeX final. Les corrections portent sur la structure de l'introduction/conclusion, l'exclusion du score historique non traçable, la qualification des campagnes multi-VM comme preuve de laboratoire et l'intégration des preuves de traçabilité Phase 13A. Aucune expérience n'a été relancée.

## 2026-09-09 — Architecture multi-agents autonome légère

- Audit préalable écrit dans `docs/MULTI_AGENT_GAP_ANALYSIS.md`.
- Noyau Contract Net et registre d'idempotence ajoutés.
- `AgentMessage` conservé avec sept champs.
- Sept tests unitaires ajoutés et réussis.
- Deux smoke tests conservés; le premier documente un échec de séparateur, le second valide la correction.
- Un premier run complet conservé mais non retenu, car l'accumulation des latences biaisait la RSS.
- Run corrigé retenu : `ma_20260909T154523Z_13604`.
- 160 runs principaux et 264 000 tâches exécutés sans échec.
- Adaptation, reprise post-traitement/pré-ACK et pipeline 6/6 exécutés.
- Dix figures et un manifeste SHA-256 produits.
- Rapport final écrit sans modification des chapitres du mémoire.
