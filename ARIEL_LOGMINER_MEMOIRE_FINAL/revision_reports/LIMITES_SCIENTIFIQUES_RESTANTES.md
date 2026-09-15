# Limites scientifiques restantes

1. CICIDS2017 généralise faiblement aux scénarios tenus hors entraînement ; le score aléatoire ne prédit pas ce transfert.
2. HDFS est évalué sur 2 000 blocs de test, dont 29 positifs ; le bootstrap décrit cet échantillon.
3. BGL ne contient aucun positif parmi les templates connus du test ; le rappel correspondant ne peut pas être estimé.
4. Le score CSE-CIC-IDS2018 dépend fortement de `Dst Port` et d’un petit groupe de caractéristiques.
5. Les contrôles CSE-CIC écartent certains mécanismes triviaux, pas toute fuite ou tout biais de scénario possible.
6. Le routeur open-set n’est testé que sur trois fichiers inconnus et 28 connus.
7. L’ablation du routage ne met pas en évidence de gain prédictif systématique.
8. La fixture Apache contient une seule ligne ; elle valide le chemin logiciel, pas un corpus Apache réel.
9. Aucune exactitude globale multi-source n’est disponible.
10. Le F1 Linux/auth de 0,390244 reste descriptif pour la source sélectionnée.
11. La mémoire influence certaines décisions mais n’améliore pas systématiquement débit, latence ou équité.
12. Le bénéfice d’une mise à jour contrôlée des modèles n’est pas évalué par un cycle complet de promotions et rejets.
13. La campagne multi-VM utilise deux VM, un Redis central et une durée courte ; elle ne démontre pas une haute disponibilité.
14. Les pannes de broker, partitions réseau, déploiements multi-sites et charges longues ne sont pas testés.
15. Le dashboard est fonctionnel, mais aucune étude d’utilisabilité avec des analystes n’a été menée.
16. La corrélation est évaluée sur un corpus synthétique et ne garantit pas la reconstruction d’incidents réels.
17. TLS, RBAC, gestion de secrets, réplication, observabilité et orchestration de production restent des perspectives.
