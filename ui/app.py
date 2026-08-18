import streamlit as st
import tempfile

from graph.workflow import build_workflow

from tools.csv_parser import CSVParser
from tools.validators import TransactionValidator
from tools.transaction_normalizer import TransactionNormalizer


st.set_page_config(
    page_title="AI Financial Planner",
    page_icon="💰",
    layout="wide",
)

@st.cache_resource
def get_workflow():
    print("Building LangGraph workflow...", flush=True)
    workflow = build_workflow()
    print("LangGraph workflow built.", flush=True)
    return workflow

csv_parser = CSVParser()
validator = TransactionValidator()
normalizer = TransactionNormalizer()

workflow = get_workflow()


# ─────────────────────────────────────────────────────────
# Pipeline flow-diagram helpers
# ─────────────────────────────────────────────────────────

PIPELINE_STEPS = [
    ("📂", "Parse Date"),
    ("✅", "Validate"),
    ("⚙️", "Normalize"),
    ("📊", "Analyse"),
    ("💡", "Recommend"),
    ("📝", "Report"),
]

_PIPELINE_CSS = """
<style>
@keyframes pulse-ring {
  0%   { box-shadow: 0 0 0 0 rgba(99,179,237,.7); }
  70%  { box-shadow: 0 0 0 8px rgba(99,179,237,0); }
  100% { box-shadow: 0 0 0 0 rgba(99,179,237,0); }
}
.pipeline-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 10px 0 6px;
  font-family: 'Inter', 'Segoe UI', sans-serif;
}
.pip-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 68px;
}
.pip-icon {
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
  border: 2px solid transparent;
  transition: background .3s, border-color .3s;
}
.pip-icon.pending { background: #1e2a38; border-color: #2d3d50; color: #4a6077; }
.pip-icon.active  { background: #1a3a5c; border-color: #63b3ed; color: #fff;
                    animation: pulse-ring 1.4s ease-out infinite; }
.pip-icon.done    { background: #153a28; border-color: #38a169; color: #68d391; }
.pip-icon.error   { background: #3a1515; border-color: #e53e3e; color: #fc8181; }
.pip-label {
  font-size: 10px; font-weight: 600; letter-spacing: .03em;
  white-space: nowrap;
}
.pip-label.pending { color: #4a6077; }
.pip-label.active  { color: #90cdf4; }
.pip-label.done    { color: #68d391; }
.pip-label.error   { color: #fc8181; }
.pip-connector {
  flex: 1; height: 2px; min-width: 6px; max-width: 28px;
  margin-bottom: 16px;
  transition: background .3s;
}
.pip-connector.pending { background: #2d3d50; }
.pip-connector.done    { background: #38a169; }
.pip-connector.active  { background: linear-gradient(90deg, #38a169, #63b3ed); }
.pip-step-num {
  font-size: 9px; color: #4a6077; margin-top: -2px;
}
</style>
"""


def _render_pipeline(completed: int, active: int, error: bool = False) -> str:
    """
    Render the 6-step pipeline as an HTML string.

    completed : number of fully-done steps (0–6)
    active    : index (0–5) of the currently-running step, or -1
    error     : colour the active step red
    """
    html = _PIPELINE_CSS + '<div class="pipeline-wrap">'
    n = len(PIPELINE_STEPS)
    for i, (icon, label) in enumerate(PIPELINE_STEPS):
        if i < completed:
            cls, disp = "done", "✓"
        elif i == active:
            cls = "error" if error else "active"
            disp = "✕" if error else icon
        else:
            cls, disp = "pending", icon

        html += (
            f'<div class="pip-step">'
            f'  <div class="pip-icon {cls}">{disp}</div>'
            f'  <div class="pip-label {cls}">{label}</div>'
            f'  <div class="pip-step-num">{i + 1}/6</div>'
            f'</div>'
        )

        if i < n - 1:
            if i < completed:
                conn = "done"
            elif i == active - 1:
                conn = "active"
            else:
                conn = "pending"
            html += f'<div class="pip-connector {conn}"></div>'

    html += "</div>"
    return html


