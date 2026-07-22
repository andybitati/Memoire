# Prompt Pour Rediger Le Memoire Avec ChatGPT

Tu dois rediger un memoire de TFE a partir de ce dossier uniquement.

Sujet:

Detection Autonome et Distribuee d'Anomalies dans les Journaux Systemes et
Reseaux a l'aide d'Agents Intelligents Multi-Taches.

## Regles Obligatoires

1. Suivre en priorite le plan officiel:
   `01_plan_et_redaction/PLAN_DIRECTEUR_OFFICIEL.md`.
2. Utiliser `01_plan_et_redaction/plan.md` comme adaptation operationnelle du
   plan au prototype Logminer reel.
3. Utiliser `01_plan_et_redaction/pack_redaction_memoire.md` pour les contenus
   prets a inserer chapitre par chapitre.
4. Utiliser `01_plan_et_redaction/synthese_resultats_pour_memoire_articles.md`
   pour les resultats, interpretations et formulations mesurees.
5. Inserer les tableaux de `03_resultats_tableaux/` et les figures de
   `04_figures_png_pdf/` selon les chapitres.
6. Inserer les captures dashboard de `05_captures_dashboard/` dans le chapitre
   Implementation ou en annexe.
7. Ne pas inventer de chiffres. Les valeurs autorisees sont celles des tableaux,
   CSV, figures et documents de synthese.
8. Presenter les anomalies non supervisees comme des anomalies candidates, pas
   comme des attaques confirmees.
9. Ne pas presenter la baseline fail2ban-like comme fail2ban officiel.
10. Presenter Redis/MQTT comme extensions locales et perspectives de
    scalabilite, pas comme preuve de production SOC industrielle.

## Ordre De Redaction Conseille

1. Chapitre 3 - Modele propose.
2. Chapitre 4 - Implementation.
3. Chapitre 5 - Resultats et evaluation.
4. Chapitre 6 - Discussion, conclusion et perspectives.
5. Chapitre 2 - Etat de l'art.
6. Chapitre 1 - Introduction.
7. Annexes.

## Resultats Principaux A Conserver

- Linux/auth RandomForest: F1 = 0.916602.
- CICIDS2017 RandomForest: F1 = 0.997163.
- UNSW/CIC-DDoS RandomForest: F1 = 0.999965.
- Wazuh: 122 563 evenements, 3 676 anomalies candidates.
- Benchmark temps reel: 10 cycles, 8 537 lignes par cycle, moyenne 8.2012 s.
- Campagne CPU/RAM: 30 cycles, workflow moyen 9.3300 s.
- Robustesse multi-format: logs incomplets conserves.

## Structure Finale Attendue

- Chapitre 1: Introduction.
- Chapitre 2: Etat de l'art.
- Chapitre 3: Modele propose.
- Chapitre 4: Implementation.
- Chapitre 5: Resultats et evaluation.
- Chapitre 6: Conclusion et perspectives.
- Annexes.


