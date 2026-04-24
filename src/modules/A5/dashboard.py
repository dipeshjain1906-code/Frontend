import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from config import BASE_URL


@st.cache_data(ttl=30)
def fetch_patients():
    try:
        res = requests.get(f"{BASE_URL}/patients", timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return []


@st.cache_data(ttl=20)
def fetch_dashboard(patient_id):
    try:
        res = requests.get(f"{BASE_URL}/dashboard/{patient_id}", timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None


def show():
    # ─── If a patient is already selected in session state, jump straight to details ───
    if st.session_state.get("patient_id"):
        _show_patient_details(st.session_state.patient_id)
    else:
        _show_patient_list()


def _show_patient_list():
    st.markdown("""
    <h2 style='margin-bottom:4px;'>
      <i class='fa-solid fa-users-rectangle' style='color:#00d2ff'></i>  Patient Dashboard
    </h2>
    <div style='color:#a0a0b0; margin-bottom:20px;'>Select a patient to view their full clinical profile.</div>
    """, unsafe_allow_html=True)

    patients = fetch_patients()

    if not patients:
        st.warning("No patients found. Please add a patient first.")
        if st.button("➕ Add Patient"):
            st.session_state.page = "Add Patient"
            st.rerun()
        return

    # ── Summary metrics ──────────────────────────────────
    col1, col2 = st.columns(2)
    col1.metric("Total Patients Registered", len(patients))
    col2.metric("System Status", "🟢 Online")

    st.markdown("---")
    st.markdown("### Select a Patient")

    # ── Searchable selectbox ─────────────────────────────
    options = {f"{p['Name']}  |  ID: {p['PatientID']}": p for p in patients}
    chosen_label = st.selectbox(
        "🔍 Search by name or ID",
        options=list(options.keys()),
        index=None,
        placeholder="Type to search..."
    )

    if not chosen_label:
        st.info("Select a patient above to open their clinical profile.")
        return

    patient = options[chosen_label]

    if st.button("Open Patient Profile →", type="primary"):
        st.session_state.patient_id   = patient["PatientID"]
        st.session_state.patient_name = patient["Name"]
        st.session_state.page = "Patient Dashboard"
        st.rerun()


def _show_patient_details(patient_id):
    with st.spinner("Loading clinical data..."):
        data = fetch_dashboard(patient_id)

    if not data:
        st.error("Failed to load patient data. Check that the Flask server is running.")
        if st.button("⬅  Back to Patient List"):
            st.session_state.patient_id = None
            st.session_state.patient_name = None
            st.rerun()
        return

    p = data["patient"]

    # ── Patient header ───────────────────────────────────
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:18px; margin-bottom:16px;'>
      <div style='background:#27293d; border-radius:50%; width:64px; height:64px;
                  display:flex; align-items:center; justify-content:center; font-size:28px;
                  border: 2px solid #00d2ff;'>
        <i class='fa-solid fa-user-injured' style='color:#00d2ff'></i>
      </div>
      <div>
        <h2 style='margin:0; font-size:1.6rem;'>{p['Name']}</h2>
        <div style='color:#a0a0b0; font-size:.9rem;'>
          ID: <strong>{p['PatientID']}</strong> &nbsp;·&nbsp;
          DOB: {p.get('DateOfBirth','N/A')} &nbsp;·&nbsp;
          Gender: {p.get('Gender','N/A')}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Action buttons ───────────────────────────────────
    a1, a2, a3 = st.columns(3)
    with a1:
        if st.button("➕ Add Allergy", use_container_width=True):
            st.session_state.page = "Add Allergy"
            st.rerun()
    with a2:
        if st.button("💉 Add Immunization", use_container_width=True, type="primary"):
            st.session_state.page = "Add Immunization"
            st.rerun()
    with a3:
        if st.button("⚠️ Record Reaction", use_container_width=True):
            st.session_state.page = "Record Reaction"
            st.rerun()

    st.markdown("---")

    # ── KPI Cards ────────────────────────────────────────
    allergies     = data.get("allergies", [])
    immunizations = data.get("immunizations", [])
    reactions     = data.get("reactions", [])

    overdue = 0
    for imm in immunizations:
        nd = imm.get("NextDueDate")
        if nd:
            try:
                if datetime.strptime(nd, "%Y-%m-%d") < datetime.now():
                    overdue += 1
            except Exception:
                pass

    k1, k2, k3 = st.columns(3)
    k1.metric("⚠️ Total Allergies",     len(allergies))
    k2.metric("💉 Total Doses Taken",    len(immunizations))
    k3.metric("⏰ Overdue Vaccines",     overdue)

    st.markdown("---")

    # ── Allergies ─────────────────────────────────────────
    st.markdown("### ⚠️ Allergies")
    if allergies:
        for a in allergies:
            lvl = a.get("SeverityLevel", "Mild")
            msg = f"**{a['AllergyName']}** &nbsp;·&nbsp; *{a['AllergyType']}* &nbsp;·&nbsp; Severity: {lvl}"
            if lvl in ("Severe", "Anaphylaxis"):
                st.error(msg)
            elif lvl == "Moderate":
                st.warning(msg)
            else:
                st.success(msg)
    else:
        st.info("No allergies recorded.")

    st.markdown("---")

    # ── Immunization History ──────────────────────────────
    st.markdown("### 💉 Immunization History")
    if immunizations:
        df = pd.DataFrame(immunizations)
        show_cols = [c for c in ["VaccineID","DoseNumber","AdministrationDate","NextDueDate"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True)
    else:
        st.info("No immunizations recorded.")

    st.markdown("---")

    # ── Schedule status ───────────────────────────────────
    st.markdown("### 📅 Schedule Status")
    if immunizations:
        for imm in immunizations:
            nd = imm.get("NextDueDate")
            if not nd:
                continue
            try:
                due = datetime.strptime(nd, "%Y-%m-%d")
                if due < datetime.now():
                    st.error(f"**OVERDUE** — {imm['VaccineID']} (Was due {nd})")
                else:
                    st.success(f"**Upcoming** — {imm['VaccineID']} (Due {nd})")
            except Exception:
                pass
    else:
        st.info("No active schedules.")

    st.markdown("---")

    # ── Adverse Reactions ─────────────────────────────────
    st.markdown("### ⚠️ Adverse Reactions")
    if reactions:
        r_df = pd.DataFrame(reactions)
        r_cols = [c for c in ["VaccineID","ReactionDate","SeverityLevel","ReactionDescription","ActionTaken"] if c in r_df.columns]
        st.dataframe(r_df[r_cols], use_container_width=True)
    else:
        st.info("No adverse reactions recorded.")