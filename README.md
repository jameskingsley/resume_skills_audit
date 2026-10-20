# Resume Skills Audit Studio

An end-to-end Machine Learning-powered HR solution that automates candidate skill gap analysis, shortlisting probability scoring, and tailored upskilling recommendations. By accepting raw Job Descriptions and Candidate Resumes in multiple formats (.pdf, .docx, .txt, .csv, .md), the studio instantly parses skill taxonomies, calculates candidate-job alignment, and highlights high-impact learning pathways.

Live Application

 Experience the deployed application on Streamlit Cloud:

 [Resume Skills Audit Studio Live Demo](https://resumeskillsaudit-3lu8sw6qjb97oe3f5smd6b.streamlit.app/)

Key Features

Document Parsing & Text Extraction:

Automated extraction from .pdf, .docx, .txt, .csv, and .md files using pypdf and python-docx.

Intelligent skill taxonomy matching against standardized core and optional skills.

ML-Powered Shortlist Scoring:

Feature-engineered probabilistic scoring model predicting candidate shortlist likelihood in real time.

ClearML MLOps Integration:

Remote fetching of audited model artifacts and metadata dynamically from the ClearML Model Registry.

Automated Skill Gap & Criteria Auditing:

Direct side-by-side verification of required vs. nice-to-have skills.

Hard constraint verification for experience level, education level, and geographic location.

Priority Upskilling & Lift Analysis:

Feature attribution mechanism determining missing skills that yield the highest match score lift.

Direct mapping of identified gaps to actionable training courses.

System Architecture & Project Structure

The repository adheres to a clean modular structure separating MLOps pipelines, data features, and user-facing frontend code:

resume_skills_audit/
├── app/
│   └── frontend.py           # Streamlit application entry point & UI engine
├── models/
│   ├── model.joblib          # Trained model artifact (local backup)
│   └── metadata.json         # Taxonomy & feature schema contract
├── src/
│   ├── __init__.py
│   ├── features.py           # Feature engineering & pairing logic
│   ├── inference.py          # Inference engine & ClearML integration
│   ├── taxonomy.py          # Skill dictionary & course mappings
│   └── train.py              # ML training pipeline script
├── .gitignore
├── README.md                 # System documentation
└── requirements.txt          # Python dependencies


🧪 ML Pipeline & Feature Engineering

The inference engine constructs pairwise vectors between candidate profiles and job requirements:

Taxonomy Parsing: Normalizes skill text into a structured dictionary of core, optional, and candidate skill vectors.

Feature Pairing Matrix (pair_features):

Skill Overlap Ratios: Computes core skill coverage, optional skill coverage, and total taxonomy match percentage.

Requirement Checks: Binary and scalar calculations for candidate experience relative to minimum job experience.

Categorical Alignments: Educational equivalency score and state/location match logic.

Lift Strategy: Evaluates counterfactual skill scenarios ($Score_{after} - Score_{base}$) for missing required/optional skills to rank top training recommendations.

 Technology Stack

Frontend & UI: Streamlit

ML & Inference: Scikit-learn, Pandas, Joblib

MLOps & Registry: ClearML

Document Processing: PyPDF, Python-Docx

Runtime Environment: Python 3.10+

Local Setup & Installation

1. Prerequisites

Ensure you have Python 3.10+ and pip installed.

2. Clone Repository & Setup Virtual Environment

git clone https://github.com/your-username/resume_skills_audit.git
cd resume_skills_audit

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt


4. Configure ClearML Credentials

To connect locally to your ClearML instance, export your API keys or create a clearml.conf file:

# Windows PowerShell
$env:CLEARML_API_ACCESS_KEY="YOUR_ACCESS_KEY"
$env:CLEARML_API_SECRET_KEY="YOUR_SECRET_KEY"

# Linux/macOS
export CLEARML_API_ACCESS_KEY="YOUR_ACCESS_KEY"
export CLEARML_API_SECRET_KEY="YOUR_SECRET_KEY"


5. Launch the Streamlit App

streamlit run app/frontend.py


Deployment & Streamlit Secrets Configuration

When deploying to Streamlit Community Cloud, configure your ClearML credentials inside App Settings Secrets:

Open your app on Streamlit Cloud and click Settings $\rightarrow$ Secrets.

Add your ClearML credentials in TOML format:

CLEARML_API_ACCESS_KEY = "your_api_access_key_here"
CLEARML_API_SECRET_KEY = "your_api_secret_key_here"
CLEARML_API_HOST = "https://api.clear.ml"
CLEARML_WEB_HOST = "https://app.clear.ml"
CLEARML_FILES_HOST = "https://files.clear.ml"


Save settings. The InferenceEngine inside src/inference.py will automatically read st.secrets upon startup and pull the audited model artifact from ClearML.

 User Guide for HR Teams

Upload Job Description: Drag and drop or upload the vacancy file (.pdf, .docx, etc.) under Column 1.

Upload Candidate Resume: Drag and drop or upload the applicant's resume under Column 2.

Automated Extraction: Review or adjust auto-extracted job titles, experience thresholds, location, and skills.

Run Audit: Click Run Skills Audit to generate:

Match Score & Shortlist Likelihood Percentage.

Skill Breakdown Matrix (Core vs. Optional vs. Missing).

Experience, Education, and Location checks.

Priority Upskilling Recommendations with specific course suggestions.
