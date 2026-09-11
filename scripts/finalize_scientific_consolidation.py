#!/usr/bin/env python3
"""Produit la matrice, le rapport et le manifeste de consolidation finale."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from final_consolidation_common import (  # noqa: E402
    CONFIG_PATH, PHASE_ROOT, append_ledger, ensure_phase_dirs, relative,
    run_id, sha256_file, utc_now, write_json,
)

EXPERIMENT_ID = "final_p5_p6_scientific_consolidation"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def f(value: float) -> str:
    return f"{float(value):.6f}".replace(".", ",")


def n(value: int) -> str:
    return f"{int(value):,}".replace(",", " ")


def render_claim_matrix(p1: dict[str, Any], p2: dict[str, Any], p3: dict[str, Any], p4: dict[str, Any]) -> str:
    m = next(row for row in p3["conditions"] if row["condition"] == "M")
    return "\n".join([
        "# Matrice claim–evidence consolidée", "",
        "| Claim | Avant | Nouvelle preuve | Résultat | Limite | Statut final |",
        "| --- | --- | --- | --- | --- | --- |",
        f"| LR externe non triviale | LR F1 moyen {f(p1['observed']['f1_mean'])} ; absence de vecteurs exacts inter-jour | Permutation, 78 mono-features, coefficients standardisés, ablations train-only | `Dst Port` seule : F1 {f(p1['best_single_feature_by_f1']['f1_mean'])} ; après retrait top-10 : F1 {f(next(row for row in p1['ablation'] if int(row['removed_count']) == 10)['f1_mean'])} ; conclusion B | Deux jours et quatre scénarios DoS ; PR-AUC de permutation instable ; causalité non établie | PARTIELLEMENT SOUTENU |",
        f"| Router open-set | Rejet 0/3 | Seuil `top_score={p2['policy']['min_top_score']:.0f}` sélectionné sur 196 observations de validation pseudo-open connues, puis test final gelé | Rejet 3/3 ; faux rejet connu 0/28 ; coverage {f(p2['final_test']['coverage'])} | Trois fichiers inconnus locaux seulement ; pas de généralisation open-set | PARTIELLEMENT SOUTENU |",
        f"| E2E modèles réels | 1 401 tâches avec `e2e_lightweight_candidate_rule_v1` | Registre de compatibilité et traces par tâche avec modèle chargé, hash et marqueur d’inférence | {n(m['model_inference_count'])}/1 401 inférences réelles, {m['heuristic_fallback_count']} fallback explicite, {m['errors']} erreur | Local ; artefacts historiques ; métriques prédictives H non évaluables sans circularité | SOUTENU |",
        f"| HDFS block robustness | F1 bloc {f(p4['baseline']['f1'])} sur 29 positifs | 1 000 bootstraps par `block_id`, seuil gelé et 29 retraits d’un positif | Médiane F1 {f(next(row for row in p4['bootstrap']['descriptive_intervals'] if row['metric'] == 'f1')['median'])}, intervalle descriptif [{f(next(row for row in p4['bootstrap']['descriptive_intervals'] if row['metric'] == 'f1')['percentile_2_5'])} ; {f(next(row for row in p4['bootstrap']['descriptive_intervals'] if row['metric'] == 'f1')['percentile_97_5'])}] ; résultat variable | Bootstrap descriptif, non preuve d’indépendance ; 29 positifs | PARTIELLEMENT SOUTENU |",
        "| Multi-agent autonomy | acquis | Non réévalué inutilement ; tests CNP et idempotence conservés | Architecture légère, décisions, refus, attributions, mémoire et transport Redis déjà prouvés dans le périmètre laboratoire | Pas de causalité nouvelle sur performance ou résilience industrielle | SOUTENU |",
        "| Industrial deployment | perspective | Non testé dans cette phase | NON ÉVALUÉ | Haute disponibilité, multi-site, partitions et très grande échelle non évalués | HORS PÉRIMÈTRE |",
        "",
        "Les statuts portent sur les claims formulés dans le périmètre exact des artefacts cités, pas sur une validité industrielle générale.",
    ]) + "\n"


def render_recommendations(p1: dict[str, Any], p2: dict[str, Any], p3: dict[str, Any], p4: dict[str, Any]) -> str:
    m = next(row for row in p3["conditions"] if row["condition"] == "M")
    f1_boot = next(row for row in p4["bootstrap"]["descriptive_intervals"] if row["metric"] == "f1")
    return "\n".join([
        "# Recommandations contrôlées pour la mise à jour ultérieure du mémoire", "",
        "Aucune modification du manuscrit n’a été effectuée pendant la consolidation.", "",
        "| Chapitre | Section | Ancien claim concerné | Nouvelle valeur | Nouvelle formulation recommandée | Figure à ajouter | Tableau à remplacer ou compléter | Limitation à conserver |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| Chapitre 5 | Validation externe CSE-CIC-IDS2018 | Le F1 LR proche de 1 suggère une forte généralisation | LR {f(p1['observed']['f1_mean'])} ; `Dst Port` seule {f(p1['best_single_feature_by_f1']['f1_mean'])} ; top-10 retirées {f(next(row for row in p1['ablation'] if int(row['removed_count']) == 10)['f1_mean'])} | « Sur ce holdout de deux journées DoS, la LR atteint un F1 moyen de {f(p1['observed']['f1_mean'])}, mais l’audit montre une forte dépendance à quelques caractéristiques, notamment le port de destination. » | Figures 12 à 15 | Ajouter permutation, mono-feature, coefficients et ablation | Deux journées, quatre scénarios DoS, échantillons équilibrés et dépendance aux variables dominantes |",
        f"| Chapitre 5 | Routage multi-famille | Le routeur ne rejette aucune source inconnue | Seuil 100 ; rejet 3/3 ; faux rejet 0/28 ; coverage {f(p2['final_test']['coverage'])} | « Une politique de rejet calibrée sur validation pseudo-open rejette les trois fichiers inconnus du corpus sans rejeter les 28 fichiers connus. » | Figure 16 | Remplacer la ligne open-set 0/3 par le résultat consolidé, tout en conservant l’historique | Seulement trois sources inconnues locales ; `decision_margin` n’est pas une probabilité |",
        f"| Chapitre 5 | Pipeline CNP multi-source | Les modèles sont recommandés mais la règle légère est exécutée | {m['model_inference_count']}/1 401 inférences réelles ; 1 fallback ; 0 erreur ; latence moyenne {f(m['latency_mean'])} s | « La condition M exécute réellement les artefacts compatibles sur 1 400 unités ; Apache utilise un fallback heuristique explicite. » | Figures 17 et 18 | Ajouter le tableau par source modèle recommandé/modèle exécuté | Pas d’accuracy globale ; H utilise directement certains labels ; avertissements de versions scikit-learn sur trois artefacts IsolationForest |",
        f"| Chapitre 5 | HDFS block-level | F1 bloc présenté comme valeur ponctuelle | F1 {f(p4['baseline']['f1'])} ; bootstrap médian {f(f1_boot['median'])}, intervalle [{f(f1_boot['percentile_2_5'])} ; {f(f1_boot['percentile_97_5'])}] | « Le F1 observé vaut {f(p4['baseline']['f1'])} sur ce test gelé ; le bootstrap descriptif indique une variabilité liée au faible nombre de blocs positifs. » | Figures 19 et 20 | Compléter le tableau HDFS par intervalle descriptif, IQR et leave-one-positive-out | 29 positifs ; intervalle descriptif ; aucune indépendance statistique revendiquée |",
        "| Chapitre 8 | Limites et perspectives | Industrialisation parfois mêlée aux limites expérimentales immédiates | NON ÉVALUÉ | « Les propriétés industrielles de haute disponibilité, de déploiement multi-site, de tolérance aux partitions et de montée en charge à très grande échelle sont laissées aux perspectives. » | Aucune | Aucune | Ne pas transformer ces perspectives en propriétés démontrées |",
        "| Résumé et conclusion | Portée des contributions | Généralisation large implicite | Aucun nouveau chiffre global | Réserver les claims aux corpus, unités et protocoles effectivement évalués ; distinguer preuve d’exécution, métrique prédictive et anomalie candidate | Aucune | Aucune | Ni SOC industriel, ni gain prédictif systématique du routage, ni transfert inter-datasets |",
    ]) + "\n"


def render_report(
    p1: dict[str, Any], p2: dict[str, Any], p3: dict[str, Any], p4: dict[str, Any],
    tests: dict[str, Any], matrix_path: Path, recommendations_path: Path,
) -> str:
    h = next(row for row in p3["conditions"] if row["condition"] == "H")
    m = next(row for row in p3["conditions"] if row["condition"] == "M")
    f1_ablated = next(row for row in p1["ablation"] if int(row["removed_count"]) == 10)
    f1_boot = next(row for row in p4["bootstrap"]["descriptive_intervals"] if row["metric"] == "f1")
    predictive = {row["source"]: row for row in p3["predictive_metrics"]}
    linux = predictive.get("linux_auth", {})
    return "\n".join([
        "# Rapport final de consolidation scientifique d’Ariel Logminer", "",
        "## 1. Objectif", "",
        "Cette phase ferme quatre critiques encore traitables sans alourdir le prototype : audit du résultat externe CSE-CIC-IDS2018, rejet open-set, inférence effective des modèles routés et sensibilité du résultat HDFS au niveau bloc. Les expériences antérieures jugées solides ne sont pas relancées.", "",
        "## 2. État avant consolidation", "",
        "La LR externe atteignait un F1 moyen de 0,999212 après un contrôle de doublons exacts. Le routeur reconnaissait 28 fichiers connus mais rejetait 0/3 inconnus. Le replay CNP de 1 401 unités exécutait une règle légère malgré les recommandations de modèles. HDFS atteignait 0,892308 au niveau bloc sur seulement 29 positifs test.", "",
        "## 3. Audit LR CSE-CIC-IDS2018", "",
        f"Le run `{p1['run_id']}` réutilise les pools figés du run `{p1['principal_run_id']}` : apprentissage le 15 février 2018, test le 16 février, 78 caractéristiques numériques, cinq graines et 10 000 observations par classe dans chaque partition. La conclusion retenue est B : performance très dépendante de quelques features.", "",
        "Les contrôles exécutés n’ont pas mis en évidence de fuite triviale correspondant aux mécanismes testés.", "",
        "Cette phrase ne signifie pas qu’aucune fuite est possible et ne dépasse pas les contrôles réalisés.", "",
        "## 4. Permutation labels", "",
        f"La permutation de `y_train` conserve X_train, X_test et y_test. Le F1 moyen tombe à {f(p1['label_permutation']['f1_mean'])}, le MCC à {f(p1['label_permutation']['mcc_mean'])}. La PR-AUC moyenne vaut {f(p1['label_permutation']['pr_auc_mean'])}, avec une forte dispersion jusqu’à {f(p1['label_permutation']['pr_auc_max'])}. Le contrôle détruit la qualité de décision au seuil fixé mais pas systématiquement le classement, ce qui renforce le constat de variables dominantes.", "",
        "## 5. Analyse mono-feature", "",
        f"Parmi les 78 modèles mono-feature, `Dst Port` atteint à elle seule un F1 moyen de {f(p1['best_single_feature_by_f1']['f1_mean'])} et une PR-AUC de {f(p1['best_single_feature_by_pr_auc']['pr_auc_mean'])}. Cette séparation doit être décrite comme propre à la composition des deux journées et scénarios évalués.", "",
        "## 6. Coefficients LR", "",
        "Les coefficients proviennent d’une LR précédée d’un `StandardScaler` ajusté sur le train uniquement. Les plus fortes valeurs absolues moyennes concernent `Dst Port`, `Fwd Seg Size Min`, `PSH Flag Cnt`, `Fwd Header Len` et `Pkt Len Var`. Elles signalent une association discriminante dans le modèle, pas une cause de l’attaque.", "",
        "## 7. Ablation features", "",
        f"Les retraits top-1/3/5/10 sont fixés avant exécution et classés sur le modèle train de chaque graine. Le F1 passe de {f(p1['observed']['f1_mean'])} avec 78 variables à {f(f1_ablated['f1_mean'])} après retrait des dix premières ; le FPR passe de {f(p1['observed']['fpr_mean'])} à {f(f1_ablated['fpr_mean'])}. La performance dépend donc fortement d’un petit sous-ensemble de caractéristiques.", "",
        "## 8. Router open-set", "",
        f"Le run `{p2['run_id']}` sélectionne `top_score >= 100` sur 196 observations leave-one-family-out issues exclusivement des 28 sources connues. Le test final, consulté après gel, donne une known accuracy de {f(p2['final_test']['known_accuracy'])}, une macro-F1 connue de {f(p2['final_test']['known_macro_f1'])}, un rejet inconnu de {f(p2['final_test']['unknown_rejection_rate'])}, un faux rejet connu de {f(p2['final_test']['false_rejection_rate_on_known'])}, une coverage de {f(p2['final_test']['coverage'])} et une selective accuracy de {f(p2['final_test']['selective_accuracy'])}. `decision_margin` reste un score heuristique de séparation.", "",
        "## 9. E2E avec modèles réellement routés", "",
        f"Le run `{p3['run_id']}` exécute deux conditions de 1 401 tâches. H applique 1 401 fois la règle légère. M appelle réellement un artefact compatible sur {m['model_inference_count']} unités, utilise {m['heuristic_fallback_count']} fallback Apache, produit {m['errors']} erreur et {m['reassignments']} réattribution. La latence moyenne passe de {f(h['latency_mean'])} s à {f(m['latency_mean'])} s ; le P95 passe de {f(h['latency_p95'])} s à {f(m['latency_p95'])} s. Les refus CNP ({m['refusals']}) proviennent des agents sans capability compatible et ne sont pas des erreurs d’exécution.", "",
        f"Les temps processus mesurés valent {f(h['condition_process_time_sec'])} s pour H et {f(m['condition_process_time_sec'])} s pour M. Le RSS après condition vaut {int(h['rss_after_bytes'])} octets pour H et {int(m['rss_after_bytes'])} octets pour M. Ces valeurs sont des instantanés du même processus ; M garde sept artefacts en cache. Elles ne décrivent ni un pic isolé ni une consommation de production.", "",
        f"Sur Linux/auth, seule source sélectionnée contenant deux classes et une unité compatible, la condition M donne un F1 descriptif de {f(linux.get('f1', float('nan')))}. BGL et CICIDS ne contiennent qu’une classe dans leurs 200 premières unités : NON ÉVALUÉ. Les métriques H sont NON ÉVALUÉES car la règle historique lit directement les labels disponibles. Aucune accuracy globale n’est fabriquée.", "",
        "## 10. Robustesse HDFS block-level", "",
        f"Le run `{p4['run_id']}` reproduit le F1 {f(p4['baseline']['f1'])} sur 2 000 blocs, dont 29 positifs, avec l’état Drain3 inchangé, l’agrégateur `mean` et le seuil {p4['threshold']:.16f}. Sur 1 000 bootstraps de `block_id`, la médiane est {f(f1_boot['median'])}, l’intervalle descriptif 2,5–97,5 % [{f(f1_boot['percentile_2_5'])} ; {f(f1_boot['percentile_97_5'])}] et l’IQR {f(f1_boot['iqr'])}. Les 29 retraits d’un bloc positif donnent tous un F1 {f(p4['leave_one_positive_out']['f1_min'])} et un rappel {f(p4['leave_one_positive_out']['recall_min'])}. Le score block-level reste variable sous les analyses de sensibilité réalisées.", "",
        "## 11. Résultats négatifs", "",
        "- La LR externe est fortement dominée par quelques caractéristiques ; son score ne justifie pas une généralisation large.",
        "- La PR-AUC du contrôle permuté ne s’effondre pas de manière stable selon la graine.",
        f"- L’inférence réelle Linux/auth n’atteint qu’un F1 descriptif de {f(linux.get('f1', float('nan')))} sur les 200 premières lignes.",
        "- Le test HDFS reste variable sous bootstrap malgré un rappel stable.",
        "- Trois artefacts IsolationForest Colab émettent un avertissement de compatibilité scikit-learn 1.6.1 vers 1.7.2 ; les appels réussissent, mais cette limite doit rester visible.", "",
        "- Le premier run P3 (`multisource_cnp_model_inference_20260911T001644Z`) est SUPERSEDED : son calcul d’incidents H était incomplet. Ses sorties raw sont conservées, mais seules les valeurs du run définitif `multisource_cnp_model_inference_20260911T003432Z` soutiennent les claims finaux.", "",
        "## 12. Statistiques", "",
        "P1 rapporte moyenne, écart-type d’échantillon, médiane, extrema et IC normal approximatif sur cinq graines corrélées par pools parents. P2 est une évaluation sur fichiers et groupes, sans IC. P3 rapporte latences moyennes/P95 et métriques par source uniquement. P4 utilise des percentiles bootstrap descriptifs au niveau bloc ; ils ne prouvent pas l’indépendance statistique.", "",
        "## 13. Tests de non-régression", "",
        f"Le fichier JUnit atteste `{tests['tests']}` tests, `{tests['failures']}` échec, `{tests['errors']}` erreur et `{tests['skipped']}` test ignoré. Les garde-fous couvrent AgentMessage, CNP, idempotence, splits, Drain3, scalers, calibration, schémas, marqueurs d’inférence et seuil HDFS gelé.", "",
        "## 14. Claim–evidence final", "",
        f"La matrice consolidée est `{relative(matrix_path)}`. Elle retient : LR externe partiellement soutenue, open-set partiellement soutenu, E2E réel soutenu, robustesse HDFS partiellement soutenue, autonomie multi-agent soutenue dans le laboratoire et industrialisation hors périmètre.", "",
        "## 15. Impact H1–H5", "",
        "| Hypothèse | Impact final | Statut recommandé |", "| --- | --- | --- |",
        "| H1 | Aucun changement de couverture ; HDFS reste évalué au bloc et le pipeline multiformat est préservé | PARTIELLEMENT SOUTENUE |",
        "| H2 | Le CNP exécute désormais les modèles compatibles sur 1 400 unités, sans nouvelle preuve de débit ou de résilience | PARTIELLEMENT SOUTENUE |",
        "| H3 | Le rejet fonctionne sur 3/3 inconnues après calibrage connu-only, mais le test est très petit | PARTIELLEMENT SOUTENUE |",
        "| H4 | L’audit LR impose une forte requalification ; l’inférence réelle est prouvée mais l’utilité prédictive générale ne l’est pas | PARTIELLEMENT SOUTENUE |",
        "| H5 | Aucun nouvel effet causal de la mémoire n’est mesuré | PARTIELLEMENT SOUTENUE, inchangée |", "",
        "## 16. Impact QR1–QR6", "",
        "| Question | Impact final | Niveau recommandé |", "| --- | --- | --- |",
        "| QR1 | Couverture multiformat inchangée ; robustesse HDFS mieux quantifiée | RÉPONSE PARTIELLE renforcée |",
        "| QR2 | Preuve d’exécution effective des artefacts dans le CNP | RÉPONSE PARTIELLE renforcée |",
        "| QR3 | Rejet open-set ajouté et validé sur trois fichiers | RÉPONSE PARTIELLE renforcée |",
        "| QR4 | Aucun test utilisateur | RÉPONSE PARTIELLE, inchangée |",
        "| QR5 | Aucun gain causal de mémoire nouveau | RÉPONSE PARTIELLE, inchangée |",
        "| QR6 | Protocoles figés, contrôles négatifs, hashes et tests renforcent la reproductibilité | RÉPONSE FORTE dans le périmètre laboratoire |", "",
        "## 17. Affirmations désormais soutenables", "",
        "- Le résultat LR externe est reproductible sous son holdout, mais très dépendant de quelques caractéristiques.",
        "- Une politique légère calibrée sans les trois fichiers finaux les rejette tous, sans faux rejet parmi les 28 fichiers connus.",
        "- Les agents CNP chargent et appellent réellement sept artefacts compatibles sur 1 400 des 1 401 unités de la condition M.",
        "- Le F1 HDFS observé est reproduit avec seuil gelé et sa variabilité bootstrap est quantifiée.", "",
        "## 18. Affirmations toujours non démontrées", "",
        "- Absence de toute fuite possible dans CSE-CIC-IDS2018 : NON SOUTENU.",
        "- Généralisation de la LR à l’ensemble de CSE-CIC-IDS2018 ou à un SOC : NON SOUTENU.",
        "- Rejet open-set général au-delà des trois fichiers testés : NON SOUTENU.",
        "- Gain prédictif systématique du routage ou de la condition M : NON SOUTENU.",
        "- Accuracy globale multi-source : NON ÉVALUÉ.",
        "- Haute disponibilité, tolérance aux partitions et très grande échelle : NON ÉVALUÉ.", "",
        "## 19. Perspectives industrielles", "",
        "Les propriétés industrielles de haute disponibilité, de déploiement multi-site, de tolérance aux partitions et de montée en charge à très grande échelle sont laissées aux perspectives.", "",
        "Les prolongements nécessaires pour passer d’une validation de laboratoire à un système opérationnel de production comprennent Redis Sentinel/Cluster, le test des partitions réseau et du failover broker, le multi-site, Kubernetes, Prometheus/Grafana, une gestion industrielle des secrets, l’authentification forte, TLS, RBAC, la haute disponibilité, les tests de charge à grande échelle, un SOC réel et une étude utilisateur auprès d’analystes SOC.", "",
        "## 20. Artefacts", "",
        "Les configurations, résultats bruts, données préparées, agrégats, figures 12 à 20, rapports et manifests se trouvent sous `experiments/phase_final_scientific_consolidation/`. Les rapports spécialisés P1–P4 y restent séparés des synthèses finales.", "",
        "## 21. Hashes", "",
        "`experiments/phase_final_scientific_consolidation/manifests/SHA256_MANIFEST.json` recense les scripts, configurations, modèles, références d’entrée et artefacts. Le manifeste s’exclut lui-même afin d’éviter une dépendance circulaire. La validation machine est conservée séparément.", "",
        "## 22. Commandes exactes", "",
        "```powershell",
        ".venv-hdfs-bgl\\Scripts\\python.exe scripts\\run_final_csecicids2018_lr_forensic.py",
        ".venv-hdfs-bgl\\Scripts\\python.exe scripts\\run_router_open_set_consolidation.py",
        ".venv-hdfs-bgl\\Scripts\\python.exe scripts\\run_multisource_cnp_model_inference.py",
        ".venv-hdfs-bgl\\Scripts\\python.exe scripts\\run_hdfs_block_robustness.py",
        ".venv-hdfs-bgl\\Scripts\\python.exe -m pytest tests\\test_dataset_strengthening.py tests\\test_true_multi_agent.py tests\\test_final_scientific_consolidation.py -q --junitxml=experiments\\phase_final_scientific_consolidation\\logs\\relevant_tests_junit.xml",
        ".venv-hdfs-bgl\\Scripts\\python.exe scripts\\finalize_scientific_consolidation.py",
        "```", "",
        "Dans cette session, chaque commande shell a été préfixée par `rtk`, conformément aux instructions du dépôt.", "",
        "La commande `graphify update .` a été tentée après modification du code et a échoué avec `[WinError 5] Accès refusé`. Cet échec de l’outil de cartographie n’affecte pas les résultats expérimentaux ni leurs empreintes.", "",
        "## 23. Recommandations de rédaction du mémoire", "",
        f"Les modifications à appliquer après validation sont détaillées dans `{relative(recommendations_path)}`. Elles visent les sections expérimentales du chapitre 5, les limites/perspectives du chapitre 8, puis le résumé et la conclusion. Aucun chapitre n’a été modifié par cette phase.",
    ]) + "\n"


def junit_summary(path: Path) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    return {
        key: sum(int(suite.attrib.get(key, 0)) for suite in suites)
        for key in ("tests", "failures", "errors", "skipped")
    } | {"path": relative(path), "sha256": sha256_file(path)}


def artifact_category(path: Path) -> str:
    value = relative(path)
    if value.startswith("scripts/") or value.endswith("model_router.py"):
        return "script"
    if "/configs/" in value:
        return "config"
    if value.startswith("models/"):
        return "model"
    if "/raw/" in value:
        return "raw_result"
    if "/processed/" in value:
        return "processed"
    if "/aggregated/" in value:
        return "aggregated"
    if "/figures/" in value:
        return "figure"
    if "/reports/" in value or value.endswith("REPORT.md") or "CLAIM_EVIDENCE" in value:
        return "report"
    return "artifact"


def main() -> int:
    ensure_phase_dirs()
    current_run = run_id("final_scientific_consolidation")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID, phase="P5-P6", run_id=current_run, dataset="consolidated",
        protocol="claim_evidence_hash_and_writing_recommendations", status="RUNNING", started_at=started_at,
        command="python scripts/finalize_scientific_consolidation.py", error_path=relative(error_path),
    )
    try:
        p1 = load_json(PHASE_ROOT / "aggregated/external_csecicids2018_lr_forensic_summary.json")
        p2 = load_json(PHASE_ROOT / "aggregated/router_open_set_summary.json")
        p3 = load_json(PHASE_ROOT / "aggregated/multisource_cnp_model_inference_summary.json")
        p4 = load_json(PHASE_ROOT / "aggregated/hdfs_block_robustness_summary.json")
        tests_path = PHASE_ROOT / "logs/relevant_tests_junit.xml"
        tests = junit_summary(tests_path)
        if tests["failures"] or tests["errors"]:
            raise AssertionError(f"Tests non verts: {tests}")

        matrix_path = ROOT / "FINAL_CONSOLIDATED_CLAIM_EVIDENCE_MATRIX.md"
        report_path = ROOT / "FINAL_SCIENTIFIC_CONSOLIDATION_REPORT.md"
        recommendations_path = PHASE_ROOT / "reports/MEMOIRE_REVISION_RECOMMENDATIONS.md"
        matrix_path.write_text(render_claim_matrix(p1, p2, p3, p4), encoding="utf-8")
        recommendations_path.write_text(render_recommendations(p1, p2, p3, p4), encoding="utf-8")
        report_path.write_text(render_report(p1, p2, p3, p4, tests, matrix_path, recommendations_path), encoding="utf-8")

        figures = [PHASE_ROOT / "figures" / f"dataset_{number:02d}_{name}.png" for number, name in [
            (12, "external_lr_coefficients"), (13, "external_single_feature_scores"),
            (14, "external_feature_ablation"), (15, "external_label_permutation"),
            (16, "router_open_set_tradeoff"), (17, "e2e_real_model_coverage"),
            (18, "e2e_real_model_latency"), (19, "hdfs_block_bootstrap"),
            (20, "hdfs_positive_sensitivity"),
        ]]
        if not all(path.exists() and path.stat().st_size > 0 for path in figures):
            missing = [relative(path) for path in figures if not path.exists() or path.stat().st_size == 0]
            raise AssertionError(f"Figures finales absentes: {missing}")

        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P5-P6", run_id=current_run, dataset="consolidated",
            protocol="claim_evidence_hash_and_writing_recommendations", status="COMPLETED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/finalize_scientific_consolidation.py",
            summary_path=relative(report_path), error_path=relative(error_path),
            notes=f"claims consolidated; {tests['tests']} tests pass; manuscript unchanged.",
        )

        additional = [
            ROOT / "scripts/final_consolidation_common.py",
            ROOT / "scripts/run_final_csecicids2018_lr_forensic.py",
            ROOT / "scripts/run_router_open_set_consolidation.py",
            ROOT / "scripts/run_multisource_cnp_model_inference.py",
            ROOT / "scripts/run_hdfs_block_robustness.py",
            ROOT / "scripts/finalize_scientific_consolidation.py",
            ROOT / "src/logminer/agents/model_router.py",
            ROOT / "docs/FINAL_SCIENTIFIC_GAP_ANALYSIS.md",
            ROOT / "state/FINAL_SCIENTIFIC_CONSOLIDATION_PROGRESS.md",
            ROOT / "state/EXPERIMENT_LEDGER.csv",
            matrix_path, report_path,
            ROOT / "experiments/phase_dataset_strengthening/configs/external_csecicids2018_protocol.json",
            ROOT / "experiments/phase_dataset_strengthening/configs/router_independent_sources.json",
            ROOT / "experiments/phase_dataset_strengthening/configs/multiformat_balanced_protocol.json",
            ROOT / "experiments/phase_dataset_strengthening/processed/external_csecicids2018_20260910T230136Z_train_pool.csv.gz",
            ROOT / "experiments/phase_dataset_strengthening/processed/external_csecicids2018_20260910T230136Z_test_pool.csv.gz",
            ROOT / "experiments/phase_dataset_strengthening/raw/router_independent_20260910T094257Z_routes.csv",
            ROOT / "experiments/phase_dataset_strengthening/raw/ds_hdfs_block_20260910T081756Z__hdfs_selected_events.csv.gz",
            ROOT / "experiments/phase_dataset_strengthening/processed/ds_hdfs_block_20260910T081756Z__hdfs_selected_blocks.csv",
            ROOT / "experiments/phase_dataset_strengthening/processed/ds_hdfs_block_20260910T081756Z__hdfs_drain3_train_state.bin",
        ]
        registry = load_json(PHASE_ROOT / "configs/multisource_model_compatibility_registry.json")
        additional.extend(ROOT / entry["recommended_model"] for entry in registry["entries"])

        manifest_path = PHASE_ROOT / "manifests/SHA256_MANIFEST.json"
        validation_path = PHASE_ROOT / "aggregated/final_artifact_validation.json"
        files = {
            path.resolve()
            for path in [*PHASE_ROOT.rglob("*"), *additional]
            if path.is_file() and path.resolve() not in {manifest_path.resolve(), validation_path.resolve()}
        }
        entries = [
            {
                "category": artifact_category(path), "path": relative(path),
                "size_bytes": path.stat().st_size, "sha256": sha256_file(path),
            }
            for path in sorted(files, key=lambda item: relative(item))
        ]
        p1_manifest = load_json(next(PHASE_ROOT.glob("manifests/final_csecic_lr_forensic_*_manifest.json")))
        manifest = {
            "schema_version": 1, "generated_at": utc_now(), "run_id": current_run,
            "self_excluded": relative(manifest_path), "validation_excluded_to_avoid_circularity": relative(validation_path),
            "entries": entries,
            "external_raw_references": p1_manifest["raw_sources"],
            "entry_count": len(entries),
        }
        write_json(manifest_path, manifest)
        mismatches = []
        for entry in entries:
            path = ROOT / entry["path"]
            if not path.exists() or sha256_file(path) != entry["sha256"]:
                mismatches.append(entry["path"])
        validation = {
            "generated_at": utc_now(), "manifest": relative(manifest_path),
            "manifest_sha256": sha256_file(manifest_path), "entry_count": len(entries),
            "all_entries_exist_and_match": not mismatches, "mismatches": mismatches,
            "figures_12_to_20_present": True, "tests": tests,
            "manuscript_files_modified_by_phase": False,
        }
        write_json(validation_path, validation)
        if mismatches:
            raise AssertionError(f"Hashes invalides: {mismatches}")
        print(json.dumps({
            "status": "COMPLETED", "run_id": current_run, "manifest_entries": len(entries),
            "manifest_sha256": validation["manifest_sha256"], "tests": tests,
        }, ensure_ascii=False))
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P5-P6", run_id=current_run, dataset="consolidated",
            protocol="claim_evidence_hash_and_writing_recommendations", status="FAILED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/finalize_scientific_consolidation.py",
            error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
