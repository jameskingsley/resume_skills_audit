import json
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from clearml import Task
from sklearn.ensemble import HistGradientBoostingClassifier
from src.features import FEATURES, pair_features
from src.evaluator import evaluate_model
from src.taxonomy import SKILLS

STATES = ["Lagos", "FCT", "Kano", "Oyo", "Rivers", "Kaduna", "Enugu", "Ogun"]
ROLES = {
    "Data Analyst": (["excel", "sql", "data_analysis"], ["power_bi", "python", "statistics"], 1, "bsc"),
    "Junior Data Scientist": (["python", "statistics", "sql"], ["data_analysis", "machine_learning"], 2, "bsc"),
    "M&E Assistant": (["excel", "data_analysis", "monitoring_evaluation"], ["statistics", "survey_tools"], 1, "bsc"),
}
EDU_LEVELS = ["secondary", "tvet", "ond", "bsc", "msc"]

def generate_synthetic_data(n_jobs=300, n_cands=1000, seed=42):
    rng = np.random.default_rng(seed)
    roles = list(ROLES)
    jobs = []
    for j in range(n_jobs):
        r = rng.choice(roles); core, opt, mexp, medu = ROLES[r]
        jobs.append(dict(job_id=f"J{j:04d}", title=r, core_skills=list(core),
                         optional_skills=list(rng.choice(opt, size=rng.integers(1, len(opt) + 1), replace=False)),
                         min_experience=int(max(0, mexp + rng.integers(-1, 2))), min_education=medu,
                         state="Remote" if rng.random() < .12 else str(rng.choice(STATES))))
    cands = []
    for c in range(n_cands):
        r = rng.choice(roles); core, opt, mexp, medu = ROLES[r]
        skills = {s for s in core if rng.random() < .75} | {s for s in opt if rng.random() < .45}
        floor = EDU_LEVELS.index(medu if medu in EDU_LEVELS else "tvet")
        cands.append(dict(candidate_id=f"C{c:04d}", background=r, skills=sorted(skills),
                          years_experience=int(rng.integers(0, 6)),
                          education=EDU_LEVELS[int(np.clip(floor + rng.integers(-1, 2), 0, 4))],
                          state=str(rng.choice(STATES)), signup_day=int(rng.integers(0, 60))))
    by_title = {}
    for j in jobs: by_title.setdefault(j["title"], []).append(j)
    rows = []
    sig = lambda z: 1 / (1 + np.exp(-z))
    for c in cands:
        for j in list(rng.choice(by_title[c["background"]], size=2)) + list(rng.choice(jobs, size=2)):
            f = pair_features(c, j)
            z = -4.8 + 5.5 * f["core_coverage"] + 1.2 * f["optional_coverage"] + 1.0 * f["exp_ok"] + 1.2 * f["location_ok"]
            rows.append({**f, "candidate_id": c["candidate_id"], "job_id": j["job_id"],
                         "signup_day": c["signup_day"], "shortlisted": int(rng.random() < sig(z)),
                         "keyword_overlap": len(set(c["skills"]) & set(j["core_skills"] + j["optional_skills"]))})
    return pd.DataFrame(rows)

def train_and_track():
    task = Task.init(project_name="Resume Skills Audit", task_name="Production Model Training")
    
    df = generate_synthetic_data()
    X, y = df[FEATURES], df["shortlisted"].values
    tr, te = df.signup_day < 48, df.signup_day >= 48
    
    model = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.05, random_state=42)
    model.fit(X[tr], y[tr])
    
    # Rigorous Evaluation before logging
    metrics = evaluate_model(model, X[te], y[te], df[te])
    print("Evaluation Metrics:", metrics)
    
    logger = task.get_logger()
    for k, v in metrics.items():
        logger.report_scalar(title="Evaluation", series=k, value=v, iteration=1)
        
    art_dir = Path("artifacts")
    art_dir.mkdir(exist_ok=True)
    model_path = art_dir / "model.joblib"
    meta_path = art_dir / "model_meta.json"
    
    joblib.dump(model, model_path)
    meta = {"version": "skillaudit-v2", "features": FEATURES, "skills": SKILLS, "metrics": metrics}
    meta_path.write_text(json.dumps(meta, indent=2))
    
    task.upload_artifact("model", artifact_object=str(model_path))
    task.upload_artifact("metadata", artifact_object=str(meta_path))
    print("Model evaluated successfully and uploaded to ClearML.")

if __name__ == "__main__":
    train_and_track()