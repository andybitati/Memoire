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
3. Le score du candidat est compare au score du modele courant avec une
   metrique declaree dans le plan: `f1` si labels disponibles, sinon une
   metrique proxy documentee.
4. Si le candidat depasse le modele courant d'au moins `min_delta`, il peut etre
   promu avec `--promote`. L'ancien artefact est sauvegarde dans
   `models/backups/`.
5. Le resultat complet est journalise dans l'audit et dans
   `data/processed/monthly_retraining_report.json`.

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

## Planificateur Windows

Exemple de tache mensuelle, le premier jour du mois a 02:00:

```powershell
$action = New-ScheduledTaskAction `
  -Execute "python" `
  -Argument "scripts\monthly_model_retraining.py --plan docs\model_training\monthly_retraining_plan.example.json --promote" `
  -WorkingDirectory "E:\Cours\TFE"

$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 2:00
Register-ScheduledTask -TaskName "LogminerMonthlyRetraining" -Action $action -Trigger $trigger
```

## Prudence Scientifique

La memoire des agents ne doit pas etre injectee aveuglement comme verite
absolue. Les rejets, validations et reclassements sont des labels operationnels:
ils ameliorent surtout la reduction des faux positifs et l'adaptation au
contexte local. Pour le memoire, il faut presenter ce mecanisme comme un
reentrainement controle et auditable, pas comme un apprentissage continu sans
garde-fou.
