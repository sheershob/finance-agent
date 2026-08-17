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

# ---------------- Sidebar ----------------

with st.sidebar:

    st.header("Configuration")

    model = st.selectbox(
        "Choose Ollama LLM Model",
        [
            "llama3.1:8b",
            "qwen3:8b",
            "gemma4:31b-cloud",
            "qwen3.5:cloud",
        ],
    )

    uploaded_file = st.file_uploader(
        "Upload Transaction CSV",
        type=["csv"],
    )

    analyze = st.button(
        "Analyze Finances",
        use_container_width=True,
    )

# ---------------- Main ----------------

if uploaded_file is None:

    st.info(
        "Please upload a CSV file to begin."
    )

    st.stop()

st.success("CSV uploaded successfully!")
print("CSV uploaded:", uploaded_file.name, flush=True)
# st.write("DEBUG: app reached button")

# Placeholder

if analyze:
    # st.write("DEBUG: Analyze button clicked")
    print("Analyze button clicked", flush=True)
    st.subheader("Analysis Progress")

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
        }

        print("[4/6] Starting LangGraph...", flush=True)

        result = workflow.invoke(state)
        print("[DEBUG] Final workflow state keys:", list(result.keys()), flush=True)

        print("[4/6] LangGraph completed", flush=True)

        progress_box.info("5/6 — Preparing recommendations...")

        analysis = result.get("financial_analysis")
        recommendations = result.get("recommendations")
        report = result.get("report")

        if analysis is None:
            errors = result.get("errors", [])
            progress_box.error("Analysis failed before recommendations could be generated.")
            if errors:
                st.error("Workflow errors: " + "; ".join(errors))
            print("[analysis failed] Result keys:", list(result.keys()), flush=True)
            st.stop()

        progress_box.info("6/6 — Preparing report...")

        if report is None:
            progress_box.warning("Analysis finished, but the report was not generated.")

        print("[6/6] Complete", flush=True)

    progress_box.success("Analysis complete!")