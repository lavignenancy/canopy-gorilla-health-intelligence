import streamlit as st
import pandas as pd
import numpy as np
import os
from vulnerability_model import calculate_environmental_risk
from pdf_curator import curate_knowledge_base
import data_cleaner

st.set_page_config(page_title="CANOPY Vet Portal", layout="wide", page_icon="🦍")

st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .stTabs [data-baseweb="tab-list"] { gap: 16px; }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: #ffffff;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .stTabs [aria-selected="true"] {
        background-color: #10b981 !important;
        color: white !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
    }
    .stButton>button {
        background-color: #10b981;
        color: white;
        border-radius: 6px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🦍 CANOPY Platform")
st.markdown("### Gorilla Health Case Continuity & Environmental Intelligence")

st.sidebar.header("📍 Sector Tracking Controls")
selected_sector = st.sidebar.selectbox("Select Park Ranging Sector", ["Sector A (Karisoke Core)", "Sector B (Mikeno Slopes)", "Sector C (Visoke High Ridge)"])
elevation_map = {"Sector A (Karisoke Core)": 3100, "Sector B (Mikeno Slopes)": 2850, "Sector C (Visoke High Ridge)": 3400}

st.sidebar.metric(label="Current Altitude Alignment", value=f"{elevation_map[selected_sector]} meters ASL")

tab1, tab2, tab3 = st.tabs(["📋 Vet Review Queue", "🗺️ Climate & Macro-Risk Mapping", "📚 Curated Knowledge Base (RAG)"])

mock_cases = pd.DataFrame({
    'Case ID': ['CASE-2026-04', 'CASE-2026-05'],
    'Gorilla Group': ['Susa-A', 'Pablo Group'],
    'Reported Signs': ['Mild coughing, lethargy', 'Sustained nasal discharge'],
    'Visibility Status': ['Clear View (Full Group)', 'Partial View (Dense Vegetation)'],
    'Confidence Score': ['High (Senior Tracker)', 'Medium'],
    'Sync Status': ['Acknowledged by Base', 'Seen']
})

with tab1:
    st.markdown("#### Active Health Triage Queue")
    st.dataframe(mock_cases, width="stretch")
    
    st.markdown("---")
    st.markdown("#### Action Center: Process Case `CASE-2026-04`")
    
    col1, col2 = st.columns(2)
    with col1:
        vet_decision = st.selectbox("Clinical Action Override", [
            "Escalate to Field Intervention (Deploy Vet Team)",
            "Routine Follow-up: Assign Daily Observation",
            "Maintain Passive Monitoring"
        ])
    with col2:
        override_reason = st.text_input("Reason Code for Model Optimization Audit Trail", placeholder="e.g., Symptoms consistent with seasonal weather stressor")
        
    if st.button("Submit Clinical Decision"):
        st.success(f"Decision logged successfully. Action: '{vet_decision}'. Audit Trail saved.")

with tab2:
    st.markdown("#### Environmental Risk Window Prediction")
    
    if not os.path.exists("master_climate_2000_2026.csv"):
        with st.spinner("Compiling clean 2000-2026 climate timeline..."):
            df_timeline = data_cleaner.generate_master_timeline()
            df_timeline.to_csv("master_climate_2000_2026.csv", index=False)
    else:
        df_timeline = pd.read_csv("master_climate_2000_2026.csv")
    
    df_timeline['date'] = pd.to_datetime(df_timeline['date'])
    min_date = df_timeline['date'].min().date()
    max_date = df_timeline['date'].max().date()
    
    selected_date = st.date_input("Select Historical Analysis Date to Audit Model Risk Window", 
                                  value=max_date, min_value=min_date, max_value=max_date)
    
    day_data = df_timeline[df_timeline['date'].dt.date == selected_date]
    
    if not day_data.empty:
        t_max = float(day_data['temperature_2m_max'].values[0])
        t_min = float(day_data['temperature_2m_min'].values[0])
        precip = float(day_data['precipitation_sum'].values[0])
        rh = float(day_data['relative_humidity_2m_max'].values[0])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Max Temp", f"{t_max} °C")
        m2.metric("Min Temp", f"{t_min} °C")
        m3.metric("Precipitation", f"{precip} mm")
        m4.metric("Max Humidity", f"{rh} %")
        
        risk_score = calculate_environmental_risk((t_max - t_min), precip, rh)
        
        if risk_score > 70:
            st.error(f"🚨 HIGH RISK WINDOW ALERT (Index Score: {risk_score:.1f}/100)")
        elif risk_score > 40:
            st.warning(f"⚠️ MODERATE RISK WINDOW (Index Score: {risk_score:.1f}/100)")
        else:
            st.success(f"✅ LOW RISK WINDOW (Index Score: {risk_score:.1f}/100)")

with tab3:
    st.markdown("#### Curated Vector Database Previews")
    
    raw_pdfs = [
        {'title': 'IUCN Great Ape Health Guidelines.pdf', 'sample_text': 'Guidelines for mountain gorilla field encounters, monitoring respiratory infection transmission.'},
        {'title': 'AZA Captive Husbandry Manual.pdf', 'sample_text': 'Captive guidelines for western lowland gorillas. Isolation protocols apply for respiratory containment.'},
        {'title': 'Study on Lipoprotein and Cardiovascular Risk.pdf', 'sample_text': 'Human cohorts showing markers for high lipoprotein cholesterol distribution.'},
        {'title': 'Duplicate Great Ape Guidelines.pdf', 'sample_text': 'Guidelines for mountain gorilla field encounters, monitoring respiratory infection transmission.'}
    ]
    
    curated = curate_knowledge_base(raw_pdfs)
    st.dataframe(pd.DataFrame(curated)[['title', 'curated_category']], width="stretch")
