# Kvalitetssystem i Streamlit - Alt-i-én
# Funktioner: Opret K-Note, se dashboard, responsloop (R-Loop)
# Krav: Streamlit, pandas, os, datetime, json

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

# --- Konfiguration ---
K_NOTE_FOLDER = "data/k_notes"
R_LOOP_FOLDER = "data/r_loops"
os.makedirs(K_NOTE_FOLDER, exist_ok=True)
os.makedirs(R_LOOP_FOLDER, exist_ok=True)

# --- Hjælpefunktioner ---
def gem_json(data, folder, filename):
    with open(os.path.join(folder, filename), "w") as f:
        json.dump(data, f, indent=4)

def hent_k_notes():
    notes = []
    for file in os.listdir(K_NOTE_FOLDER):
        with open(os.path.join(K_NOTE_FOLDER, file)) as f:
            notes.append(json.load(f))
    return pd.DataFrame(notes)

def hent_r_loops():
    loops = []
    for file in os.listdir(R_LOOP_FOLDER):
        with open(os.path.join(R_LOOP_FOLDER, file)) as f:
            loops.append(json.load(f))
    return pd.DataFrame(loops)

# --- Navigation ---
st.set_page_config(page_title="Kvalitetssystem", layout="wide")
valg = st.sidebar.radio("Vælg funktion", ["Opret K-Note", "Se Dashboard", "Responsloop"])

# --- Opret K-Note ---
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
        filename = f"{timestamp}_{saelger}.json"
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
        gem_json(data, K_NOTE_FOLDER, filename)
        st.success("K-Note gemt")

# --- Se Dashboard ---
elif valg == "Se Dashboard":
    st.title("Kvalitetsdashboard")
    df = hent_k_notes()
    if df.empty:
        st.info("Ingen K-Notes endnu.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Totalt antal K-Notes", len(df))
            top_brud = df.explode("brud")["brud"].value_counts().head(3)
            st.write("**Top 3 brud:**", top_brud)
        with col2:
            manglende_svar = df[df["status"] == "Afventer svar"]
            st.metric("Afventer svar", len(manglende_svar))

        st.subheader("Oversigt")
        st.dataframe(df.sort_values(by="timestamp", ascending=False))

# --- Responsloop ---
elif valg == "Responsloop":
    st.title("Responsloop")
    df = hent_k_notes()
    afventer = df[df["status"] == "Afventer svar"]

    if afventer.empty:
        st.success("Ingen K-Notes kræver svar.")
    else:
        valgt = st.selectbox("Vælg K-Note", afventer["timestamp"] + " – " + afventer["saelger"])
        note = afventer[afventer["timestamp"] == valgt.split(" – ")[0]].iloc[0]

        st.write(f"**Sælger:** {note['saelger']}")
        st.write(f"**Dato:** {note['dato']}")
        st.write(f"**Brud:** {', '.join(note['brud'])}")
        st.write(f"**Kommentar:** {note['kommentar']}")
        st.write(f"**Anbefaling:** {note['anbefaling']}")

        svar = st.radio("Vælg handling", ["✅ Accepteret", "❓ Uenig", "📞 Book møde"])
        svar_tekst = ""
        if svar == "❓ Uenig":
            svar_tekst = st.text_area("Begrundelse")

        if st.button("Send svar"):
            note["status"] = svar
            note["svar_tekst"] = svar_tekst
            gem_json(note, K_NOTE_FOLDER, f"{note['timestamp']}_{note['saelger']}.json")
            gem_json(note, R_LOOP_FOLDER, f"rloop_{note['timestamp']}_{note['saelger']}.json")
            st.success("Svar gemt og opdateret")