def show_pipeline(placeholder, completed: int, active: int, error: bool = False):
    placeholder.markdown(
        _render_pipeline(completed, active, error),
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────
# Render helpers
# ─────────────────────────────────────────────────────────

def render_recommendations(
    recommendations: list[str] | None,
    generation_seconds: float | None,
) -> None:
    if not recommendations:
        return

    st.header("Recommendations")
    if generation_seconds is not None:
        st.write(f"Recommendations generated in {generation_seconds:.2f} seconds")

    for recommendation in recommendations:
        st.write(f"• {recommendation}")

def render_report(
    report: str | None,
    report_path: str | None,
    generation_seconds: float | None,
) -> None:
    if report is None:
        return

    st.header("Financial Report")
    if generation_seconds is not None:
        st.write(f"Report generated in {generation_seconds:.2f} seconds")

    if report_path:
        print(f"Report saved to: {report_path}", flush=True)

    st.markdown(report)
    st.download_button(
        "Download Report",
        data=report,
        file_name="financial_report.md",
        mime="text/markdown",
    )

# ─────────────────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────────────────

st.title("AI Financial Planning Assistant")

st.markdown(
    "Upload your transaction history and receive an AI-powered financial analysis."
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        text-align: center;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div {
        justify-content: center;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────

with st.sidebar:

    st.header("Configuration")

    model_options = {
        "☁ ": [
            "gemma4:31b-cloud",
            "gpt-oss:20b-cloud",
            "nemotron-3-nano:30b-cloud",
        ],
        "🔒 Local": [
            "llama3.1:8b",
            "llama3.2:1b",
            "gemma2:2b",
            "qwen3.5:2b",
        ],
    }
    labeled_models = {
        f"{group}: {model_name}": model_name
        for group, model_names in model_options.items()
        for model_name in model_names
    }
    selected_model = st.selectbox(
        "Choose Ollama LLM Model",
        options=list(labeled_models),
    )
    model = labeled_models[selected_model]

    uploaded_file = st.file_uploader(
        "Upload Transaction CSV",
        type=["csv"],
    )

    if uploaded_file is not None:
        uploaded_file_key = (uploaded_file.name, uploaded_file.size)
        if st.session_state.get("uploaded_file_key") != uploaded_file_key:
            st.session_state.uploaded_file_key = uploaded_file_key
            st.session_state.pop("analysis_result", None)

    analyze = st.button(
        "Analyze Finances",
        use_container_width=True,
        disabled=uploaded_file is None,
    )

# ── Main ──────────────────────────────────────────────────

if uploaded_file is None:
    st.info("Please upload a CSV file to begin.")
    st.stop()

upload_message = st.empty()
if "analysis_result" not in st.session_state:
    upload_message.success("CSV uploaded successfully!")
print("CSV uploaded:", uploaded_file.name, flush=True)

# ── Analysis run ──────────────────────────────────────────

if analyze:
    print("Analyze button clicked", flush=True)
    st.session_state.pop("analysis_result", None)

    # Pipeline diagram — shown for the whole duration of analysis
    st.markdown("##### Pipeline")
    pipeline_ph = st.empty()
    show_pipeline(pipeline_ph, completed=0, active=0)   # step 1 active

    with st.spinner("Analyzing finances…"):

        # 1 — Parse CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(uploaded_file.getbuffer())
            temp_file_path = tmp.name

        transactions = csv_parser.parse(temp_file_path)
        print("[1/6] CSV parsing complete", flush=True)

        # 2 — Validate
        show_pipeline(pipeline_ph, completed=1, active=1)
        validation_result = validator.validate_batch(transactions)
        transactions = validation_result.as_batch()
        print("[2/6] Validation complete", flush=True)

        # 3 — Normalize
        show_pipeline(pipeline_ph, completed=2, active=2)
        transactions = normalizer.normalize(validation_result)
        print("[3/6] Normalization complete", flush=True)

        # 4 — Financial analysis (LangGraph)
        show_pipeline(pipeline_ph, completed=3, active=3)

        state = {
            "transactions": transactions,
            "goals": [],
            "debts": [],
            "errors": [],
            "llm_model": model,
        }

        print("[4/6] Starting LangGraph…", flush=True)

        results_header = st.empty()
        recommendations_placeholder = st.empty()
        report_placeholder = st.empty()
        result = {}

        for update in workflow.stream(state, stream_mode="updates"):
            for node_name, node_result in update.items():
                result.update(node_result)

                if node_name == "analyze_finances":
                    # 5 — Recommendations
                    show_pipeline(pipeline_ph, completed=4, active=4)

                if node_name == "generate_recommendations":
                    with results_header.container():
                        st.divider()
                        st.header("Analysis Results")

                    with recommendations_placeholder.container():
                        render_recommendations(
                            node_result.get("recommendations"),
                            node_result.get("recommendation_generation_seconds"),
                        )
                    # 6 — Report
                    show_pipeline(pipeline_ph, completed=5, active=5)

                if node_name == "generate_report":
                    with report_placeholder.container():
                        render_report(
                            node_result.get("report"),
                            node_result.get("report_path"),
                            node_result.get("report_generation_seconds"),
                        )

        print("[DEBUG] Final workflow state keys:", list(result.keys()), flush=True)
        print("[6/6] LangGraph completed", flush=True)

        analysis = result.get("financial_analysis")
        recommendations = result.get("recommendations")
        recommendation_generation_seconds = result.get("recommendation_generation_seconds")
        report = result.get("report")
        report_path = result.get("report_path")
        report_generation_seconds = result.get("report_generation_seconds")

        if analysis is None:
            errors = result.get("errors", [])
            show_pipeline(pipeline_ph, completed=3, active=3, error=True)
            st.error("Analysis failed before recommendations could be generated.")
            if errors:
                st.error("Workflow errors: " + "; ".join(errors))
            print("[analysis failed] Result keys:", list(result.keys()), flush=True)
            st.stop()

        report_missing = report is None

        # All 6 steps complete
        show_pipeline(pipeline_ph, completed=6, active=-1)
        print("[6/6] Complete", flush=True)

    upload_message.empty()

    st.session_state.analysis_result = {
        "recommendations": recommendations,
        "recommendation_generation_seconds": recommendation_generation_seconds,
        "report": report,
        "report_path": report_path,
        "report_generation_seconds": report_generation_seconds,
        "report_missing": report_missing,
    }

# ── Show cached results ───────────────────────────────────

completed_result = st.session_state.get("analysis_result")

if completed_result and not analyze:
    recommendations = completed_result["recommendations"]
    recommendation_generation_seconds = completed_result.get(
        "recommendation_generation_seconds"
    )
    report = completed_result["report"]
    report_path = completed_result["report_path"]
    report_generation_seconds = completed_result["report_generation_seconds"]

    st.divider()
    st.header("Analysis Results")

    if completed_result["report_missing"]:
        st.warning("Analysis finished, but the report was not generated.")

    render_recommendations(recommendations, recommendation_generation_seconds)
    render_report(report, report_path, report_generation_seconds)
