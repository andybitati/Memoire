# Audit scientifique final du mémoire

Date de consolidation : 11 septembre 2026  
Dossier compilé : `ARIEL_LOGMINER_MEMOIRE_FINAL`  
PDF : `build/main.pdf`  
Pagination finale après stabilisation des références croisées : 140 pages

## Résultats et statut

| Élément | Fait conservé | Preuve | Statut final |
| --- | --- | --- | --- |
| CICIDS2017 aléatoire | RF F1 0,995142 | `cicids_protocol_comparison.csv` | Résultat descriptif du split aléatoire |
| CICIDS2017 scénario | RF F1 macro 0,157744 | même artefact | Généralisation inter-scénarios faible |
| CICIDS2017 temporel | RF 0,437429 ; LR 0,556615 | même artefact | Transfert temporel partiel |
| Sélection CICIDS2017 | LR 0,233670, meilleur F1 parmi cinq candidats | `cicids_model_candidates_summary.csv` | Comparaison valide dans ce protocole |
| HDFS | F1 bloc 0,892308 ; seuil 1,2729429339548877 | JSON HDFS final | Drain3 train-only vérifié |
| Bootstrap HDFS | médiane 0,894737 ; [0,800000 ; 0,961039] | 1 000 réplications par `block_id` | Incertitude descriptive |
| BGL | Histogram 0,913698 ; inconnus 89,8081 % | métriques BGL par groupe | Dépendance à la nouveauté explicitée |
| BGL baseline | 0,277885 | même artefact | Histogram supérieur au baseline simple |
| CSE-CIC-IDS2018 | LR 0,999212 ; RF 0,401375 | métriques split 15/16 février | Forte dépendance aux variables |
| CSE mono-feature | `Dst Port` 0,999720 | scores mono-feature | Diagnostic, pas preuve de généralisation |
| CSE ablation | top 10 retirées : 0,657859 | ablation finale | Sensibilité démontrée dans le protocole |
| Routeur open-set | 3/3 inconnus rejetés ; 0/28 faux rejet | trade-off final | Fonctionnement démontré sur 31 fichiers |
| Multi-format | 7 001/7 001 lues, parsées, normalisées | synthèse multi-format | Couverture du protocole seulement |
| E2E modèles | 1 400/1 401 inférences réelles ; 1 fallback | synthèse CNP par source | Usage réel des modèles confirmé |
| Benchmark A--D | 160 runs ; 264 000 tâches ; 0 échec | statistiques multi-agent | Aucun gain systématique de la mémoire |
| Multi-VM | 60/60, répartition 30/30, 15 refus, 1 FAIL contrôlé | JSON `multivm_cnp_20260909T202632Z_37592` | Validation distribuée de laboratoire |
| Corrélation | précision 0,764706 ; rappel 0,866667 ; F1 0,812500 | artefact synthétique final | Validité limitée au corpus construit |

## Incertitudes P0 fermées

### Campagne multi-VM

La seule campagne retenue dans le corps du mémoire est `multivm_cnp_20260909T202632Z_37592`. Elle associe Debian 13 et Ubuntu, un worker par VM, un coordinateur sur l’hôte et Redis 7.4.9 centralisé. Sa durée est 2,712455 s pour 60 tâches. Les campagnes antérieures ne servent pas de preuve principale.

### Ancien score ambigu

La valeur ambiguë n’apparaît plus dans le résumé, les chapitres, la conclusion ou les annexes. Aucun résultat final n’est attribué à un dataset dont la provenance n’est pas démontrée.

### Contrat `AgentMessage`

Le mémoire présente exactement : `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`. Il n’ajoute pas d’`event_id` de premier niveau. Les identifiants protocolaires sont dans `payload` ; les identifiants Redis/MQTT appartiennent au transport.

### Drain3 HDFS

Le JSON final établit des blocs disjoints, un ajustement sur entraînement seulement, `match_only` en validation/test, un état inchangé avant/après inférence, et un choix agrégateur/seuil sur validation. Le résultat retenu est celui au niveau bloc.

### CPU et RAM

Le mémoire ne conserve que les unités documentées : tâches/s, ms, secondes CPU, pourcentage équivalent cœur, pourcentage normalisé machine et RSS en Mo. Les anciennes valeurs sans unité établie sont supprimées.

### Mise à jour contrôlée

Statut : infrastructure IMPLÉMENTÉE, chemins partiellement TESTÉS, bénéfice global NON ÉVALUÉ, mise à jour continue en PERSPECTIVE. Aucune promotion/rejet complet en exploitation n’est revendiqué.

### Ablation du routage

L’expérience établit le fonctionnement du routage et le contrôle de compatibilité. Aucun gain prédictif systématique n’est revendiqué.

### Régression logistique à 0,233670

Le résultat provient de CICIDS2017, split fichier/scénario, graines 42–46, espace commun, cinq candidats. LR possède le meilleur F1 moyen parmi les candidats testés, avec une dispersion élevée ; il n’est pas présenté comme un bon score absolu.

## Contrôles rédactionnels

- Titre complet harmonisé dans la page de garde et les métadonnées PDF.
- Résumé et abstract cohérents avec le chapitre des résultats.
- Toutes les hypothèses H1–H5 : PARTIELLEMENT SOUTENUES.
- QR1–QR3 : réponses partielles renforcées ; QR4–QR5 : réponses partielles ; QR6 : réponse forte dans le laboratoire.
- Aucune exactitude globale multi-source inventée.
- Aucun résultat industriel extrapolé.
- Texte et bibliographie en UTF-8 ; aucun mojibake détecté par le scan final.
- Figures finales générées depuis les artefacts, avec captions interprétatives et sources.

## Réserves qui demeurent

Les tests open-set ne contiennent que trois inconnus. HDFS possède 29 blocs positifs dans le test. BGL ne contient aucun positif dans le groupe des templates connus. CSE-CIC-IDS2018 reste dépendant de caractéristiques liées au scénario. Redis est centralisé. La mémoire n’apporte pas de gain systématique. L’utilisabilité du dashboard n’a pas été évaluée auprès d’analystes.
