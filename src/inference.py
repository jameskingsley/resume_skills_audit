import json
import joblib
import pandas as pd
from pathlib import Path
from clearml import Task
from src.features import FEATURES, pair_features
from src.taxonomy import SKILLS, COURSES

class InferenceEngine:
    def __init__(self):
        print("Connecting to ClearML Model Registry...")
        task = Task.get_task(project_name="Resume Skills Audit", task_name="Production Model Training")
        
        if not task:
            raise RuntimeError("Could not find 'Production Model Training' task in ClearML.")
        
        # Use task.artifacts dictionary mapping to fetch local copies of artifacts
        artifacts = task.artifacts
        if "model" not in artifacts or "metadata" not in artifacts:
            raise RuntimeError("ClearML task found, but 'model' or 'metadata' artifacts are missing.")
            
        model_local_path = artifacts["model"].get_local_copy()
        meta_local_path = artifacts["metadata"].get_local_copy()
        
        self.model = joblib.load(model_local_path)
        self.meta = json.loads(Path(meta_local_path).read_text())
            
        assert self.meta["features"] == FEATURES, "Feature mismatch between ClearML artifact and local codebase."
        assert self.meta["skills"] == SKILLS, "Taxonomy mismatch between ClearML artifact and local codebase."
        print("Model successfully loaded from ClearML.")

    def score(self, cand, job):
        features_dict = pair_features(cand, job)
        df_feat = pd.DataFrame([features_dict])[FEATURES]
        return float(self.model.predict_proba(df_feat)[0, 1])

    def lifts(self, cand, job, missing):
        base = self.score(cand, job)
        out = []
        for s in missing:
            new_cand = {**cand, "skills": sorted(set(cand["skills"]) | {s})}
            new_score = self.score(new_cand, job)
            out.append({
                "skill": s, 
                "score_after": round(new_score, 3), 
                "lift": round(new_score - base, 3), 
                "course": COURSES.get(s, f"{s.replace('_', ' ').title()} course")
            })
        return sorted(out, key=lambda d: -d["lift"])