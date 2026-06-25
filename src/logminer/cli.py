# Source Generated with Decompyle++
# File: cli.cpython-311.pyc (Python 3.11)

'''CLI officielle du pipeline Logminer.

Exemples:
  - Convertir un fichier:
      python -m Logminer.cli -i /var/log/auth.log --out-dir Dataset_csv --name auth.csv

  - Convertir un dossier (récursif):
      python -m Logminer.cli -i ./Dataset_raw --out-dir Dataset_csv --name dataset.csv --tqdm
'''
import argparse
import os
import sys
from pipeline import run_pipeline

def main(argv = None):
    p = argparse.ArgumentParser(description = 'Logminer: détection -> parsing -> CSV normalisé')
    p.add_argument('-i', '--input', required = True, help = "Chemin d'entrée: fichier ou dossier")
    p.add_argument('--out-dir', default = 'Dataset_csv', help = 'Dossier où enregistrer tous les CSV')
    p.add_argument('--name', default = 'dataset.csv', help = 'Nom du CSV principal (dans --out-dir)')
    p.add_argument('--sep', default = ';', help = 'Séparateur CSV')
    p.add_argument('--split-rows', type = int, default = 0, help = 'Rotation: max lignes par CSV (0 = pas de split)')
    p.add_argument('--progress-every', type = int, default = 0, help = 'Affiche une progression toutes N lignes (si supporté)')
    p.add_argument('--tqdm', action = 'store_true', help = 'Barre de progression (si supporté)')
    p.add_argument('--debug', action = 'store_true', help = 'Mode debug')
    p.add_argument('--parallel-workers', type = int, default = 1, help = 'Nombre de fichiers parses en parallele pour un dossier')
    args = p.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok = True)
    produced = run_pipeline(input_path = args.input, out_dir = args.out_dir, out_name = args.name, sep = args.sep, split_rows = args.split_rows, progress_every = args.progress_every, use_tqdm = args.tqdm, debug = args.debug, parallel_workers = args.parallel_workers)
    print('\n'.join(produced))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
