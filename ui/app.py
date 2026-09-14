import streamlit as st
import tempfile
from decimal import Decimal

from agents.llm import OllamaConnectionError
from graph.workflow import build_workflow

from tools.csv_parser import CSVParser
from tools.validators import TransactionValidator
from tools.transaction_normalizer import TransactionNormalizer
from schemas.debt import Debt
from schemas.goal import FinancialGoal


st.set_page_config(
    page_title="AI Financial Planner",
    page_icon="💰",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Single-file uploader: hide the trailing "+" (it replaces the file, it does not add another). */
    [data-testid="stFileUploader"] button[aria-label="Add files"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
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
    ("📂", "Parse File"),
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
# st.markdown("Add optional debts and goals, then upload your transaction history to receive an AI-powered financial analysis.")

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

# ── Upload transactions (Main Page) ───────────────────────

st.divider()
st.subheader("Upload Transactions")

uploaded_file = st.file_uploader(
    "Required: date, description, amount, type.  Optional: category",
    type=["csv"],
    help="Required: date, description, amount, type. Optional: category.",
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

upload_message = st.empty()
if uploaded_file is None:
    # st.info("Add any optional debts or goals above, then upload a CSV to begin analysis.")
    print("No CSV uploaded yet", flush=True)
else:
    if "analysis_result" not in st.session_state:
        upload_message.success("CSV uploaded successfully!")
    print("CSV uploaded:", uploaded_file.name, flush=True)

# ── Optional Debt Information (Main Page) ─────────────────
if "debts" not in st.session_state:
    st.session_state.debts = []

debts_count = len(st.session_state.debts)
expander_title = (
    f"Optional: Add Debt / Loan Information ({debts_count} Added)"
    if debts_count > 0
    else "Optional: Add Debt / Loan Information"
)

with st.expander(expander_title, expanded=False):
    st.markdown(
        "If you have any active loans or debts (e.g., Home Loan, Car Loan, Personal Loan), "
        "add them below."
    )
    st.subheader("Add a New Debt")
    loan_name_input = st.text_input(
        "Loan / Debt Name *",
        placeholder="e.g. Home Loan, Car Loan, Credit Card",
        key="new_debt_loan_name",
    )
    col1, col2 = st.columns(2)
    outstanding_principal_input = col1.number_input(
        "Outstanding Principal (₹) *",
        min_value=0.0,
        step=5000.0,
        format="%.2f",
        help="Total remaining principal balance left to pay.",
        key="new_debt_outstanding_principal",
    )
    interest_rate_input = col2.number_input(
        "Annual Interest Rate (%) *",
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.2f",
        help="Annual interest rate percentage.",
        key="new_debt_interest_rate",
    )
    col3, col4 = st.columns(2)
    remaining_tenure_input = col3.number_input(
        "Remaining Tenure (months) *",
        min_value=0,
        step=1,
        help="Remaining tenure in months.",
        key="new_debt_remaining_tenure",
    )
    monthly_emi_input = col4.number_input(
        "Monthly EMI (₹) *",
        min_value=0.0,
        step=500.0,
        format="%.2f",
        help="Fixed monthly installment amount.",
        key="new_debt_monthly_emi",
    )

    form_valid = (
        loan_name_input.strip() != ""
        and outstanding_principal_input > 0
        and remaining_tenure_input > 0
        and monthly_emi_input > 0
    )

    submit_debt = st.button(
        "➕ Add Debt Entry",
        use_container_width=True,
        disabled=not form_valid,
    )

    if submit_debt:
        new_debt = Debt(
            loan_name=loan_name_input.strip(),
            outstanding_principal=Decimal(str(outstanding_principal_input)),
            interest_rate=Decimal(str(interest_rate_input)),
            remaining_tenure_months=int(remaining_tenure_input),
            monthly_emi=Decimal(str(monthly_emi_input)),
        )

        st.session_state.debts.append(new_debt)
        st.session_state.pop("analysis_result", None)
        for field_key in (
            "new_debt_loan_name",
            "new_debt_outstanding_principal",
            "new_debt_interest_rate",
            "new_debt_remaining_tenure",
            "new_debt_monthly_emi",
        ):
            st.session_state.pop(field_key, None)
        st.success(f"Added '{loan_name_input.strip()}' successfully!")
        st.rerun()

    if st.session_state.debts:
        st.divider()
        st.subheader(f"Active Debts ({len(st.session_state.debts)})")
        for idx, d in enumerate(st.session_state.debts):
            col_info, col_btn = st.columns([5, 1])
            is_insuff = (d.monthly_emi * Decimal(d.remaining_tenure_months)) < d.outstanding_principal
            with col_info:
                warning_badge = " ⚠️ *(EMI/tenure insufficient to repay principal)*" if is_insuff else ""
                st.markdown(
                    f"**{idx + 1}. {d.loan_name}**{warning_badge} — "
                    f"Principal: **₹{d.outstanding_principal:,.2f}** @ **{d.interest_rate}%** p.a. | "
                    f"EMI: **₹{d.monthly_emi:,.2f}/mo** | "
                    f"Tenure: **{d.remaining_tenure_months} months**"
                )
                if is_insuff:
                    st.caption("⚠️ Total EMI payments over remaining tenure (₹{:,.2f}) cannot fully cover the principal (₹{:,.2f}).".format(
                        d.monthly_emi * Decimal(d.remaining_tenure_months), d.outstanding_principal
                    ))
            with col_btn:
                if st.button("Delete", key=f"del_debt_{idx}"):
                    st.session_state.debts.pop(idx)
                    st.session_state.pop("analysis_result", None)
                    st.rerun()

        if st.button("Clear All Debts"):
            st.session_state.debts = []
            st.session_state.pop("analysis_result", None)
            st.rerun()

# ── Optional Goal Information (Main Page) ─────────────────
if "goals" not in st.session_state:
    st.session_state.goals = []

goals_count = len(st.session_state.goals)
goal_expander_title = (
    f"Optional: Add Financial Goals ({goals_count} Added)"
    if goals_count > 0
    else "Optional: Add Financial Goals"
)

with st.expander(goal_expander_title, expanded=False):
    st.markdown(
        "If you have target financial goals (e.g., Buying a Car, House Down Payment), "
        "add them below."
    )
    goal_name_input = st.text_input(
        "Goal Name *",
        placeholder="e.g. Emergency Fund, Buy a Car, House Down Payment",
        key="new_goal_name",
    )
    g_col1, g_col2 = st.columns(2)
    target_amount_input = g_col1.number_input(
        "Target Amount (₹) *",
        min_value=0.0,
        step=10000.0,
        format="%.2f",
        help="Target cost to achieve this goal.",
        key="new_goal_target_amount",
    )
    current_amount_input = g_col2.number_input(
        "Current Savings Accumulated (₹) *",
        min_value=0.0,
        step=5000.0,
        format="%.2f",
        help="Savings already accumulated toward this goal.",
        key="new_goal_current_amount",
    )
    g_col3, g_col4 = st.columns(2)
    time_horizon_input = g_col3.number_input(
        "Time Horizon (months) *",
        min_value=0,
        step=1,
        help="Target timeframe to achieve the goal in months.",
        key="new_goal_time_horizon",
    )
    priority_input = g_col4.slider(
        "Priority (1 = Highest, 5 = Lowest)",
        min_value=1,
        max_value=5,
        value=3,
        help="Priority ranking for surplus allocation.",
        key="new_goal_priority",
    )
    category_input = st.selectbox(
        "Goal Category",
        options=["Emergency Fund", "Savings", "House / Property", "Vehicle", "Retirement", "Travel", "Other"],
        key="new_goal_category",
    )

    goal_form_valid = (
        goal_name_input.strip() != ""
        and target_amount_input > 0
        and time_horizon_input > 0
    )

    submit_goal = st.button(
        "➕ Add Goal Entry",
        use_container_width=True,
        disabled=not goal_form_valid,
        key="submit_goal_btn",
    )

    if submit_goal:
        new_goal = FinancialGoal(
            name=goal_name_input.strip(),
            target_amount=Decimal(str(target_amount_input)),
            current_amount=Decimal(str(current_amount_input)),
            time_horizon_months=int(time_horizon_input),
            priority=int(priority_input),
            category=category_input,
        )

        st.session_state.goals.append(new_goal)
        st.session_state.pop("analysis_result", None)
        for field_key in (
            "new_goal_name",
            "new_goal_target_amount",
            "new_goal_current_amount",
            "new_goal_time_horizon",
            "new_goal_priority",
            "new_goal_category",
        ):
            st.session_state.pop(field_key, None)
        st.success(f"Added goal '{goal_name_input.strip()}' successfully!")
        st.rerun()

    if st.session_state.goals:
        st.divider()
        st.subheader(f"Active Financial Goals ({len(st.session_state.goals)})")
        for idx, g in enumerate(st.session_state.goals):
            g_info, g_btn = st.columns([5, 1])
            progress_pct = min((float(g.current_amount) / float(g.target_amount)) * 100, 100) if g.target_amount > 0 else 0
            with g_info:
                st.markdown(
                    f"**{idx + 1}. {g.name}** ({g.category or 'General'} | Priority {g.priority}) — "
                    f"Target: **₹{g.target_amount:,.2f}** | Saved: **₹{g.current_amount:,.2f}** ({progress_pct:.1f}%) | "
                    f"Horizon: **{g.time_horizon_months} months**"
                )
            with g_btn:
                if st.button("Delete", key=f"del_goal_{idx}"):
                    st.session_state.goals.pop(idx)
                    st.session_state.pop("analysis_result", None)
                    st.rerun()

        if st.button("Clear All Goals"):
            st.session_state.goals = []
            st.session_state.pop("analysis_result", None)
            st.rerun()

# ── Analysis run ──────────────────────────────────────────

if analyze and uploaded_file is not None:
    print("Analyze button clicked", flush=True)
    st.session_state.pop("analysis_result", None)

    # Pipeline diagram — shown for the whole duration of analysis
    st.markdown("##### Pipeline")
    pipeline_ph = st.empty()
    show_pipeline(pipeline_ph, completed=0, active=0)   # step 1 active

    try:
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
                "goals": st.session_state.get("goals", []),
                "debts": st.session_state.get("debts", []),
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

    except OllamaConnectionError as exc:
        show_pipeline(pipeline_ph, completed=4, active=4, error=True)
        st.error(str(exc))
        # st.info("Please verify Ollama is running and try again.")
        print(f"[LLM] Ollama connection error handled in UI: {exc}", flush=True)
        st.stop()

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
