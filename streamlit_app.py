import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
from google.cloud.firestore_v1._helpers import DatetimeWithNanoseconds
import json
from datetime import datetime

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

def format_time(datetime_value):
    if isinstance(datetime_value, (datetime, DatetimeWithNanoseconds)):
        return datetime_value.strftime("%Y-%m-%d %H:%M")
    return "Unknown"  # Fallback for invalid or missing times

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
                "Log Time": format_time(data.get("log_time", "Unknown")),
                "Log Step": data.get("log_step", "Unknown")[:8],
                "Model Start": format_time(data.get("model_start_date", "Unknown")),
                "Model End": format_time(data.get("model_end_date", "Unknown")),
                "Model Time Step": format_time(data.get("current_time_step", "Unknown")),
                "Elapsed Time": data.get("elapsed_time_hours", "Unknown"),
                "Average Time": average_times,
                "Slow Domains": slow_domains,
            }
            rows.append(row)

        # Create a DataFrame and display it using Streamlit
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

def display_jobs_complete(jobs, title):
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
                "Log Time": format_time(data.get("log_time", "Unknown")),
                "Model Start": format_time(data.get("model_start_date", "Unknown")),
                "Model End": format_time(data.get("model_end_date", "Unknown")),
                "Elapsed Time": data.get("elapsed_time_hours", "Unknown"),
                "Average Time": average_times,
            }
            rows.append(row)

        # Create a DataFrame and display it using Streamlit
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)


# Add a refresh button
if st.button("Refresh Data"):
    st.rerun()

# Load jobs from Firestore
running_jobs = load_jobs("runs")
completed_jobs = load_jobs("completed_runs")

# Create tabs for Running Jobs and Completed Runs
st.title("Job Monitoring Dashboard")
tab1, tab2 = st.tabs(["Running Jobs", "Completed Runs"])

with tab1:
    display_jobs(running_jobs, "Running Jobs")

with tab2:
    display_jobs_complete(completed_jobs, "Completed Runs")

