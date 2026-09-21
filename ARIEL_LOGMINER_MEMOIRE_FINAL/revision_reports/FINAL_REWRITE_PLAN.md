# Plan de réécriture scientifique finale

Le manuscrit reste dans `ARIEL_LOGMINER_MEMOIRE_FINAL`. Les corrections sont guidées
par les rapports expérimentaux finaux et par la matrice claim–evidence consolidée.

| Partie | Correction prévue | Preuve de référence |
| --- | --- | --- |
| Résumé et abstract | Remplacer les valeurs HDFS, multiformat, routeur et multi-VM obsolètes ; rappeler que la contribution est architecturale et méthodologique. | `FINAL_SCIENTIFIC_CONSOLIDATION_REPORT.md` |
| Introduction générale | Définir explicitement agent, autonomie, intelligence, multitâche et distribution ; maintenir H1–H5 et QR1–QR6 comme réponses prudentes. | `docs/TRUE_MULTI_AGENT_ARCHITECTURE.md`, statuts H/QR |
| Chapitre 1 — état de l’art | Conserver l’état de l’art existant et vérifier que les notions d’agents, CNP, open-set, dérive de distribution et fuite restent reliées à des références vérifiables. | `references.bib`, chapitre 2 |
| Chapitre 2 — architecture | Décrire les classes multi-agents réellement utilisées, le cycle CNP et la politique d’utilité ; distinguer coordination métier et transport Redis. | code `src/logminer/agents`, `docs/TRUE_MULTI_AGENT_ARCHITECTURE.md` |
| Chapitre 3 — implémentation | Documenter `AgentMessage` avec exactement sept champs, les stores d’idempotence, les bus et le registre de compatibilité des modèles. | `src/logminer/agents/bus.py`, registre P3 |
| Chapitre 4 — résultats | Mettre à jour HDFS au niveau `block_id`, BGL et sa baseline de nouveauté, multiformat 7001/7001, open-set 3/3 et CNP 1400/1401. | rapport de consolidation et artefacts P1–P4 |
| Chapitre 5 — validité | Distinguer validité interne, externe, de construit et statistique ; conserver les limites : 29 positifs HDFS, 89,8081 % de templates BGL inconnus, N=1 Apache, trois fichiers open-set. | rapport final, matrices de preuve |
| Chapitre 6 — discussion | Interpréter le coût de négociation, l’absence de gain systématique de mémoire/routage et la portée réelle des résultats. | benchmark multi-agent, ablation, P3 |
| Chapitre 7 — reproductibilité | Actualiser run_id, manifests, tests, figures 12–20 et commandes ; laisser l’industrialisation aux perspectives. | manifeste SHA-256 et JUnit |
| Conclusion et annexes | Répondre aux QR/H sans transformer une preuve fonctionnelle en preuve prédictive ; mettre à jour les contrats, protocoles et tableaux. | matrices H/QR et audit final |

Les occurrences historiques conservées dans les rapports d’audit sont explicitement
étiquetées comme anciennes, invalidées ou hors périmètre ; elles ne servent pas de
résultats finaux dans le corps scientifique.
