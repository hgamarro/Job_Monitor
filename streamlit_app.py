import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
import json

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

# Page title
st.title("Job Monitoring Dashboard")

# Retrieve Firestore collections
def get_jobs_from_firestore(collection_name):
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    jobs = {doc.id: doc.to_dict() for doc in docs}
    return jobs

# Fetch running and completed jobs
running_jobs = get_jobs_from_firestore("runs")
completed_jobs = get_jobs_from_firestore("completed_runs")

# Create tabs for running and completed jobs
tabs = st.tabs(["Running Jobs", "Completed Runs"])

# Helper function to display jobs in a table
def display_jobs(jobs, title):
    if not jobs:
        st.info(f"No {title.lower()}.")
    else:
        st.write(f"**{title}:**")
        # Table header
        st.write(
            """
            <style>
            table {width: 100%; border-collapse: collapse;}
            th, td {border: 1px solid #ddd; padding: 8px;}
            th {text-align: left; background-color: #f2f2f2;}
            </style>
            """,
            unsafe_allow_html=True,
        )
        table = """
        <table>
        <thead>
            <tr>
                <th>Job ID</th>
                <th>Status</th>
                <th>Log Time</th>
                <th>Log Step</th>
                <th>Model Start</th>
                <th>Model End</th>
                <th>Elapsed Time (Hours)</th>
                <th>Current Time Step</th>
                <th>Average Time Per Domain</th>
                <th>Slow Domains</th>
            </tr>
        </thead>
        <tbody>
        """
        for job_id, data in jobs.items():
            average_times = ", ".join(
                [f"Domain {d}: {t:.2f}s" for d, t in data.get("average_elapsed_time_per_domain", {}).items()]
            )
            slow_domains = ", ".join(data.get("slow_domains", [])) or "None"
            row = f"""
            <tr>
                <td>{job_id}</td>
                <td>{data.get('status', 'Unknown')}</td>
                <td>{data.get('log_time', 'Unknown')}</td>
                <td>{data.get('log_step', 'Unknown')}</td>
                <td>{data.get('model_start_date', 'Unknown')}</td>
                <td>{data.get('model_end_date', 'Unknown')}</td>
                <td>{data.get('elapsed_time_hours', 'Unknown')}</td>
                <td>{data.get('current_time_step', 'Unknown')}</td>
                <td>{average_times}</td>
                <td>{slow_domains}</td>
            </tr>
            """
            table += row
        table += "</tbody></table>"
        st.write(table, unsafe_allow_html=True)

# Running Jobs Tab
with tabs[0]:
    display_jobs(running_jobs, "Running Jobs")

# Completed Runs Tab
with tabs[1]:
    display_jobs(completed_jobs, "Completed Runs")

