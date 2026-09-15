# Audit d'intégration des résultats multi-agents

Date : 2026-09-09

## Conclusion de l'audit

Le manuscrit est déjà très avancé, structuré et prudent dans la formulation de ses limites.
La partie multi-agents est toutefois scientifiquement dépassée par les expériences exécutées
le 9 septembre 2026. Le résumé, le chapitre des résultats, la discussion, la reproductibilité,
la conclusion et les annexes utilisent encore principalement :

- le benchmark historique de 60 tâches (`1,6357` tâche/s contre `1,5715` tâche/s) ;
- la campagne Redis multi-VM `redis-vbox-1h-20260722153650`, qui établit 525 lectures/ACK,
  mais pas 525 succès métier ;
- l'affirmation qu'aucune ablation contrôlée de la mémoire n'est disponible.

Ces éléments ne sont pas faux dans leur protocole propre, mais ils ne doivent plus porter la
conclusion principale sur l'architecture multi-agents. Ils peuvent être conservés comme
résultats historiques ou exploratoires, de préférence en annexe.

## Résultats à retenir

### Architecture et protocole

- Implémentation d'un Contract Net léger : `CFP`, `PROPOSE`, `REFUSE`, `AWARD`, `REJECT`,
  `ACCEPT`, `RESULT`, `FAIL`, `FEEDBACK`.
- Utilité calculée localement par chaque agent ; le coordinateur diffuse, compare les offres
  et trace la décision.
- `AgentMessage` reste limité aux sept champs déjà décrits dans le mémoire. Les identifiants
  de contrat, tâche et idempotence ainsi que les composantes d'utilité sont placés dans
  `payload`. Les identifiants Redis restent dans l'enveloppe de transport.

### Campagne principale locale

- Run : `ma_20260909T160812Z_34016`.
- Architectures : A monolithe, B trois workers centralisés, C trois agents autonomes mémoire
  OFF, D trois agents autonomes mémoire ON.
- Charges : 100, 500, 1 000 et 5 000 tâches.
- Répétitions : 10 par architecture et charge, soit 160 runs.
- Volume : 264 000 traitements, aucun échec.
- Unité : microcharge déterministe de douze entiers ; elle mesure le coût d'orchestration et
  non la qualité d'une inférence de cybersécurité.
- Résultat central : le CNP autonome coûte nettement plus cher en débit et produit environ
  dix messages par tâche. Aucun gain systématique de débit dû à la mémoire n'est démontré ;
  les quatre intervalles appariés D-C contiennent zéro.

### Adaptation par mémoire

- 120 tâches en deux phases.
- Huit réattributions au début de la seconde phase ; elles cessent à l'index 67 lorsque
  l'utilité de gamma (`0,947776`) dépasse celle d'alpha (`0,946808`).
- Portée autorisée : la mémoire influence la décision d'allocation dans ce scénario contrôlé.
- Portée interdite : gain prédictif ou bénéfice général sur des journaux réels.

### Redis inter-processus

- Run : `redis_cnp_20260909T162814Z_47940`.
- Trois processus Python distincts sur un même hôte.
- 60/60 tâches réussies ; débit `23,958378` tâches/s ; p95 `59,871450` ms.

### Redis multi-VM retenu

- Run : `multivm_cnp_20260909T202632Z_37592`.
- Agents invités : Debian (`andy`, PID 2787) et Ubuntu (`andy-VirtualBox`, PID 4305).
- Redis 7.4.9 centralisé sur l'hôte Windows du laboratoire.
- 60/60 tâches réussies ; durée `2,712455` s ; débit `22,120187` tâches/s ; p95
  `63,029850` ms ; répartition 30/30.
- Quinze refus explicites et une réattribution après un échec contrôlé.
- Replay idempotent entre les deux VM : un effet persistant, aucun effet dupliqué.
- Portée autorisée : décision et exécution multi-agents sur deux VM de laboratoire.
- Portée interdite : haute disponibilité, déploiement multi-site, cloud, SOC réel ou
  généralisation industrielle.

