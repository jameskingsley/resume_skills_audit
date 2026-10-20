import numpy as np
from src.taxonomy import SKILLS, IDX

FEATURES = [
    "core_coverage", "optional_coverage", "n_core_missing", "cosine_sim", 
    "exp_gap", "exp_ok", "edu_gap", "location_ok", "n_candidate_skills"
]

EDU = {"secondary": 0, "tvet": 1, "ond": 1, "hnd": 2, "bsc": 2, "msc": 3}

def skill_vector(skills):
    v = np.zeros(len(SKILLS), dtype=np.float32)
    for s in skills:
        if s in IDX:
            v[IDX[s]] = 1.0
    n = np.linalg.norm(v)
    return v / n if n else v

def pair_features(cand, job):
    cs, core, opt = set(cand["skills"]), set(job["core_skills"]), set(job["optional_skills"])
    exp_gap = cand["years_experience"] - job["min_experience"]
    return {
        "core_coverage": len(cs & core) / max(len(core), 1),
        "optional_coverage": len(cs & opt) / max(len(opt), 1),
        "n_core_missing": len(core - cs),
        "cosine_sim": float(skill_vector(cs) @ skill_vector(core | opt)),
        "exp_gap": exp_gap,
        "exp_ok": int(exp_gap >= 0),
        "edu_gap": EDU.get(cand["education"], 0) - EDU.get(job["min_education"], 0),
        "location_ok": int(job["state"] == "Remote" or job["state"] == cand["state"]),
        "n_candidate_skills": len(cs),
    }