# Kvalitetssystem i Streamlit - med Google Sheets integration og fejlhåndtering
# Funktioner: Opret K-Note (gemmes i Google Sheets)
# Krav: streamlit, pandas, gspread, oauth2client

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets Opsætning ---
SHEET_NAME = "Kvalitets-KNotes"  # Navnet på dit Google Sheet

# --- Google API adgang ---
# Upload din credentials json til Streamlit Secrets: ["gspread_service_account"]
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gspread_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# --- Funktion: Gem K-Note til Google Sheets ---
def gem_k_note_to_sheets(data):
    try:
        sheet.append_row([
            data["timestamp"],
            data["saelger"],
            data["dato"],
            data["tid"],
            data["opkalds_id"],
            data["score"],
            ", ".join(data["brud"]),
            data["kommentar"],
            data["anbefaling"],
            data["status"]
        ])
        st.success("K-Note gemt i Google Sheets ✅")
    except Exception as e:
        st.error(f"❌ FEJL: {e}")

# --- UI Start ---
st.set_page_config(page_title="Kvalitetssystem", layout="wide")
valg = st.sidebar.radio("Vælg funktion", ["Opret K-Note"])

if valg == "Opret K-Note":
    st.title("Opret K-Note")

    col1, col2 = st.columns(2)
    with col1:
        saelger = st.text_input("Sælgernavn")
        opkalds_id = st.text_input("Opkalds-ID eller link")
        score = st.slider("Score", 0, 5, 3)
    with col2:
        dato = st.date_input("Dato", value=datetime.today())
        tidspunkt = st.time_input("Tidspunkt", value=datetime.now().time())

    st.subheader("Brudstyper")
    brud = st.multiselect("Vælg relevante brud", [
        "Misvisende info", "Overdrivelse", "Manglende accept", "Uklar vilkår"])

    kommentar = st.text_area("Kommentar")
    anbefaling = st.text_input("Anbefalet handling")

    if st.button("Gem K-Note"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data = {
            "saelger": saelger,
            "dato": str(dato),
            "tid": str(tidspunkt),
            "opkalds_id": opkalds_id,
            "score": score,
            "brud": brud,
            "kommentar": kommentar,
            "anbefaling": anbefaling,
            "status": "Afventer svar",
            "timestamp": timestamp
        }
        gem_k_note_to_sheets(data)
