# Reentrainement Mensuel Controle

Oui, le projet peut programmer un reentrainement mensuel des modeles a partir
des donnees recentes et de la memoire des agents. La regle importante est de ne
jamais remplacer automatiquement un modele parce qu'il vient d'etre entraine:
il devient d'abord un candidat, puis il est compare au modele courant.

## Principe

1. Les decisions analyste stockees dans `data/processed/logminer_audit.jsonl`
   sont exportees dans `data/processed/monthly_feedback_labels.csv`.
2. Chaque famille (`windows`, `wazuh`, `network`, `linux_auth`, etc.) lance sa
   commande de reentrainement et produit un artefact candidat dans
   `models/candidates/`.
3. Le modele courant et le candidat sont tous les deux scores sur le jeu de
   validation declare dans `monthly_retraining_plan.example.json`.
4. Le score du candidat est compare au score du modele courant avec une
   metrique declaree dans le plan: `f1` si labels disponibles, sinon
   `stability_score` pour les sources non labelisees.
5. Si le candidat depasse le modele courant d'au moins `min_delta`, il peut etre
   promu avec `--promote`. L'ancien artefact est sauvegarde dans
   `models/backups/`.
6. Le resultat complet est journalise dans l'audit et dans
   `data/processed/monthly_retraining_report.json`.

## Familles Couvertes

Le plan fourni couvre les familles chargees par le routeur:

| Famille | Modele courant | Validation | Metrique |
| --- | --- | --- | --- |
| `windows` | `models/isolation_forest_windows_local.joblib` | `data/processed/validation_simulated_windows.csv` | `f1` |
| `wazuh` | `models/isolation_forest_wazuh.joblib` | `data/processed/wazuh_months_logminer.csv` | `stability_score` |
| `network_cicids` | `models/random_forest_network_cicids.joblib` | `data/processed/network_verify_smoke_fast.csv` | `f1` |
| `network` | `models/random_forest_network_unsw_80_20_sampled.joblib` | `data/processed/network_verify_smoke_fast.csv` | `f1` |
| `linux_auth` | `models/random_forest_linux_auth.joblib` | `data/processed/linux_auth_labeled_logminer_sample_check.csv` | `f1` |
| `linux` | `models/isolation_forest_linux_colab.joblib` | `data/raw/Datasets/Dataset_csv/Linux_2k.log_structured.csv` | `stability_score` |
| `hdfs` | `models/isolation_forest_hdfs_colab.joblib` | `data/processed/validation_hdfs_test.csv` | `f1` |
| `bgl` | `models/isolation_forest_bgl_colab.joblib` | `data/processed/validation_bgl_test.csv` | `f1` |
| `fallback` | `models/isolation_forest_fallback_colab.joblib` | `data/processed/fallback_corrupt_incomplete_events.csv` | `stability_score` |

## Commande Manuelle

```powershell
python scripts\monthly_model_retraining.py `
  --plan docs\model_training\monthly_retraining_plan.example.json `
  --dry-run
```

Pour autoriser la promotion des meilleurs candidats:

```powershell
python scripts\monthly_model_retraining.py `
  --plan docs\model_training\monthly_retraining_plan.example.json `
  --promote
```

Le lanceur PowerShell ajoute un journal d'execution dans
`data/processed/monthly/monthly_retraining_task.log`:

```powershell
.\scripts\run_monthly_retraining.ps1
```

Avec promotion:

```powershell
.\scripts\run_monthly_retraining.ps1 -Promote
```

## Planificateur Windows

Installation de la tache mensuelle, le premier jour du mois a 02:00:

```powershell
.\scripts\install_monthly_retraining_task.ps1 -Promote
```

## Prudence Scientifique

La memoire des agents ne doit pas etre injectee aveuglement comme verite
absolue. Les rejets, validations et reclassements sont des labels operationnels:
ils ameliorent surtout la reduction des faux positifs et l'adaptation au
contexte local. Pour le memoire, il faut presenter ce mecanisme comme un
reentrainement controle et auditable, pas comme un apprentissage continu sans
garde-fou.
