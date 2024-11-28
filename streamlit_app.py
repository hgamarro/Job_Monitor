import streamlit as st
from google.cloud import firestore
google.oauth2 import service_account
import json

key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="job_monitor")
doc_ref = db.collection("completed_runs").document("FfncJd")
doc = doc_ref.get()
st.write("The id is: ", doc.id)
st.write("The contents are: ", doc.to_dict())


