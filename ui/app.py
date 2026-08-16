import streamlit as st

from graph.workflow import build_workflow

from tools.csv_parser import CSVParser
from tools.validators import TransactionValidator
from tools.transaction_normalizer import TransactionNormalizer

csv_parser = CSVParser()
validator = TransactionValidator()
normalizer = TransactionNormalizer()

workflow = build_workflow()

st.set_page_config(
    page_title="AI Financial Planner",
    page_icon="💰",
    layout="wide",
)

st.title("💰 AI Financial Planning Assistant")
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
            "phi3:mini",
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

# Placeholder

if analyze:

    with st.spinner("Analyzing finances..."):

        # Parse CSV
        transactions = csv_parser.parse(uploaded_file)

        # Validate
        transactions = validator.validate(transactions)

        # Normalize
        transactions = normalizer.normalize(transactions)

        state = {
            "transactions": transactions,
            "goals": [],
            "debts": [],
            "errors": [],
        }

        result = workflow.invoke(state)

        analysis = result["financial_analysis"]
        recommendations = result["recommendations"]
        report = result["report"]

        st.subheader("Financial Summary")

        # st.metric("Income", "₹0")
        # st.metric("Expenses", "₹0")
        # st.metric("Savings", "₹0")
        # st.metric("Health Score", "0/100")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Monthly Income",
                f"₹{analysis.monthly_income}"
            )

            st.metric(
                "Monthly Expenses",
                f"₹{analysis.monthly_expenses}"
            )

        with col2:
            st.metric(
                "Monthly Savings",
                f"₹{analysis.monthly_surplus}"
            )

            st.metric(
                "Health Score",
                f"{analysis.financial_health_score}/100"
            )

        st.divider()

        st.subheader("Recommendations")

        for recommendation in recommendations:
            st.success(recommendation)

        st.divider()

        st.subheader("Charts")

        st.markdown(report)

        st.download_button(
            "Download Report",
            report,
            file_name="financial_report.md",
        )

        st.divider()

        st.subheader("Financial Report")

        st.info(
            "Generated report will appear here."
        )

        st.subheader("Debt Analysis")

        for debt in analysis.debt_analysis:
            st.write(debt)

        st.subheader("Goal Analysis")

        for goal in analysis.goal_analysis:
            st.write(goal)