# test_agent3.py
from agents.jd_parser import parse_jd
from agents.resume_evaluator import evaluate_resume
from agents.gap_analyst import analyze_gaps
import json

# Sample JD
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

# Step 1 — Agent 1
print("Running Agent 1 — JD Parser...")
parsed_jd = parse_jd(sample_jd)
print("✅ Done\n")

# Step 2 — Agent 2
print("Running Agent 2 — Resume Evaluator...")
evaluation = evaluate_resume(sample_resume, parsed_jd)
print("✅ Done\n")

# Step 3 — Agent 3
print("Running Agent 3 — Gap Analyst...")
gaps = analyze_gaps(sample_resume, parsed_jd, evaluation)
print("✅ Done\n")

# Print results
print("=" * 50)
print("WHAT THEY REALLY WANT:")
for item in gaps["what_they_want"]:
    print(f"  → {item}")

print("\nCRITICAL GAPS:")
for g in gaps["critical_gaps"]:
    print(f"  ❌ {g['gap']}")
    print(f"     Priority: {g['importance']}")
    print(f"     Fix: {g['how_to_fix']}\n")

print("SUGGESTED PROJECTS:")
for i, p in enumerate(gaps["suggested_projects"], 1):
    print(f"  {i}. {p['title']}")
    print(f"     Tech: {', '.join(p['tech_stack'])}")
    print(f"     Why: {p['why_it_helps']}")
    print(f"     Metric: {p['sample_metric']}\n")

print("QUICK WINS:")
for qw in gaps["quick_wins"]:
    print(f"  ✅ {qw}")