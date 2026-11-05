# LIVRABLE 6 — Reproductibilité, artefacts et déclaration IA

## 1. Périmètre traité

Ce livrable couvre le chapitre 7, l'annexe A, la déclaration relative à l'usage d'outils
d'IA, les artefacts des campagnes `agent2` à `agent6`, le point C5 sur la reproductibilité
indépendante et la suppression transférée du §7.7 consacré à pdfLaTeX. Aucun fichier `.tex`
du manuscrit n'a été modifié ; les passages prêts à intégrer sont dans `agent_6/sections/`.

Sources principales :

- `revision_reports/chantier_20261105/RETOURS_LECTEURS.md`, lecteur 1 E.2--E.3 et
  lecteur 2 §2.3, point de non-recevabilité D ;
- `ARIEL_LOGMINER_MEMOIRE_FINAL/frontmatter/declaration_ia.tex` ;
- `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/chapitre7_reproductibilite_deploiement.tex` ;
- `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/annexes.tex` ;
- `revision_reports/agent_2/` à `revision_reports/agent_6/`, notamment leurs
  `PATCH_NOTES.md`, scripts et artefacts ;
- `experiments/phase_revision_20261104/README.md` et `MANIFEST_SHA256.csv`.

## 2. Diagnostic

### 2.1 Traçabilité présente, reproduction indépendante non établie

Le dépôt local fournit une traçabilité substantielle : identifiants de campagne, résultats
CSV/JSON, scripts de contrôle et paquet de 54 fichiers muni d'un manifeste SHA-256. Le
`HANDOFF.md` rapporte une vérification sans erreur des 54 empreintes. Cette situation permet
de contrôler l'intégrité et de recalculer plusieurs valeurs.

Elle ne suffit pas à certifier une reproductibilité indépendante :

- aucun rapport d'exécution par un tiers n'est disponible ;
- le plan de dépôt public `revision_reports/agent_7/public_release/PUBLIC_RELEASE_PLAN.md`
  se présente explicitement comme une proposition et aucun DOI stable n'est renseigné ;
- le paquet `phase_revision_20261104` contient les sorties, mais les scripts des campagnes
  complémentaires restent principalement sous `revision_reports/agent_2` à `agent_6` ;
- plusieurs entrées brutes ne sont pas redistribuées et dépendent de chemins ou de jeux
  locaux ;
- les campagnes multi-VM dépendent d'une topologie VirtualBox/Redis et de secrets exclus
  des artefacts, ce qui impose une procédure de reconstruction documentée.

Conclusion rédactionnelle retenue : distinguer explicitement traçabilité, répétabilité et
reproductibilité indépendante ; ne revendiquer que les deux premiers niveaux.

### 2.2 Campagnes exécutées avec assistance IA

L'inventaire demandé par le lecteur 2 et la mission comporte neuf groupes :

| Groupe | Identifiants principaux | Script ou dossier de preuve |
|---|---|---|
| HDFS principal, test complet | `agent2_hdfs_full_20261104T131314Z`, réplication `…T134240Z` | `revision_reports/agent_2/` ; `experiments/phase_revision_20261104/agent_2_hdfs/` |
| BGL | `agent4_bgl_second_protocol_20261104T142629Z`, `agent4_bgl_contiguous_horizon_20261104T145740Z` et diagnostics associés | `revision_reports/agent_4/scripts/`, `artifacts/bgl/` |
| Audit CSE-CIC-IDS2018 | `agent4_csecic_shortcut_20261104T144738Z` | `revision_reports/agent_4/scripts/csecic_shortcut_audit.py` |
| Routeur open-set étendu | `agent5_router_open_set_20261104T145601Z` | `revision_reports/agent_5/scripts/agent5_router_open_set_extended.py` |
| Panne appariée H2 | `agent3_paired_failure_abcd_20261104T141803Z` | `revision_reports/agent_3/run_paired_failure_abcd.py` |
| Saturation multi-VM | `agent3_saturation_multivm_20261104T142325Z` | `revision_reports/agent_3/run_saturation_multivm.py` |
| Détection HDFS distribuée | `hdfs_multivm_cnp_20261104T135345Z` | `revision_reports/agent_3/run_hdfs_multivm.py` et scripts d'agent |
| Isolation Forest de contrôle | `agent6_cicids_iforest_20261104T141904Z`, agrégation `agent6_strict_e3_aggregate_20261104T143019Z` | `revision_reports/agent_6/scripts/` |
| Corrélation étendue | `agent5_correlation_20261104T141916Z`, sensibilité `…T143159Z` | `revision_reports/agent_5/scripts/agent5_correlation_*.py` |

La répartition précise entre éléments préexistants de l'auteur, automatisation et questions
de maîtrise figure dans `PREPARATION_SOUTENANCE.md`, conformément à C4(d). Elle n'est pas
introduite dans le manuscrit.

### 2.3 Préenregistrement

Les campagnes ci-dessus ne peuvent pas être décrites comme préenregistrées. Le dépôt ne
contient pas de document indépendant, versionné avant leur exécution, qui fixe les
comparateurs, métriques et critères. Le fait qu'un script écrive `protocol.json` avant sa
phase d'évaluation ne suffit pas : le protocole et le script ont été conçus dans le même
cycle d'assistance.

La déclaration et le chapitre 7 proposés utilisent donc la règle suivante : seul un
document horodaté et versionné avant l'exécution permet d'employer le terme
« préenregistré ». Les expériences décidées sous C13 suivent désormais cette procédure,
mais elles ne rendent pas rétroactivement préenregistrées les campagnes listées ici.

### 2.4 Déclaration IA actuelle

