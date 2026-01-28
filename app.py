import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np

from datetime import datetime
from faker import Faker

fake = Faker()


import uuid
import streamlit as st
from supabase_client import supabase

st.title("Clinical Trial Audit System")
st.caption("Real-time audit logging and AI-assisted anomaly detection for clinical trials")
action = st.text_input("Enter action")
source = st.selectbox("Source", ["frontend", "ai", "manual"])

if st.button("Submit"):
    data = {
        "action": action,
        "metadata": {"source": source}
    }
    supabase.table("audit_logs").insert(data).execute()
    st.success("Log saved successfully")

st.subheader("Audit Logs")
logs = supabase.table("audit_logs").select("*").order("created_at", desc=True).execute()
st.dataframe(logs.data)


st.set_page_config(
    page_title="Clinical EDC Intelligence Platform",
    page_icon="🧬",
    layout="wide"
)




st.markdown("""
<style>
body { background-color: #f8fafc; }
.block-container { padding-top: 1.5rem; }

.card {
    background: white;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.section-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: #0f172a;
}

.subtitle {
    color: #475569;
    font-size: 0.95rem;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

def generate_messy_clinical_data(n=30) -> pd.DataFrame:
    """
    Simulates real-world EDC messiness:
    - Missing fields
    - Out-of-range vitals
    - Inconsistent demographics
    """
    rows = []
    for _ in range(n):
        hr = np.random.choice(
            [fake.random_int(55, 120), fake.random_int(350, 1800), None],
            p=[0.7, 0.2, 0.1]
        )

        rows.append({
            "client_code": fake.bothify("SUBJ-###"),
            "age_years": np.random.choice([fake.random_int(18, 85), None]),
            "gender_text": np.random.choice(["Male", "Female", "M", "F", "Unknown"]),
            "heartRate": hr,
            "visit_date": fake.date_this_decade().strftime("%Y-%m-%d")
        })

    return pd.DataFrame(rows)


def map_to_sdtm(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Simplified SDTM-style mapping
    (AI/LLM-based mapping can replace this later)
    """
    return pd.DataFrame({
        "USUBJID": raw_df["client_code"],
        "AGE": raw_df["age_years"],
        "SEX": raw_df["gender_text"]
            .map({"Male": "M", "Female": "F", "M": "M", "F": "F"})
            .fillna("U"),
        "HR": raw_df["heartRate"],
        "VSDTC": raw_df["visit_date"]
    })

def agentic_risk_detection(sdtm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Perception → Reasoning → Action
    Explainable by design (regulatory safe)
    """
    alerts = []

    for _, row in sdtm_df.iterrows():
        if pd.notna(row["HR"]) and row["HR"] > 300:
            alerts.append({
                "USUBJID": row["USUBJID"],
                "Risk Category": "Safety",
                "Issue": "Improbable Heart Rate",
                "AI Reasoning": "Value exceeds known physiological limits.",
                "Recommended Action": "Immediate manual review"
            })

        if pd.isna(row["AGE"]):
            alerts.append({
                "USUBJID": row["USUBJID"],
                "Risk Category": "Data Quality",
                "Issue": "Missing Age",
                "AI Reasoning": "Age required for stratification and analysis.",
                "Recommended Action": "Query site"
            })

    return pd.DataFrame(alerts)


def log_audit_event(event: str, payload: dict) -> dict:
    return {
        "audit_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event,
        "details": payload
    }


st.markdown("## 🧬 Clinical EDC Intelligence Platform")
st.caption(
    "Agentic AI · SDTM Harmonization · Live Monitoring · Explainable Insights"
)
st.markdown("---")


tabs = st.tabs([
    "📝 Data Entry",
    "🧪 Synthetic Data",
    "📐 SDTM Mapping",
    "📡 Live Monitoring",
    "🤖 AI Insights",
    "📜 Audit Trail"
])


with tabs[0]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Rapid Clinical Data Entry</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    pid = c1.text_input("Patient ID (USUBJID)", "SUBJ-001")
    hr = c2.number_input("Heart Rate (bpm)", 0, 2000)

    if st.button("Submit Entry"):
        if hr > 300:
            st.error("🚨 Safety Alert: Implausible heart rate detected.")
        else:
            st.success("✅ Entry accepted.")

        st.session_state["audit"] = log_audit_event(
            "Manual Entry", {"USUBJID": pid, "HR": hr}
        )
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Synthetic EDC Dataset</div>", unsafe_allow_html=True)

    if st.button("Generate Synthetic Data"):
        st.session_state["raw_df"] = generate_messy_clinical_data()

    if "raw_df" in st.session_state:
        st.dataframe(st.session_state["raw_df"], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>SDTM Harmonization</div>", unsafe_allow_html=True)

    if "raw_df" in st.session_state:
        st.session_state["sdtm_df"] = map_to_sdtm(st.session_state["raw_df"])
        st.dataframe(st.session_state["sdtm_df"], use_container_width=True)
    else:
        st.info("Generate synthetic data first.")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[3]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Live Monitoring</div>", unsafe_allow_html=True)

    if "sdtm_df" in st.session_state:
        hr_vals = st.session_state["sdtm_df"]["HR"].dropna().tolist()

        components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <canvas id="liveChart"></canvas>
        <script>
        new Chart(document.getElementById('liveChart'), {{
            type: 'line',
            data: {{
                labels: {list(range(len(hr_vals)))},
                datasets: [{{
                    label: 'Heart Rate (bpm)',
                    data: {hr_vals},
                    borderColor: '#2563eb',
                    tension: 0.35
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: 'Patient Vital Trends' }}
                }}
            }}
        }});
        </script>
        """, height=420)
    else:
        st.info("No SDTM data available.")
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[4]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>AI Insights</div>", unsafe_allow_html=True)

    if "sdtm_df" in st.session_state:
        risks = agentic_risk_detection(st.session_state["sdtm_df"])
        st.session_state["risks"] = risks

        if not risks.empty:
            counts = risks["Risk Category"].value_counts()

            components.html(f"""
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <canvas id="riskChart"></canvas>
            <script>
            new Chart(document.getElementById('riskChart'), {{
                type: 'doughnut',
                data: {{
                    labels: {counts.index.tolist()},
                    datasets: [{{
                        data: {counts.values.tolist()},
                        backgroundColor: ['#ef4444', '#facc15']
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{ display: true, text: 'AI Risk Distribution' }}
                    }}
                }}
            }});
            </script>
            """, height=360)

            st.dataframe(
                risks[["USUBJID", "Issue", "AI Reasoning", "Recommended Action"]],
                use_container_width=True
            )
        else:
            st.success("No risks detected.")
    else:
        st.info("Generate and standardize data first.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[5]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Audit Trail</div>", unsafe_allow_html=True)

    if "audit" in st.session_state:
        st.json(st.session_state["audit"])
    else:
        st.info("No audit events yet.")
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("---")
st.caption( 
    "Future-ready architecture: LLM agents, federated learning, homomorphic "
    "encryption, and real-time streaming can be layered without refactoring."
)
st.markdown("---")
st.subheader("System Intelligence & Compliance Risk Assessment")

try:
    logs = (
        supabase.table("audit_logs")
        .select("action, created_at, metadata")
        .order("created_at", desc=True)
        .limit(100)
        .execute()
        .data
    )
except Exception as e:
    logs = []

if not logs:
    st.info(
        "No audit events available for compliance risk assessment."
    )
else:
    actions = [log["action"].strip().lower() for log in logs]
    total_events = len(actions)

    risk_keywords = ["error", "fail", "unauthorized", "override", "deleted"]
    risk_events = [
        a for a in actions
        if any(keyword in a for keyword in risk_keywords)
    ]

    activity_rate = "Normal"
    risk_level = "Low"

    if total_events >= 50:
        activity_rate = "High"
        risk_level = "Medium"

    if risk_events:
        risk_level = "High"

    if risk_level == "High":
        st.error(
            "High compliance risk detected based on recent audit patterns. "
            "Immediate review of system activity is recommended."
        )
    elif risk_level == "Medium":
        st.warning(
            "Moderate compliance risk detected due to elevated audit activity. "
            "Periodic review is advised."
        )
    else:
        st.success(
            "System audit activity is within acceptable compliance thresholds."
        )

    with st.expander("Compliance Risk Summary"):
        st.write(f"Total audit events analyzed: {total_events}")
        st.write(f"Events containing risk indicators: {len(risk_events)}")
        st.write(f"Detected activity rate: {activity_rate}")
        st.write(f"Overall compliance risk level: {risk_level}")



