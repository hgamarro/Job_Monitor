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

# Running Jobs Tab
with tabs[0]:
    st.subheader("Running Jobs")
    if not running_jobs:
        st.info("No running jobs.")
    else:
        for job_id, job_data in running_jobs.items():
            with st.expander(f"Job ID: {job_id}"):
                st.write(f"**Status**: {job_data.get('status', 'Unknown')}")
                st.write(f"**Log Time**: {job_data.get('log_time', 'Unknown')}")
                st.write(f"**Log Step**: {job_data.get('log_step', 'Unknown')}")
                st.write(f"**Model Start Date**: {job_data.get('model_start_date', 'Unknown')}")
                st.write(f"**Model End Date**: {job_data.get('model_end_date', 'Unknown')}")
                st.write(f"**Elapsed Time (Hours)**: {job_data.get('elapsed_time_hours', 'Unknown')}")
                st.write(f"**Current Time Step**: {job_data.get('current_time_step', 'Unknown')}")
                st.write("**Average Time Per Domain**:")
                for domain, avg_time in job_data.get("average_elapsed_time_per_domain", {}).items():
                    st.write(f"  - Domain {domain}: {avg_time} seconds")
                slow_domains = job_data.get("slow_domains", [])
                st.write(f"**Slow Domains**: {', '.join(slow_domains) if slow_domains else 'None'}")

# Completed Runs Tab
with tabs[1]:
    st.subheader("Completed Runs")
    if not completed_jobs:
        st.info("No completed runs.")
    else:
        for job_id, job_data in completed_jobs.items():
            with st.expander(f"Job ID: {job_id}"):
                st.write(f"**Status**: {job_data.get('status', 'Unknown')}")
                st.write(f"**Created At**: {job_data.get('created_at', 'Unknown')}")
                st.write(f"**Finished At**: {job_data.get('finished_at', 'Unknown')}")
                st.write(f"**Total Runtime**: {job_data.get('total_runtime', 'Unknown')}")
                st.write(f"**Model Start Date**: {job_data.get('model_start_date', 'Unknown')}")
                st.write(f"**Model End Date**: {job_data.get('model_end_date', 'Unknown')}")
                st.write(f"**Elapsed Time (Hours)**: {job_data.get('elapsed_time_hours', 'Unknown')}")
                st.write(f"**Current Time Step**: {job_data.get('current_time_step', 'Unknown')}")
                st.write("**Average Time Per Domain**:")
                for domain, avg_time in job_data.get("average_elapsed_time_per_domain", {}).items():
                    st.write(f"  - Domain {domain}: {avg_time} seconds")
                slow_domains = job_data.get("slow_domains", [])
                st.write(f"**Slow Domains**: {', '.join(slow_domains) if slow_domains else 'None'}")

