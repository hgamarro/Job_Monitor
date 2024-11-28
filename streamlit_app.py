import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

st.set_page_config(page_title="Job Monitoring Dashboard", layout="wide")

# Helper function to load jobs from Firestore
def load_jobs(collection_name):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    jobs = {doc.id: doc.to_dict() for doc in docs}
    return jobs

# Helper function to display jobs using a DataFrame
def display_jobs(jobs, title):
    st.write(f"**{title}:**")
    if not jobs:
        st.info(f"No {title.lower()} available.")
    else:
        rows = []
        for job_id, data in jobs.items():
            average_times = ", ".join(
                [f"Domain {d}: {t:.2f}s" for d, t in data.get("average_elapsed_time_per_domain", {}).items()]
            )
            slow_domains = ", ".join(data.get("slow_domains", [])) or "None"
            row = {
                "Job ID": job_id,
                "Status": data.get("status", "Unknown"),
                "Log Time": data.get("log_time", "Unknown"),
                "Log Step": data.get("log_step", "Unknown"),
                "Model Start": data.get("model_start_date", "Unknown"),
                "Model End": data.get("model_end_date", "Unknown"),
                "Elapsed Time (Hours)": data.get("elapsed_time_hours", "Unknown"),
                "Current Time Step": data.get("current_time_step", "Unknown"),
                "Average Time Per Domain": average_times,
                "Slow Domains": slow_domains,
            }
            rows.append(row)

        # Create a DataFrame and display it using Streamlit
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

# Load jobs from Firestore
running_jobs = load_jobs("runs")
completed_jobs = load_jobs("completed_runs")

# Create tabs for Running Jobs and Completed Runs
st.title("Job Monitoring Dashboard")
tab1, tab2 = st.tabs(["Running Jobs", "Completed Runs"])

with tab1:
    display_jobs(running_jobs, "Running Jobs")

with tab2:
    display_jobs(completed_jobs, "Completed Runs")

