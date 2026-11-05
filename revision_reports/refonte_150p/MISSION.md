# Mission de l'auteur (2026-11-05), texte intégral

Rôle et objectif
Tu es un assistant de révision scientifique chargé de produire un plan de refonte structuré du mémoire « Architecture multi-agents légère pour l'analyse de journaux système et réseau hétérogènes — Ariel Logminer » (FP/UNIKIN, 2025–2026), à partir des deux rapports de lecture (Lecteur 1 : 12,50/20 ; Lecteur 2 : 9,25/20).

Contrainte de volume : réduire de 180 à ~150 pages, en supprimant la redondance et le matériel non essentiel, sans diluer ni contourner l'idée principale (conception et évaluation critique d'une architecture multi-agents pour l'analyse de journaux). Aucune nouvelle revendication de supériorité ne doit être ajoutée ; le travail reste une étude expérimentale critique d'intégration et d'orchestration.

Méthode : mobiliser des agents spécialisés distincts (un par axe de critique), chacun produisant des correctifs précis, localisés et traçables. Puis un agent d'intégration fusionne les sorties en un plan cohérent de 150 pages.

## Agents à déployer (un par problème soulevé)

### Agent A — « Resserrement de l'objet scientifique »
Traite : problématique descriptive (L2 §2.1), hypothèses tautologiques H1/H2 (L2 §2.1 ; L1 §A.1–A.2), H3–H5 non opérationnalisées (L1 §A.3 ; L2 §2.1), non-correspondance QR/hypothèses (L2 §2.1), titre surestimé (L2 §2.1, §4).
Livrables :
- Reformulation de la question centrale en thèse falsifiable (opposer deux explications concurrentes).
- Requalification de H1/H2 en exigences de réalisation (hors hypothèses scientifiques) ; H3–H5 dotées de grandeurs fixées a priori (taux d'exécutions incompatibles, budget ressources, métrique de priorisation).
- Tableau unique QR ↔ hypothèse ↔ mesure ↔ statut ; suppression de QR4 ou rattachement explicite.
- Proposition de titre et conclusion recadrés (retirer « hétérogènes » au sens multi-source ; requalifier « intelligents »).

### Agent B — « Rigueur expérimentale et comparateurs manquants »
Traite : modèles battus par règles simples (L1 §B.1 ; L2 §2.2), spécialisation non généralisable (L1 §B.2), benchmark micro-tâches non pertinent (L2 §2.2), comparateurs H2/H3 non exécutés (L2 §2.2, §3), seuils par défaut / échantillons plafonnés (L2 §2.2), Contract Net sans avantage (L1 §C.1), mémoire à gain conditionnel extrême (L1 §C.2), distribution non démontrée (L1 §C.4 ; L2 §2.2).
Livrables :
- Expériences à exécuter ou à requalifier explicitement comme non faites : chaîne sans routage (H3), agents sans idempotence (H2), tâches d'inférence réalistes pour le benchmark A–D.
- Protocole de calibration des seuils ; justification ou suppression du plafonnement des échantillons ; correction de la pondération du scénario Infiltration.
- Requalification de H4 en « non validée, composante de supériorité infirmée » ; suppression de tout budget rétroactif.
- Analyse causale des pertes de tâches sous Contract Net (L1 §C.3) ; explicitation du biais du comparateur « moindre chargé » (accès direct à l'état, sans coût de communication).

### Agent C — « Intégrité des données et validité interne »
Traite : contamination E-H3b (L1 §B.3 ; L2 §2.2), CSE-CIC-IDS2018 possiblement tronqué (L2 §2.2), CICIDS2017 non corrigé utilisé en connaissance de cause (L2 §2.2), absence d'audit des autres campagnes (L2 §2.2, §3), recherche à chemins multiples sur BGL (L2 §2.2), HDFS/graines fictives (L2 §2.2), préenregistrement auto-certifié (L1 §E.2 ; L2 §2.2).
Livrables :
- Audit systématique du pipeline de préparation + tests automatisés empêchant la fuite de la cible.
- Vérification des fichiers CSE-CIC-IDS2018 contre la distribution officielle, ou retrait de la section 4.6 et des conclusions H4 qui en dépendent.
- Requalification ou retrait du protocole BGL principal et du protocole G (conçu après lecture du test) ; documentation des variantes exploratoires comme telles.
- Traitement honnête du préenregistrement : limiter l'affirmation aux campagnes concernées, ne pas prétendre à un préenregistrement global ; vérifier l'antériorité réelle des commits.
- Correction des graines HDFS (matrice de confusion identique → pas d'observations indépendantes).

### Agent D — « Cadre théorique, originalité et positionnement »
Traite : catalogue de manuel (L2 §2.3), littérature d'allocation/équilibrage absente (L2 §2.3), détecteur Histogram sans référence (L2 §2.3), jeux de données non cités (L2 §2.3 ; §4), originalité limitée (L1 §D ; L2 §2.6), résultats injectés dans l'état de l'art (L2 §2.4).
Livrables :
- Sections à supprimer (LOF, One-Class SVM, Extra Trees non utilisés) et références à ajouter (power of two choices, JSQ, MAS récents pour SOC/IDS, Moustafa & Slay, Linux/auth, Solaris BSM, DARPA 1998).
- Rattachement du détecteur Histogram à une filiation explicite (score de rareté fréquentielle naïve).
- Recadrage de la contribution : étude expérimentale critique d'intégration/orchestration sous contraintes de laboratoire — pas de nouveauté algorithmique revendiquée.
- Nettoyage du chapitre 1 : retirer les résultats et anticipations (renvois vers §4.2, tableau 1.6) pour rétablir la frontière cadre/constats.

### Agent E — « Forme, redondance et lisibilité »
Traite : redondance massive (L2 §2.5), résumé illisible / bokuse divergent (L2 §2.5), jargon d'identifiants internes (L2 §2.5), précision numérique incohérente (L2 §2.5), tableaux illisibles (L1 §F ; L2 §2.5), bibliographie web sans DOI (L2 §2.5), fragmentation des chapitres 1–2 (L1 §F).
Livrables :
- Cartographie des suppressions pour atteindre 150 p. (cibles : chapitre 7 et annexe A.3 redondants avec ch. 4–5 ; répétitions de chiffres ; 26+26 sections à rationaliser).
- Résumé unique et lisible ; alignement bokuse/résumé/abstract ; suppression des intervalles divergents.
- Remplacement des identifiants internes (agent4_bgl_second_protocol_…) par des étiquettes lisibles ; harmonisation de la précision numérique ; refonte des tableaux 1.4, 1.5, 7.1.
- Bibliographie : DOI, dates de consultation cohérentes, suppression des doublons Sharafaldin.

### Agent F — « Autonomie, paternité et reproductibilité »
Traite : déclaration IA accablante et calendrier des campagnes (L2 §2.7), absence de dépôt accessible (L2 §2.7, §4), apport personnel invérifiable (L2 §2.7), reproductibilité non certifiée (L1 §E.3).
Livrables :
- Dosage de l'aveu d'IA : conserver la déclaration honnête, mais préciser la répartition réelle entre conception étudiante, assistance à l'écriture de scripts et exécution automatisée ; ne pas laisser le calendrier suggérer une délégation intégrale des conclusions.
- Exigence d'un dépôt accessible (URL/archive/DOI) avec code, scripts, configurations, manifestes, graines, partitions ; à défaut, identifier explicitement ce qui reste invérifiable.
- Préparation d'une annexe de défense : justification par l'étudiant des protocoles E-H5, E-CNP, E-CNP-LL, de la fonction d'utilité et du découpage HDFS/BGL.

### Agent d'intégration — « Plan de refonte 150 pages »
Fusionne les livrables A–F en un plan chapitre par chapitre indiquant, pour chaque section : Action (conserver / réviser / fusionner / supprimer / ajouter) ; Justification (renvoi précis au reproche, L1 ou L2, section) ; Impact volume (pages gagnées/perdues, objectif net : −30 p.) ; Risque (ce qui affaiblirait l'idée principale si mal exécuté).

Règles d'intégration non négociables :
- Ne pas effacer les résultats négatifs ni remplacer les hypothèses par des affirmations favorables (L1 §5).
- Ne pas introduire de revendication de supériorité non démontrée.
- Maintenir la distinction propriétés implémentées / testées / effectivement supérieures (L1 §F), aujourd'hui dispersée entre ch. 4–7 : la concentrer en une section unique de synthèse.
- Toute expérience non exécutée doit être déclarée comme telle, jamais comblée par une inférence.

## Format de sortie attendu
1. Tableau de bord des 8 faiblesses critiques (L1 §4) et des points de non-recevabilité (L2 §4) → agent responsable → correctif → statut.
2. Plan de 150 pages (structure cible, sections supprimées/fusionnées, ajouts).
3. Liste des expériences à exécuter avant soutenance (H2, H3, benchmark réaliste) avec critères de succès fixés a priori.
4. Liste des corrections formelles et bibliographiques.
5. Note de dosage de l'aveu d'IA : formulation proposée, factuelle et non auto-accablante, distinguant assistance technique et apport intellectuel.
6. Checklist de conformité : chaque reproche L1/L2 est adressé ou explicitement accepté comme limite résiduelle.

Remarque de l'auteur : « On va doser un peu cet aveu d'IA. »
