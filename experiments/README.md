# Registre des phases experimentales

La convention commune des noms se trouve dans
`ARTIFACT_NAMING_CONVENTION.md`.

## Phases canoniques

- `phase_dataset_strengthening` : robustesse des jeux et protocoles ;
- `phase_final_scientific_consolidation` : controles scientifiques finaux ;
- `phase_cnp_endurance` : endurance du Contract Net actuel sur deux VM.

## Phase historique conservee

- `phase_multi_agent` : benchmarks A--D et campagnes CNP courtes de septembre
  2026. Les artefacts restent immuables car ils sont cites dans le memoire.

La campagne Redis locale de six heures de juillet 2026 se trouve sous
`data/processed/`. Elle est `LEGACY` : preuve d'endurance des workers Redis
historiques, pas preuve principale du Contract Net actuel.

Un fichier n'est pas rendu canonique par son nom. Le resultat faisant autorite
est celui reference par un ledger avec statut `COMPLETED`, un protocole gele et
un manifeste SHA-256.