Le texte actuel affirme que les outils « n'ont pris aucune décision autonome sur les
protocoles », puis reconnaît seulement une « exécution de campagnes complémentaires ».
Cette formulation est trop étroite au regard des scripts, rapports et propositions de
protocoles produits avec l'assistance de Claude Code. Elle expose le mémoire au point D du
lecteur 2.

Le remplacement proposé déclare explicitement : proposition et mise en œuvre de protocoles
complémentaires, écriture ou adaptation de scripts, exécution, agrégation et préparation de
corrections. Il conserve la responsabilité finale de l'auteur sans attribuer à celui-ci une
conception humaine non assistée qui n'est pas démontrée. Le texte reste factuel et ne raconte
pas l'historique des tentatives, conformément à C4(b).

### 2.5 Annexe A : incohérence d'artefact

La ligne « BGL, protocole contigu G » de la matrice pointe actuellement vers
`agent4_bgl_second_protocol_20261104T142629Z__result.json`. Ce fichier contient R0 et les
variantes B--E, pas G. L'artefact correct est :

`revision_reports/agent_4/artifacts/bgl/agent4_bgl_contiguous_horizon_20261104T145740Z__result.json`.

Une ligne corrigée est fournie. Cet artefact n'apparaît pas dans le manifeste public actuel ;
le coordinateur doit soit le copier dans le paquet stable puis régénérer le manifeste, soit
conserver le chemin complet vers `revision_reports`. Il ne faut pas laisser la ligne actuelle.

## 3. Corrections prêtes à intégrer

### 3.1 Déclaration IA

Fichier : `sections/declaration_ia.tex__remplacement_integral.tex`.

Effets :

- supprime l'affirmation inexacte selon laquelle l'IA n'a pas contribué aux protocoles ;
- décrit les usages par outil, sans chronologie narrative ;
- précise que les valeurs viennent des artefacts et non de réponses générées ;
- retire toute revendication de préenregistrement des campagnes complémentaires ;
- distingue traçabilité et reproduction indépendante.

### 3.2 Chapitre 7

Fichier : `sections/chapitre7_reproductibilite_deploiement.tex__remplacement_integral.tex`.

Le remplacement complet :

- distingue traçabilité, répétabilité et reproductibilité indépendante ;
- documente le paquet de 54 artefacts et la portée du manifeste ;
- fournit une procédure de reproduction par campagne ;
- conserve les paramètres déterminants HDFS, BGL, CICIDS/CSE-CIC, routeur, corrélation et
  multi-VM ;
- indique que la campagne HDFS distribuée transporte des scores préalablement calculés ;
- formule la limite liée à l'absence de reproduction externe ;
- supprime intégralement l'ancien §7.7 « Compilation du mémoire » ;
- retire les contrôles purement éditoriaux sans portée scientifique.

### 3.3 Annexe A

Fichiers :

- `sections/annexes.tex__matrice_preuves_introduction.tex` : remplace l'introduction de la
  matrice, clarifie les chemins et la portée probatoire ;
- `sections/annexes.tex__ligne_bgl_protocole_G.tex` : corrige l'artefact de G.

## 4. Points laissés en suspens

1. **Archive stable.** Le coordinateur ou l'auteur doit décider si le dépôt remis sera
   public, privé au jury ou archivé avec DOI. Ne pas insérer d'URL ou de DOI non confirmé.
2. **Paquet complet.** Pour une reproduction externe, ajouter aux éléments remis les scripts
   des campagnes complémentaires, leurs configurations et l'artefact BGL G, puis régénérer
   un manifeste couvrant le paquet effectivement livré.
3. **Test tiers.** Une certification forte exige une reproduction par une personne qui n'a
   pas participé à la révision, avec publication des écarts d'environnement et de métriques.
4. **Plagiat.** Aucun plagiat ne peut être établi ou exclu à partir du seul PDF et du présent
   audit ; la déclaration d'IA ne doit pas être présentée comme une preuve de plagiat.
5. **Soutenance.** L'auteur doit relire et valider chaque fiche de
   `PREPARATION_SOUTENANCE.md`, puis recalculer au moins une métrique par groupe de campagne.

## 5. Contrôles effectués

- lecture des trois retours, de la mission, des décisions C1--C14 et des rapports de la
  révision précédente ;
- confrontation de la matrice A.2 au manifeste des 54 artefacts ;
- vérification des chemins de scripts et des identifiants dans les rapports `agent_2` à
  `agent_6` ;
- vérification rédactionnelle des sections proposées : aucune modification du manuscrit,
  aucun chiffre nouveau sans source, aucune revendication de reproduction indépendante ou
  de préenregistrement.

=== PASSATION ===
Agent : 6 — Reproductibilité, artefacts et déclaration IA
Statut : terminé
Livrables : `agent_6/LIVRABLE_6_reproductibilite.md` ; `agent_6/PREPARATION_SOUTENANCE.md` ; `agent_6/sections/declaration_ia.tex__remplacement_integral.tex` ; `agent_6/sections/chapitre7_reproductibilite_deploiement.tex__remplacement_integral.tex` ; `agent_6/sections/annexes.tex__matrice_preuves_introduction.tex` ; `agent_6/sections/annexes.tex__ligne_bgl_protocole_G.tex`
Prochain agent recommandé : Agent 7 — Forme, style et coquilles
Raison : le périmètre reproductibilité/IA est clos et le §7.7 est supprimé dans le remplacement complet ; l'Agent 7 peut nettoyer le reste du manuscrit sans toucher au chapitre 7.
Points de vigilance pour le repreneur : ne pas présenter les campagnes assistées comme préenregistrées ; ne pas revendiquer une reproduction indépendante ; corriger le chemin de l'artefact BGL G et régénérer le manifeste si cet artefact est ajouté au paquet stable ; ne pas réintroduire l'historique campagne par campagne dans le manuscrit.
=== FIN PASSATION ===