### Reprise et chaîne bout en bout

- Harnais local après résultat persistant et avant ACK : un effet persistant, zéro doublon,
  une tâche récupérée, latence `0,004405` s, pending et lag finaux nuls.
- Pipeline `e2e-ma_20260909T160812Z_34016` : 8/8 étapes, une entrée Windows, aucune erreur
  ni fallback, latence `8,980957` s.
- Limite : aucun test multi-VM `XPENDING/XAUTOCLAIM` avec arrêt forcé après effet et avant ACK.
- Limite : le run bout en bout n'a qu'une entrée et ne porte aucune vérité terrain prédictive.

## Ordre d'intégration recommandé

1. Chapitre 3 : ajouter la définition opérationnelle du nouvel agent, le cycle Contract Net,
   la fonction d'utilité et la séparation entre coordinateur et décision locale. Réutiliser
   `docs/architecture/true_multi_agent_architecture.png` et
   `docs/architecture/contract_net_sequence.png`.
2. Chapitre 4 : documenter les modules `intelligent_runtime.py`, `contract_net.py`,
   `redis_contract_net.py` et `idempotency.py`, sans modifier le contrat à sept champs.
3. Chapitre 5 : remplacer le benchmark principal à 60 tâches par la matrice A/B/C/D ; ajouter
   ensuite l'ablation mémoire, l'adaptation, la reprise contrôlée, Redis inter-processus, le
   run multi-VM retenu et enfin le pipeline bout en bout.
4. Chapitre 6 de validité : séparer coût d'orchestration, décision adaptative, idempotence
   contrôlée et preuve de distribution. Maintenir explicitement les limites de mesure.
5. Discussion : reformuler H2 et H5 comme « partiellement soutenues, mais renforcées ».
   Conserver l'absence de gain de débit et de gain prédictif comme résultats négatifs.
6. Chapitre 7 : remplacer les anciennes commandes et identifiants de campagne par les trois
   runs retenus et leurs manifestes SHA-256.
7. Annexes : déplacer les détails exhaustifs, les tableaux par charge, les anciens runs
   Redis et les preuves de tentative échouée. Conserver le run 525 ACK comme preuve historique,
   clairement distincte du nouveau run CNP multi-VM.
8. Résumé, abstract et conclusion : mettre à jour en dernier, après stabilisation des chapitres
   3 à 7, pour éviter toute incohérence numérique.

## Sélection de figures

Le PDF issu de la première passe compte déjà 293 pages. Ne pas ajouter les dix figures de la
campagne dans le corps du mémoire. Retenir au plus :

1. l'architecture multi-agents réelle ;
2. la séquence Contract Net ;
3. le débit selon la charge ;
4. l'ablation mémoire ou l'évolution de l'utilité ;
5. la reprise/idempotence.

Les graphes CPU, RSS, équité, répartition et pipeline bout en bout peuvent être regroupés,
placés en annexe ou remplacés par un tableau synthétique.

## Artefacts de référence

- `MULTI_AGENT_FINAL_REPORT.md` ;
- `docs/TRUE_MULTI_AGENT_ARCHITECTURE.md` ;
- `experiments/phase_multi_agent/reports/ma_20260909T160812Z_34016__summary.md` ;
- `experiments/phase_multi_agent/reports/redis_cnp_20260909T162814Z_47940__redis_cnp.md` ;
- `experiments/phase_multi_agent/reports/multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm.md` ;
- `experiments/phase_multi_agent/manifests/` et le ledger append-only de la phase.

## État de compilation observé

- `build/main.pdf` existe, première passe pdfLaTeX, 293 pages.
- La bibliographie et les références ne sont pas stabilisées : `main.bbl` est absent et le log
  contient des citations et références indéfinies.
- Plusieurs avertissements d'accents en mode mathématique restent à corriger.
- Les prochaines commandes doivent être lancées depuis
  `E:\Cours\TFE\ARIEL_LOGMINER_MEMOIRE_FINAL`, avec sortie sous `build/`.
