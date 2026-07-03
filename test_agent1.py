from agents.jd_parser import parse_jd
import json

sample_jd = """
We are looking for a Data Scientist with 3+ years experience.
Required: Python, Machine Learning, SQL, TensorFlow, Docker.
Preferred: AWS, Spark, Kubernetes.
"""

result = parse_jd(sample_jd)
print(json.dumps(result, indent=2))