# test_agent4.py
from agents.jd_parser import parse_jd
from agents.resume_evaluator import evaluate_resume
from agents.gap_analyst import analyze_gaps
from agents.resume_writer import write_resume

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
gap_analysis = analyze_gaps(sample_resume, parsed_jd, evaluation)
print("✅ Done\n")

# Step 4 — Agent 4
print("Running Agent 4 — Resume Writer...")
final_resume = write_resume(
    resume_text=sample_resume,
    parsed_jd=parsed_jd,
    evaluation=evaluation,
    gap_analysis=gap_analysis,
    include_suggested_projects=True
)
print("✅ Done\n")

# Print final resume
print("=" * 50)
print("FINAL TAILORED RESUME:")
print("=" * 50)
print(final_resume)

# Save to a txt file so you can read it easily
with open("final_resume_output.txt", "w") as f:
    f.write(final_resume)
print("\n📄 Resume also saved to final_resume_output.txt")