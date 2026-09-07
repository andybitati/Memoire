# DECISIONS SCIENTIFIQUES FIGÉES

## D001

Decision: Exclure le F1 = 0,999965 des résultats scientifiques et des nouvelles campagnes.

Evidence: Provenance dataset insuffisamment démontrée.

Reason: L'archive employée ne peut être réattribuée ni à UNSW-NB15 ni au CIC-DDoS2019 officiel.

Affected sections: Résumés, résultats supervisés, discussion et conclusion.

Do not reconsider unless: Une chaîne de provenance officielle, complète et vérifiable apparaît.

## D002

Decision: Qualifier la preuve multi-VM de preuve de laboratoire uniquement.

Evidence: Hôte Windows, VirtualBox, VM Debian, VM Ubuntu, Redis hôte, 525 entrées lues et acquittées, lag final 0 et pending final 0 ; campagne distincte de reprise après panne simulée.

Reason: Les artefacts ne démontrent pas 525 succès applicatifs individuellement traçables.

Affected sections: Architecture expérimentale, résultats multi-VM, annexes et conclusion.

Do not reconsider unless: Une nouvelle campagne traçant chaque tâche de bout en bout est produite.

## D003

Decision: Décrire `AgentMessage` avec sept champs métier seulement : `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`.

Evidence: Implémentation active dans `src/logminer/agents/bus.py`.

Reason: Aucun champ direct `event_id`, `message_id` ou `metadata`; les identifiants Redis relèvent du transport.

Affected sections: Contrat d'échange et figures d'architecture.

Do not reconsider unless: Le contrat actif est explicitement versionné et modifié.

## D004

Decision: Classer l'ancienne expérience Drain3 HDFS/BGL comme EXPLORATOIRE.

Evidence: Drain3 et certaines statistiques ont été construits séparément sur les partitions de test.

Reason: Le protocole ne constitue pas une validation train-vers-test indépendante.

Affected sections: Méthodologie, résultats HDFS/BGL, discussion et conclusion.

Do not reconsider unless: Un protocole strict avec état appris sur train, validation et test gelé est exécuté.

## D005

Decision: Conclure à l'absence de gain prédictif systématique du routage spécialisé.

Evidence: Deltas F1 : CICIDS2017 +0,000201 ; Linux/auth -0,003050 ; UNSW-NB15 -0,000264.

Reason: Deux familles sur trois régressent et l'expérience ne mesure pas le routeur réel.

Affected sections: Résultats d'ablation, discussion et contribution architecturale.

Do not reconsider unless: Une expérience différente, préenregistrée et correctement contrôlée apporte une nouvelle preuve.

## D006

Decision: Qualifier LogisticRegression de meilleur F1 moyen parmi cinq candidats dans l'ancien holdout CICIDS2017, sans généralisation au-delà.

Evidence: F1 moyen 0,233670, très variable selon le scénario et non dominant sur toutes les métriques.

Reason: Les cinq scénarios ne sont pas cinq répétitions identiques.

Affected sections: Protocole et résultats de comparaison des modèles.

Do not reconsider unless: La campagne multi-seeds produit une preuve plus robuste.

## D007

Decision: Classer la mise à jour contrôlée comme IMPLÉMENTÉE et vérifiée en DRY-RUN, mais NON ÉVALUÉE de bout en bout.

Evidence: Aucun candidat réel entraîné, aucune comparaison, promotion ou rejection réelle prouvée.

Reason: Une procédure présente dans le code n'est pas une performance démontrée.

Affected sections: Architecture, résultats, discussion et perspectives.

Do not reconsider unless: Des cas end-to-end avec scores, décisions, audits et hashes sont exécutés.

## D008

Decision: Conserver le benchmark monolithique-vers-agents comme preuve de surcoût à la charge testée.

Evidence: Monolithique 1,6357 tâche/s ; agents 1,5715 ; agents avec reprise 1,5267. CPU en pourcentage d'un cœur logique équivalent, RAM RSS en MiB.

Reason: Aucun gain de débit n'est démontré avec les agents à cette charge.

Affected sections: Méthode de mesure, tableau de performances et discussion.

Do not reconsider unless: Une nouvelle campagne comparable et correctement instrumentée est exécutée.

## D009

Decision: Utiliser les SHA-256 du manifeste pour identifier les copies locales, sans les présenter comme preuve de provenance officielle.

Evidence: Onze fichiers prioritaires ont été hashés et dimensionnés ; aucun fichier du dépôt ne fournit une chaîne de téléchargement officielle vérifiable pour ces copies.

Reason: L'identité binaire locale et la provenance officielle sont deux propriétés distinctes.

Affected sections: Reproductibilité, description des datasets et limites.

Do not reconsider unless: Des URL, versions, checksums éditeur et preuves de téléchargement concordantes sont retrouvés.
