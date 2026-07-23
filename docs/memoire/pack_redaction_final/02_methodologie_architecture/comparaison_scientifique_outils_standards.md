# Comparaison Scientifique Avec Outils Standards

Cette comparaison est volontairement limitee. Elle ne pretend pas que
fail2ban, OSSEC et Wazuh ont tous ete executes dans une meme infrastructure de
production. Trois niveaux sont separes:

1. **Baseline experimentale inspiree de fail2ban**: une regle locale detecte
   des echecs d'authentification repetes ou a risque sur un dataset Linux/auth
   labellise. Elle sert de baseline rule-based, pas d'execution officielle de
   fail2ban.
2. **Analyse d'exports Wazuh**: les fichiers Wazuh deja presents dans le corpus
   sont compares aux anomalies candidates produites par Logminer. Cette partie
   est experimentale sur donnees Wazuh exportees.
3. **Comparaison fonctionnelle OSSEC/fail2ban/Wazuh**: les outils standards
   sont utilises comme references de capacites, de maturite et de positionnement.

Formulation recommandee pour article:

> To avoid overstating the comparison, fail2ban and OSSEC are used as
> functional references, while a lightweight rule-based baseline inspired by
> fail2ban is implemented for controlled authentication scenarios. Wazuh is
> evaluated through exported alerts/logs available in the experimental corpus.

Limites:

- La baseline fail2ban-like ne remplace pas une execution reelle de fail2ban.
- OSSEC n'est pas execute directement; il sert de reference fonctionnelle.
- Les anomalies non supervisees de Logminer sont des candidates, pas des
  intrusions confirmees.
- Les comparaisons de F1 ne doivent etre faites que sur les datasets labelises.

