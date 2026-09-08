# Instabilite Holdout CICIDS2017

| Seed | Fichier tenu hors entrainement | Attaques du fichier | Taux attaque fichier | TP | FN | FP | F1 | PR-AUC | Lecture |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 42 | Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv | DDoS=61194 | 0.6119 | 2553 | 1447 | 0 | 0.779185 | 0.953532 | scenario partiellement generalise |
| 43 | Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv | PortScan=12488 | 0.1249 | 20 | 3980 | 1 | 0.009948 | 0.915857 | detection quasi nulle malgre quelques positifs retrouves |
| 44 | Friday-WorkingHours-Morning.pcap_ISCX.csv | Bot=1966 | 0.0103 | 0 | 1966 | 0 | 0.000000 | 0.315521 | aucun positif detecte dans l'echantillon tenu hors entrainement |
| 45 | Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv | Infiltration=32 | 0.0002 | 0 | 32 | 0 | 0.000000 | 0.008821 | aucun positif detecte dans l'echantillon tenu hors entrainement |
| 46 | Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv | Web Attack � Brute Force=1507, Web Attack � XSS=652, Web Attack � Sql Injection=21 | 0.0128 | 0 | 2180 | 0 | 0.000000 | 0.339342 | aucun positif detecte dans l'echantillon tenu hors entrainement |

Conclusion: l'ecart-type eleve vient de l'heterogeneite des scenarios tenus hors entrainement. Le modele generalise partiellement au DDoS, presque pas au PortScan dans ce protocole, et pas aux scenarios Bot, Infiltration et WebAttacks echantillonnes.
