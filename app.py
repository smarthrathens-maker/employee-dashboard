import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ergani_export import generate_ergani_file
from auth import login

# --- Login ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if not st.session_state["authenticated"]:
    login()
    st.stop()

# --- Φόρτωση δεδομένων ---
financials = pd.read_csv("export_financials.csv", sep=";")
performance = pd.read_csv("export_performance.csv", sep=";")

# --- Προεπεξεργασία ---
financials["Total Amount (w.o. tips)"] = financials["Total Amount (w.o. tips)"].replace("€", "", regex=True).str.replace(",", ".").astype(float)
performance["Deliveries"] = performance["Deliveries"].astype(int)

# --- Υπολογισμός ενσήμου ---
def stamp_category(amount):
    if amount <= 300:
        return "2ωρο"
    elif amount <= 600:
        return "4ωρο"
    elif amount <= 900:
        return "6ωρο"
    else:
        return "8ωρο"

financials["Stamp Category"] = financials["Total Amount (w.o. tips)"].apply(stamp_category)

# --- Συγχώνευση ---
merged = pd.merge(financials, performance, on="Id", suffixes=("_fin", "_perf"))

# --- UI ---
st.set_page_config(page_title="Απόδοση Εργαζομένων", layout="wide")
st.title("📊 Απόδοση & Τζίρος Εργαζομένων")

period = st.selectbox("Περίοδος:", ["01/10 - 15/10/2025"])
employee = st.selectbox("Εργαζόμενος:", ["Όλοι"] + list(merged["Name_fin"].unique()))
stamp_filter = st.multiselect("Κατηγορία Ενσήμου:", ["2ωρο", "4ωρο", "6ωρο", "8ωρο"], default=["2ωρο", "4ωρο", "6ωρο", "8ωρο"])

filtered = merged[merged["Stamp Category"].isin(stamp_filter)]
if employee != "Όλοι":
    filtered = filtered[filtered["Name_fin"] == employee]

# --- Γράφημα ---
fig = go.Figure()
fig.add_trace(go.Bar(
    x=filtered["Name_fin"],
    y=filtered["Total Amount (w.o. tips)"],
    name="Τζίρος",
    marker_color=[
        "#e74c3c" if cat == "2ωρο" else
        "#f39c12" if cat == "4ωρο" else
        "#3498db" if cat == "6ωρο" else
        "#2ecc71" for cat in filtered["Stamp Category"]
    ]
))
fig.add_trace(go.Scatter(
    x=filtered["Name_fin"],
    y=filtered["Deliveries"],
    name="Παραδόσεις",
    mode="lines+markers",
    marker=dict(color="gray")
))
fig.update_layout(title="Τζίρος & Παραδόσεις", xaxis_title="Εργαζόμενος", yaxis_title="Τζίρος (€)")
st.plotly_chart(fig, use_container_width=True)

# --- KPIs ---
st.subheader("📌 KPIs")
st.dataframe(filtered[["Name_fin", "Deliveries", "TAR", "DAT", "Total idle time"]].rename(columns={"Name_fin": "Εργαζόμενος"}))

# --- Εξαγωγή ΕΡΓΑΝΗ ---
csv = generate_ergani_file(filtered)
st.download_button("📁 Εξαγωγή για ΕΡΓΑΝΗ", data=csv, file_name="ergani_export.csv", mime="text/csv")
