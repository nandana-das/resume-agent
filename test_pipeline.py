# test_pipeline.py
from graph.pipeline import run_pipeline

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

# Run the full pipeline with one call
result = run_pipeline(
    resume_text=sample_resume,
    jd_text=sample_jd,
    include_suggested_projects=True
)

# Print summary of all outputs
print("=" * 50)
print(f"Role detected: {result['parsed_jd']['role']}")
print(f"Resume score: {result['evaluation']['overall_score']}/10")
print(f"Gap analysis keys: {list(result['gap_analysis'].keys())}")
print(f"Full gap analysis: {result['gap_analysis']}")
print(f"\nFinal resume preview:")
print(result["final_resume"][:300] + "...")

# Check for errors
if result["error"]:
    print(f"\n❌ Error: {result['error']}")
else:
    print(f"\n✅ Pipeline status: {result['current_step']}")