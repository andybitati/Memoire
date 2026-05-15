# Recuperation des fichiers Python

Les fichiers `.pyc` de `Preprocessing/Logminer` ont ete recuperes avec `pycdc`.

Resultats:

- `recovered_pycdc/` contient les sources `.py` reconstruites.
- `recovered_disasm/` contient les desassemblages complets `.dis.txt`.
- `recovered_py/` contient les sorties d'echec de `decompyle3` et ne doit pas etre utilise comme source principale.

Limites:

- Les `.pyc` sont en Python 3.11.
- `decompyle3` et `uncompyle6` ne supportent pas ces bytecodes.
- `pycdc` a recupere les fichiers, mais certains opcodes Python 3.11 restent incomplets.
- 25 fichiers sur 32 passent une analyse syntaxique directe.
- 7 fichiers demandent une correction manuelle:
  - `detectors.py`
  - `detectors/file_detector.py`
  - `normalizers/categorizer.py`
  - `normalizers/runner.py`
  - `parsers/cef_leef.py`
  - `parsers/cloudtrail.py`
  - `parsers/unknown.py`

Pour travailler, partir de `recovered_pycdc/Preprocessing/Logminer`.
Si une fonction est incomplete, comparer avec le fichier correspondant dans `recovered_disasm/Preprocessing/Logminer`.
