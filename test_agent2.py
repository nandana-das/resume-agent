# test_agent2.py
from agents.jd_parser import parse_jd
from agents.resume_evaluator import evaluate_resume
import json

# Sample JD — same as before
sample_jd = """
We are looking for a Data Scientist with 3+ years of experience.
Required skills: Python, Machine Learning, SQL, TensorFlow, Docker.
Preferred: AWS, Spark, Kubernetes.
Responsibilities: Build ML models, deploy to production, work with product teams.
Education: BTech in Computer Science or related field.
"""

# Sample Resume
sample_resume = """
Akash Sharma
akash@email.com | Chennai, India

EXPERIENCE
Data Scientist — ABB (2022 - Present)
- Built predictive models using Python and Scikit-learn
- Worked with SQL databases for data extraction
- Created dashboards for business stakeholders

SKILLS
Python, SQL, Scikit-learn, Pandas, Power BI

EDUCATION
BTech Computer Science — VIT University 2022

PROJECTS
Customer Churn Prediction
- Built a classification model using Python and Scikit-learn
- Achieved 85% accuracy on test data
"""

# Step 1 — Run Agent 1 first to get parsed JD
print("Running Agent 1...")
parsed_jd = parse_jd(sample_jd)
print("✅ JD Parsed\n")

# Step 2 — Run Agent 2 with resume + parsed JD
print("Running Agent 2...")
result = evaluate_resume(sample_resume, parsed_jd)
print("✅ Resume Evaluated\n")

# Print results
print(f"Overall Score: {result['overall_score']}/10")
print(f"\nBreakdown:")
for key, val in result['breakdown'].items():
    print(f"  {key}: {val}/10")
print(f"\nMatched Skills: {result['matched_skills']}")
print(f"Missing Skills: {result['missing_skills']}")
print(f"\nVerdict: {result['verdict']}")