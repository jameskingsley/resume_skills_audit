SKILLS = [
    "excel", "sql", "python", "data_analysis", "power_bi", "statistics", "data_entry", "data_visualization",
    "machine_learning", "monitoring_evaluation", "survey_tools", "web_development", "javascript", 
    "graphic_design", "digital_marketing", "social_media", "content_writing", "it_support", "networking",
    "bookkeeping", "accounting_software", "mobile_money_ops", "sales", "customer_service",
    "inventory_management", "procurement", "business_planning", "financial_literacy",
    "agronomy", "poultry_management", "irrigation", "post_harvest_handling", "agribusiness",
    "extension_services", "aquaculture", "electrical_installation", "solar_pv", "plumbing", 
    "welding", "carpentry", "motor_mechanics", "logistics", "driving", "warehouse_ops", 
    "community_health", "first_aid", "fashion_design", "photography", "video_editing",
    "communication", "teamwork", "problem_solving", "english_writing", "project_management"
]

IDX = {s: i for i, s in enumerate(SKILLS)}

SYNONYMS = {
    "ms excel": "excel", "microsoft excel": "excel", "spreadsheet": "excel", "pivot tables": "excel",
    "mysql": "sql", "postgresql": "sql", "postgres": "sql", "bigquery": "sql",
    "python3": "python", "pandas": "python", "numpy": "python",
    "data analytics": "data_analysis", "powerbi": "power_bi", "power bi": "power_bi",
    "tableau": "data_visualization", "spss": "statistics", "stata": "statistics",
    "scikit-learn": "machine_learning", "m&e": "monitoring_evaluation", "kobo toolbox": "survey_tools"
}

PHRASES = {s.replace("_", " "): s for s in SKILLS}
PHRASES.update(SYNONYMS)
PHRASES = dict(sorted(PHRASES.items(), key=lambda kv: -len(kv[0])))

COURSES = {
    "excel": "Excel for Work (2 wks)", "sql": "SQL Foundations (3 wks)", "python": "Python for Data (6 wks)",
    "data_analysis": "Data Analysis Bootcamp (4 wks)", "power_bi": "Power BI Dashboards (2 wks)",
    "statistics": "Practical Statistics (4 wks)", "machine_learning": "Intro to Machine Learning (6 wks)",
    "monitoring_evaluation": "M&E Fundamentals (3 wks)", "survey_tools": "Digital Data Collection (1 wk)"
}

_NAMES = {"sql": "SQL", "power_bi": "Power BI", "solar_pv": "Solar PV", "monitoring_evaluation": "M&E"}
def pretty(skill):
    return _NAMES.get(skill, skill.replace("_", " ").capitalize())