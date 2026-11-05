# Ariel Logminer

Prototype multi-agents léger pour l'analyse de journaux système et réseau
hétérogènes : normalisation multi-format, routage open-set par famille,
portefeuille de modèles légers, négociation Contract Net (bus local ou Redis
Streams), idempotence, corrélation d'anomalies candidates et tableau de bord.

Ce dépôt accompagne le mémoire d'ingénieur civil électricien (orientation
informatique) :

> MARHEGANE BITATI André Olivier, *Détection autonome et distribuée
> d'anomalies dans les journaux système et réseau à l'aide d'agents
> intelligents multitâches — Conception et évaluation locale du prototype
> Ariel Logminer*, Université de Kinshasa, Faculté polytechnique, 2025–2026.

Archive pérenne : DOI `10.5281/zenodo.[À COMPLÉTER]` (voir `CITATION.cff`).

**Portée.** Ariel Logminer est un prototype de laboratoire. Les résultats et
leurs limites sont exposés dans le mémoire (chapitre 5, section « Limites du
travail »). Il ne s'agit pas d'une plateforme de SOC prête pour la production.

## Contenu

| Dossier | Contenu |
|---|---|
| `src/logminer/` | Code du prototype (agents, Contract Net, bus, adaptateurs, routeur, API) |
| `scripts/` | Scripts de campagnes (`run_*.py`), agent Redis, génération de figures |
| `tests/` | Tests automatisés (`pytest`) |
| `experiments/phase_*/` | Artefacts des campagnes : `configs/`, `raw/`, `processed/`, `aggregated/`, `figures/`, `manifests/` (SHA-256), `logs/` |
| `experiments/phase_reference_copies/` | Copies des deux artefacts cités par le mémoire qui se trouvaient hors de `experiments/` (voir ci-dessous) |
| `state/EXPERIMENT_LEDGER.csv` | Registre des exécutions : `run_id`, commande, statut, chemins |
| `models/` | Modèles sérialisés utilisés par la campagne multi-source (condition M) |
| `memoire/` | Sources LaTeX du mémoire et figures finales |
| `docker/`, `Dockerfile`, `docker-compose.redis.yml` | Environnement conteneurisé et Redis de laboratoire |

## Installation

Environnement de référence : Python 3.11 ou 3.12 sous Windows 11 ; les agents
distants des campagnes multi-VM ont tourné sous Python 3.13.5 (Debian 13) et
3.8.10 (Ubuntu), d'après
`experiments/phase_cnp_endurance/aggregated/cnp_endurance_multivm_20260918T130822Z__summary.json`.

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate   |   Linux : source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-hdfs-bgl.txt   # protocoles HDFS / BGL (Drain3)
python -m pytest tests
```

## Données

Les jeux de données publics ne sont pas redistribués. Les télécharger depuis
leur source d'origine et les placer sous `data/raw/` :

| Jeu | Source | Licence / conditions |
|---|---|---|
| HDFS, BGL (Loghub) | Zenodo, DOI 10.5281/zenodo.8196385 | CC BY 4.0 (métadonnées : `data/verification/public_sources/zenodo_8196385_metadata.json`) |
| CICIDS2017 | Canadian Institute for Cybersecurity, University of New Brunswick | Conditions de l'éditeur, citation requise [À VÉRIFIER] |
| CSE-CIC-IDS2018 | CIC / Communications Security Establishment, registre AWS Open Data | Conditions de l'éditeur, citation requise [À VÉRIFIER] |
| UNSW-NB15 (modèle réseau historique) | UNSW Canberra | Conditions de l'éditeur [À VÉRIFIER] |

Le script `memoire/evidence/reproducibility/verify_public_dataset_copies.py`
compare les copies locales aux empreintes enregistrées.

## Reproduire une campagne

Chaque valeur du mémoire est reliée à un `run_id` et à un artefact. La
commande de chaque exécution figure dans `state/EXPERIMENT_LEDGER.csv`.
Exemples (commandes du registre) :

| Résultat du mémoire | `run_id` | Commande |
|---|---|---|
| HDFS au niveau bloc | `ds_hdfs_block_20260910T081756Z` | `python scripts/run_hdfs_block_strengthening.py` |
| Bootstrap HDFS | `hdfs_block_robustness_20260911T002351Z` | `python scripts/run_hdfs_block_robustness.py` |
| BGL connu / inconnu | `ds_bgl_known_unknown_20260910T082706Z` | `python scripts/run_bgl_known_unknown_strengthening.py` |
| CSE-CIC-IDS2018 | `external_csecicids2018_20260910T230136Z` | `python scripts/run_external_csecicids2018_strengthening.py` |
| Audit LR CSE-CIC-IDS2018 | `final_csecic_lr_forensic_20260911T000140Z` | `python scripts/run_final_csecicids2018_lr_forensic.py` |
| Endurance CNP multi-VM | `cnp_endurance_multivm_20260918T130822Z` | `python scripts/run_cnp_endurance_multivm.py` |

Les micro-latences dépendent de la machine : une reproduction doit publier sa
propre configuration et vérifier la conservation des tendances relatives,
non des valeurs à la décimale près.

La campagne multi-VM exige deux machines virtuelles et un Redis accessible.
Les identifiants de connexion sont fournis par variables d'environnement ou
par un gestionnaire de secrets ; ils ne font pas partie du dépôt. Ne pas
exposer Redis sur un réseau sans authentification.

## Compiler le mémoire

Depuis le dossier du mémoire : `pdflatex main`, `bibtex main`, puis deux
passes `pdflatex main` (pdfLaTeX, UTF-8, T1, babel français).

## Remarques sur les artefacts

- Les artefacts sont publiés tels qu'ils ont été produits, afin de conserver
  la validité des empreintes SHA-256 des manifestes. Certains contiennent des
  chemins absolus de la machine de laboratoire (colonnes de provenance) ; ces
  chemins sont des traces, non des dépendances.
- [À COMPLÉTER PAR L'AUTEUR, voir PUBLIC_RELEASE_PLAN.md §3] Traitement retenu
  pour les journaux Windows de la machine de laboratoire présents dans
  `experiments/phase_dataset_strengthening/processed/router_independent_*/`.
- Les fichiers `*.joblib` sont des objets Python sérialisés : ne les charger
  que depuis une source de confiance.

## Citation

Voir `CITATION.cff`. Merci de citer également les jeux de données utilisés.

## Licences

- Code : licence MIT (`LICENSE`).
- Textes du mémoire et figures : [À COMPLÉTER PAR L'AUTEUR, proposition :
  CC BY 4.0], sous réserve du règlement de l'Université de Kinshasa.
- Données dérivées : soumises aux licences des jeux d'origine
  (`DATA_LICENSES.md`).
