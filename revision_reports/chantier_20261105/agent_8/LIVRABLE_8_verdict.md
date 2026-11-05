# Livrable 8 — Verdict académique et note (provisoires)

## 1. Portée et réserves sur ce verdict

- **Évaluateur non indépendant.** Ce verdict est rédigé par l'outil qui a écrit une partie du contenu évalué. Il sert à préparer la soutenance et ne remplace pas l'avis des co-directeurs ni du jury.
- **Provisoire.** L'Agent 7 est partiel : la relecture de style par l'auteur reste à faire.
- **Règles de la Faculté inconnues.** Aucun barème ni motif formel de non-recevabilité n'a été fourni. La note repose sur une grille proposée ici.
- **Pas de relecture intégrale.** Le verdict se fonde sur les sections révisées, les artefacts contrôlés et les retours des lecteurs, non sur une relecture ligne à ligne des 181 pages.

## 2. Points de non-recevabilité soulevés par les lecteurs

| Point | Lecteur | État |
|---|---|---|
| A. Résumés contraires au corps | L2 | **Levé** : résumés récrits, aucune campagne absente du corps |
| B. Préenregistrement contradictoire | L2 | **Levé** : seuls les protocoles réellement commités avant exécution sont qualifiés ainsi |
| C. Statuts de H4 et de H5 | L2 | **Levé, à défendre** : H4 non tranchée, supériorité infirmée sur quatre jeux ; H5 non tranchée par règle préfixée |
| D. Part réelle de l'auteur | L2 | **Ouvert, et aggravé** : six campagnes préenregistrées s'ajoutent à celles du 4 novembre, toutes exécutées avec des outils d'IA |
| E. Tableau A.3 | L2 | **Levé** |
| Absence de scénario hétérogène conjoint | L3 | **Ouvert** : limite déclarée, non comblée (E-HET non exécutée, C13) |
| Évaluation sur un artefact (CSE-CIC-IDS2018) | L3 | **Levé** : section requalifiée en audit |
| Audit indépendant des résultats | L1 | **Ouvert** : rejeux internes seulement ; dépôt à remettre (A6-Q1) |

## 3. Classement des défauts

**Corrigé sans nouvelle expérience.** Résumés, statuts, préenregistrement, état de l'art, discussion référencée, chiffres contradictoires, précision, requalifications (BGL, CSE-CIC-IDS2018, corrélation).

**Corrigé par une nouvelle campagne.** Baselines HDFS au niveau bloc (E-H4), spécialisation (E-H3b stricte), mémoire (E-H5), Contract Net (E-CNP, E-CNP au moindre chargé).

**Exigerait encore une campagne, non réalisée.**

- Scénario hétérogène conjoint (E-HET).
- Routeur contre table statique : 45 sources locales au plus pour 90 requises.
- Contract Net et moindre chargé en exécution distribuée.
- Budget de ressources de H4, désormais impossible à fixer a posteriori.
- Cycle complet de promotion et de rejet (H5).
- Étude auprès d'analystes.

**Peut rendre le travail non recevable, selon le jury.**

1. **La maîtrise par l'auteur.** C'est le risque principal. Le travail expérimental décisif a été conçu et exécuté par des outils d'IA, peu avant la remise. La déclaration est exacte, mais elle n'établit pas la maîtrise. Seule la soutenance le peut.
2. **L'hétérogénéité non démontrée**, alors qu'elle figure dans le titre.

## 4. Grille et note

| Critère | Barème | Note | Points perdus |
|---|---:|---:|---|
| Fond | 8 | 4,0 | Aucune hypothèse validée. Aucun bénéfice propre de l'architecture : négociation sans avantage, mémoire seulement à p = 0,9, distribution non démontrée. Pas d'analyse conjointe de sources hétérogènes. Résultats prédictifs sous les règles simples. Points obtenus : chaîne intégrée fonctionnelle et réponses claires aux questions |
| Rigueur | 6 | 5,0 | Forte pour le préenregistrement, le jugement sur critères écrits, la publication des résultats défavorables et la traçabilité. Perdu : critères de H1 à H5 non fixés à l'avance, un défaut de données découvert tard, pas de reproduction indépendante |
| Originalité | 3 | 1,0 | Pas de nouvel algorithme ni de nouvelle méthode ; réplications de critiques connues. Point obtenu : démontage expérimental d'une architecture, rarement publié sous cette forme |
| Forme | 3 | 2,0 | Structure et bibliographie correctes. Perdu : style marqué par l'assistance, résumé long, répétitions, Bokuse non relu |
| **Total** | **20** | **12/20** | |

Fourchette plausible : **11 à 14**. Le haut suppose une soutenance où l'auteur explique seul E-CNP, E-H5 et la fuite d'E-H3b, et une relecture de style. Le bas, ou un refus, devient probable si l'auteur ne peut pas défendre ces campagnes.

Ce total ne mesure pas la soutenance et n'est pas une prédiction de la note réelle.

## 5. Recommandation

**Validation conditionnelle** : le manuscrit est défendable en tant qu'étude critique et honnête d'un prototype d'ingénierie, à condition de ne plus le présenter comme la démonstration d'une architecture supérieure.

Conditions, par ordre d'importance :

1. **L'auteur maîtrise et peut refaire** : relancer au moins une campagne par groupe, et expliquer seul chaque protocole et chaque résultat (`agent_6/PREPARATION_SOUTENANCE.md`).
2. **Relecture de style de sa main**, au moins sur l'introduction, la discussion et la conclusion.
3. **Remise du dépôt** aux évaluateurs, et choix de son mode (A6-Q1).
4. **Relecture du Bokuse** par un locuteur du lingala.
5. **Soumission préalable aux co-directeurs**, notamment du changement de thèse : le mémoire conclut désormais que la négociation n'apporte aucun avantage établi, et que la contribution est méthodologique.

Le titre mérite aussi leur avis : il annonce une architecture pour des journaux « hétérogènes », alors que seule l'hétérogénéité des formats est établie.

=== PASSATION ===
Agent : 8 — Verdict
Statut : terminé, provisoire
Livrables : `agent_8/LIVRABLE_8_verdict.md`
Prochain agent recommandé : aucun ; décisions et relecture de l'auteur
Raison : les points restants relèvent de l'auteur, des co-directeurs et du jury.
Points de vigilance pour le repreneur : ne pas présenter la note comme une évaluation indépendante ; les articles restent à traiter, dont le score 0,999965.
=== FIN PASSATION ===
