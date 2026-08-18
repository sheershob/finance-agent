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

# ---------------- Sidebar ----------------

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

# ---------------- Main ----------------

if uploaded_file is None:

    st.info(
        "Please upload a CSV file to begin."
    )

    st.stop()

upload_message = st.empty()
if "analysis_result" not in st.session_state:
    upload_message.success("CSV uploaded successfully!")
print("CSV uploaded:", uploaded_file.name, flush=True)
# st.write("DEBUG: app reached button")

# Placeholder

if analyze:
    # st.write("DEBUG: Analyze button clicked")
    print("Analyze button clicked", flush=True)
    st.session_state.pop("analysis_result", None)
    progress_header = st.empty()
    progress_header.subheader("Analysis Progress")
    progress_box = st.empty()

    with st.spinner("Analyzing finances..."):

        progress_box.info("1/6 — Parsing CSV...")
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv",
        ) as temp_file:

            temp_file.write(uploaded_file.getbuffer())

            temp_file_path = temp_file.name

        transactions = csv_parser.parse(temp_file_path)
        print("[1/6] CSV parsing complete", flush=True)

        progress_box.info("2/6 — Validating transactions...")
        validation_result = validator.validate_batch(transactions)
        transactions = validation_result.as_batch()
        print("[2/6] Validation complete", flush=True)

        progress_box.info("3/6 — Normalizing transactions...")
        # transactions = normalizer.normalize(transactions)
        transactions = normalizer.normalize(validation_result)
        print("[3/6] Normalization complete", flush=True)

        progress_box.info("4/6 — Running financial analysis...")

        state = {
            "transactions": transactions,
            "goals": [],
            "debts": [],
            "errors": [],
            "llm_model": model,
        }

        print("[4/6] Starting LangGraph...", flush=True)

        result = workflow.invoke(state)
        print("[DEBUG] Final workflow state keys:", list(result.keys()), flush=True)

        print("[4/6] LangGraph completed", flush=True)

        progress_box.info("5/6 — Preparing recommendations...")

        analysis = result.get("financial_analysis")
        recommendations = result.get("recommendations")
        report = result.get("report")
        report_path = result.get("report_path")
        report_generation_seconds = result.get("report_generation_seconds")

        if analysis is None:
            errors = result.get("errors", [])
            progress_box.error("Analysis failed before recommendations could be generated.")
            if errors:
                st.error("Workflow errors: " + "; ".join(errors))
            print("[analysis failed] Result keys:", list(result.keys()), flush=True)
            st.stop()

        progress_box.info("6/6 — Preparing report...")

        report_missing = report is None

        print("[6/6] Complete", flush=True)

    upload_message.empty()
    progress_header.empty()
    progress_box.empty()

    st.session_state.analysis_result = {
        "recommendations": recommendations,
        "report": report,
        "report_path": report_path,
        "report_generation_seconds": report_generation_seconds,
        "report_missing": report_missing,
    }

completed_result = st.session_state.get("analysis_result")

if completed_result:
    recommendations = completed_result["recommendations"]
    report = completed_result["report"]
    report_path = completed_result["report_path"]
    report_generation_seconds = completed_result["report_generation_seconds"]

    st.divider()
    st.header("Analysis Results")

    if completed_result["report_missing"]:
        st.warning("Analysis finished, but the report was not generated.")

    if report_generation_seconds is not None:
        st.write(f"LLM report generated in {report_generation_seconds:.2f} seconds")

    if recommendations:
        st.header("Recommendations")
        for recommendation in recommendations:
            st.write(f"• {recommendation}")

    if report is not None:
        # st.subheader("Financial Report")

        if report_path:
            # st.caption(f"Saved to: {report_path}")
            print(f"Report saved to: {report_path}", flush=True)

        st.markdown(report)
        st.download_button(
            "Download Report",
            data=report,
            file_name="financial_report.md",
            mime="text/markdown",
        )
