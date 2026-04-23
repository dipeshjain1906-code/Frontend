import streamlit as st
import importlib
from backend_manager import ensure_backend_running

ensure_backend_running()

st.set_page_config(
    page_title="MedTrackPro | Clinical Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL STYLES + FONTAWESOME
# ─────────────────────────────────────────────
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  /* ── Root Tokens ───────────────────────────── */
  :root {
    --cyan:    #00d2ff;
    --purple:  #7b2cbf;
    --dark:    #1e1e2d;
    --card:    #27293d;
    --muted:   #a0a0b0;
    --border:  rgba(255,255,255,0.08);
  }
  /* ── Hide Streamlit chrome ─────────────────── */
  footer { visibility: hidden; }
  #MainMenu { visibility: hidden; }
  /* ── Global font ───────────────────────────── */
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  /* ── Main buttons ──────────────────────────── */
  div.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all .25s ease;
    border: 1px solid var(--border);
    padding: .45rem 1rem;
    height: auto !important;
  }
  div.stButton > button:hover {
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
    box-shadow: 0 4px 12px rgba(0,210,255,.18);
  }
  /* primary CTA */
  div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--cyan) 0%, #3a7bd5 100%);
    border: none; color: #fff;
  }
  div.stButton > button[kind="primary"]:hover {
    opacity: .9; color: #fff !important;
    box-shadow: 0 4px 16px rgba(0,210,255,.35);
  }
  /* ── Sidebar nav buttons ───────────────────── */
  [data-testid="stSidebar"] div.stButton > button {
    width: 100%;
    text-align: left;
    justify-content: flex-start;
    background: transparent;
    border: none;
    border-radius: 0 8px 8px 0;
    padding: 10px 16px;
    color: #c8c8d8;
    font-size: .93rem;
  }
  [data-testid="stSidebar"] div.stButton > button:hover {
    background: rgba(0,210,255,.07);
    color: #fff !important;
    border-left: 3px solid var(--cyan) !important;
    box-shadow: none;
  }
  /* ── Metric cards ──────────────────────────── */
  [data-testid="stMetric"] {
    background: var(--card);
    padding: 15px 20px;
    border-radius: 10px;
    border-left: 4px solid var(--cyan);
    box-shadow: 0 4px 8px rgba(0,0,0,.15);
  }
  [data-testid="stMetricLabel"] { font-size: 15px !important; color: var(--muted); }
  [data-testid="stMetricValue"] { font-size: 30px !important; font-weight: 700; }
  /* ── Feature cards ─────────────────────────── */
  .feature-card {
    background: var(--card);
    padding: 28px 24px;
    border-radius: 12px;
    text-align: center;
    border-top: 3px solid transparent;
    transition: transform .2s ease, border-top-color .2s ease;
    height: 100%;
  }
  .feature-card:hover { transform: translateY(-5px); border-top-color: var(--cyan); }
  .feature-card i { font-size: 36px; color: var(--cyan); margin-bottom: 14px; }
  .feature-card h3 { margin-top: 0; font-size: 1.15rem; }
  .feature-card p  { color: var(--muted); font-size: .92rem; margin: 0; }
  /* ── Patient context banner ────────────────── */
  .patient-banner {
    background: var(--card);
    border-left: 5px solid var(--cyan);
    padding: 12px 18px;
    border-radius: 0 10px 10px 0;
    margin-bottom: 18px;
    font-size: .97rem;
  }
  .patient-banner strong { color: var(--cyan); font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "page":       "Home",
        "patient_id": None,
        "patient_name": None,
        "check_status": "pending",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# HELPER: navigate without re-importing modules
# ─────────────────────────────────────────────
def go(page, patient_id=None, patient_name=None):
    st.session_state.page = page
    if patient_id is not None:
        st.session_state.patient_id = patient_id
        st.session_state.patient_name = patient_name
    st.rerun()

def clear_patient():
    st.session_state.patient_id   = None
    st.session_state.patient_name = None
    st.session_state.page = "Patient Dashboard"
    st.session_state.check_status = "pending"
    st.rerun()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
      <span style='font-size:28px; color:#00d2ff;'>
        <i class='fa-solid fa-staff-snake'></i>
      </span>
      <h2 style='color:#00d2ff; font-weight:800; margin:4px 0 0; font-size:1.4rem;'>
        MedTrackPro
      </h2>
      <div style='color:#a0a0b0; font-size:.78rem; margin-top:2px;'>Clinical Decision Support</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    patient_active = st.session_state.patient_id is not None

    # ── MODE A: No patient selected → Global Nav ──
    if not patient_active:
        st.markdown("<div style='color:#a0a0b0; font-size:.8rem; font-weight:600; letter-spacing:.08em; padding: 4px 16px 8px;'>GLOBAL</div>", unsafe_allow_html=True)

        global_nav = [
            ("Home",               "fa-solid fa-house"),
            ("Patient Dashboard",  "fa-solid fa-users-rectangle"),
            ("Add Patient",        "fa-solid fa-user-plus"),
            ("Add Vaccine",        "fa-solid fa-syringe"),
            ("Add Contraindication","fa-solid fa-ban"),
            ("SQL Showcase",       "fa-solid fa-database"),
        ]

        for label, icon in global_nav:
            is_active = st.session_state.page == label
            if is_active:
                st.markdown(f"""
                <div style="background:rgba(0,210,255,.12); border-left:4px solid #00d2ff;
                     padding:10px 16px; border-radius:0 8px 8px 0; font-weight:600;
                     color:#fff; margin-bottom:4px; font-size:.93rem;">
                  <i class="{icon}" style="width:22px; color:#00d2ff; margin-right:8px;"></i>{label}
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"  {label}", key=f"nav_{label}", use_container_width=True):
                    go(label)

    # ── MODE B: Patient selected → Patient Nav ──
    else:
        st.markdown(f"""
        <div class='patient-banner'>
          <div style='color:#a0a0b0; font-size:.78rem; font-weight:600; letter-spacing:.08em;'>ACTIVE PATIENT</div>
          <strong>{st.session_state.patient_name}</strong><br>
          <span style='color:#a0a0b0; font-size:.82rem;'>ID: {st.session_state.patient_id}</span>
        </div>
        """, unsafe_allow_html=True)

        patient_nav = [
            ("Home",               "fa-solid fa-house"),
            ("Patient Dashboard",  "fa-solid fa-chart-line"),
            ("Add Allergy",        "fa-solid fa-triangle-exclamation"),
            ("Add Immunization",   "fa-solid fa-shield-virus"),
            ("Record Reaction",    "fa-solid fa-heart-crack"),
        ]

        for label, icon in patient_nav:
            is_active = st.session_state.page == label
            if is_active:
                st.markdown(f"""
                <div style="background:rgba(0,210,255,.12); border-left:4px solid #00d2ff;
                     padding:10px 16px; border-radius:0 8px 8px 0; font-weight:600;
                     color:#fff; margin-bottom:4px; font-size:.93rem;">
                  <i class="{icon}" style="width:22px; color:#00d2ff; margin-right:8px;"></i>{label}
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"  {label}", key=f"nav_p_{label}", use_container_width=True):
                    if label == "Home":
                        st.session_state.patient_id = None
                        st.session_state.patient_name = None
                        st.session_state.check_status = "pending"
                    go(label)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("⬅  Change Patient", key="nav_back", use_container_width=True):
            clear_patient()

# ─────────────────────────────────────────────
# PAGE ROUTER  — importlib ensures fresh exec
# ─────────────────────────────────────────────
page = st.session_state.page

MODULE_MAP = {
    "Home":                ("home",                        None),
    "Patient Dashboard":   ("dashboard",                   None),
    "Add Patient":         ("QuickActions.add_patient",    None),
    "Add Vaccine":         ("QuickActions.add_vaccine",    None),
    "Add Contraindication":("QuickActions.add_contraindication", None),
    "Add Allergy":         ("QuickActions.add_allergy",    None),
    "Add Immunization":    ("QuickActions.add_immunization",None),
    "Record Reaction":     ("QuickActions.record_reaction",None),
    "SQL Showcase":        ("QuickActions.sql_showcase",   None),
}

if page in MODULE_MAP:
    mod_path, _ = MODULE_MAP[page]
    mod = importlib.import_module(mod_path)
    importlib.reload(mod)   # always re-execute so state is fresh
    if hasattr(mod, "show"):
        mod.show()
else:
    st.error(f"Page '{page}' not found.")
