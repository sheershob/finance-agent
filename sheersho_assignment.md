# Agentic AI Project: AI Personal Finance & Budget Planning Assistant

## Project Overview

### Title

**Agentic AI Personal Finance & Budget Planning Assistant**

### Duration

**3 Days**

### Difficulty

**Intermediate**

---

# Problem Statement

People often have difficulty understanding where their money is going, controlling unnecessary expenses, setting financial goals, and deciding how much they should save or invest.

Traditional expense trackers only categorize transactions and display charts. They generally do not understand the user's financial goals or provide a multi-step reasoning process for creating a personalized financial plan.

The objective of this project is to build an **Agentic AI Personal Finance & Budget Planning Assistant** that can analyze income and expenses, identify spending patterns, create budgets, evaluate financial goals, and generate actionable recommendations.

The system should use multiple AI agents to analyze financial information and produce a structured financial plan.

---

# Project Objective

Develop an AI-powered financial assistant capable of:

- Understanding a user's financial goals.
- Analyzing income and expenses.
- Categorizing transactions.
- Detecting unusual spending.
- Creating monthly budgets.
- Identifying areas of overspending.
- Planning savings goals.
- Performing what-if financial calculations.
- Maintaining financial conversation context.
- Generating structured financial reports.

---

# Functional Requirements

## 1. Financial Profile Input

Allow users to provide basic financial information.

Example:

```text
Monthly Income: ₹1,50,000

Monthly Fixed Expenses: ₹45,000

Monthly Variable Expenses: ₹30,000

Existing Savings: ₹8,00,000

Monthly Investment: ₹25,000

Financial Goal:
Buy a ₹1.3 crore house in 5 years.
```

The system should convert the information into a structured financial profile.

---

# 2. Transaction Upload

Allow users to upload transaction data.

Supported formats:

- CSV
- Excel
- PDF bank statements

Example:

```text
transactions.csv
```

Example data:

| Date | Description | Amount | Type |
|---|---|---:|---|
| 01-08-2026 | Salary | ₹1,50,000 | Credit |
| 02-08-2026 | Rent | ₹25,000 | Debit |
| 03-08-2026 | Amazon | ₹4,500 | Debit |
| 04-08-2026 | Restaurant | ₹1,800 | Debit |
| 05-08-2026 | Electricity | ₹3,200 | Debit |

---

# 3. Expense Categorization Agent

The AI should automatically categorize transactions.

Example:

```text
Amazon → Shopping
Swiggy → Food
Uber → Transportation
Electricity → Utilities
Netflix → Entertainment
Rent → Housing
```

Possible categories:

```text
Housing
Food
Transportation
Shopping
Entertainment
Utilities
Healthcare
Education
Travel
Investments
Other
```

---

# 4. Financial Analysis Agent

Analyze the user's financial behavior.

Example:

```text
Monthly Income: ₹1,50,000

Total Expenses: ₹82,000

Savings: ₹68,000

Savings Rate: 45.3%
```

The agent should identify:

```text
Strengths:
- High savings rate
- Controlled housing expenses

Concerns:
- High shopping expenses
- Increasing restaurant spending
- Low emergency fund
```

---

# 5. Budget Planning Agent

The AI should create a personalized monthly budget.

Example:

```text
Recommended Monthly Budget

Housing:        ₹30,000
Food:           ₹12,000
Transportation: ₹8,000
Utilities:      ₹5,000
Entertainment:  ₹5,000
Shopping:       ₹5,000
Investments:    ₹50,000
Emergency Fund: ₹10,000
Other:          ₹5,000
```

The budget should be based on the user's actual spending rather than blindly applying a fixed rule such as 50/30/20.

---

# 6. Financial Goal Agent

Allow users to define financial goals.

Examples:

```text
Goal 1:
Buy a house

Target: ₹1.3 crore
Timeline: 5 years
```

```text
Goal 2:
Build emergency fund

Target: ₹6 lakh
Timeline: 12 months
```

```text
Goal 3:
Retirement

Target corpus: ₹5 crore
Timeline: 20 years
```

The system should calculate the approximate monthly amount required to pursue each goal.

---

# 7. Savings Optimization Agent

The system should identify opportunities to increase savings.

Example:

```text
Current Savings:
₹55,000/month

Potential Savings:

Reduce restaurant spending:
₹4,000

Reduce shopping:
₹5,000

Reduce subscriptions:
₹1,500

Optimize transportation:
₹2,500

Potential additional savings:
₹13,000/month
```

---

# 8. What-If Analysis Agent

The user should be able to ask hypothetical questions.

Example:

> What happens if I increase my investment by ₹10,000 per month?

The system should calculate and explain the potential impact.

Other examples:

```text
What if my salary increases by 10% every year?

What if I save ₹70,000 every month?

What if my expenses increase by 6% annually?

What if I delay buying the house by 2 years?

What if I invest ₹50,000 instead of ₹30,000?
```

---

# 9. Financial Alert Agent

Detect unusual or potentially problematic spending.

Example:

```text
⚠️ Spending Alert

Your restaurant spending this month is:

₹9,800

Average previous spending:

₹5,200

Increase:

88%
```

Other alerts:

```text
Unusually large transaction
Subscription increase
Repeated unnecessary expenses
Low savings rate
Emergency fund below target
High debt payment
```

---

# 10. Debt Analysis Agent

Allow users to enter loans.

Example:

```text
Home Loan

Outstanding Principal: ₹35,00,000

Interest Rate: 8.5%

Remaining Tenure: 12 years

Monthly EMI: ₹37,000
```

The system should provide:

- Outstanding loan estimate.
- Interest burden.
- EMI analysis.
- Prepayment scenarios.
- Comparison between investing and prepaying.

---

# 11. Conversation Memory

The assistant should remember financial goals and previous discussions.

Example:

User:

> I want to buy a house in 5 years.

Later:

> Can I increase my monthly investment by ₹15,000?

The system should understand that the additional investment is related to the previously discussed house goal.

Example memory:

```text
Financial Goal:
House Purchase

Target:
₹1.3 crore

Timeline:
5 years

Current Monthly Investment:
₹40,000
```

---

# 12. Financial Report Generation

Generate a structured monthly report.

Example:

```text
Monthly Financial Report

Income:
₹1,50,000

Expenses:
₹82,000

Savings:
₹68,000

Savings Rate:
45.3%

Top Expense Categories:

1. Housing — ₹25,000
2. Food — ₹14,000
3. Transportation — ₹9,000
4. Shopping — ₹8,000

Financial Health:

Good

Recommended Actions:

1. Reduce shopping expenses.
2. Increase emergency fund.
3. Maintain current savings rate.
4. Increase long-term investments gradually.
```

---

# Agent Workflow

```text
                     User
                      │
                      ▼
                Finance UI
                      │
                      ▼
               Agent Controller
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   Profile Agent   Transaction    Memory
                     Agent
                       │
                       ▼
                Categorization
                     Agent
                       │
                       ▼
                Analysis Agent
                       │
             ┌─────────┼─────────┐
             │         │         │
             ▼         ▼         ▼
          Budget      Goal      Debt
          Agent      Agent     Agent
             │         │         │
             └─────────┼─────────┘
                       ▼
                Reasoning Agent
                       │
                       ▼
                Recommendation
                       │
                       ▼
                 Report Generator
```

---

# Suggested Architecture

```text
                         User
                          │
                          ▼
                    Streamlit UI
                          │
                          ▼
                   Agent Controller
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
   Profile Agent    Transaction Agent    Memory Manager
        │                 │
        │                 ▼
        │          Categorization Agent
        │                 │
        └──────────┬──────┘
                   ▼
             Finance Analyzer
                   │
       ┌───────────┼───────────┐
       │           │           │
       ▼           ▼           ▼
     Budget       Goal        Debt
     Agent       Agent       Agent
       │           │           │
       └───────────┼───────────┘
                   ▼
             What-If Agent
                   │
                   ▼
            Recommendation Agent
                   │
                   ▼
             Report Generator
                   │
                   ▼
              Final Output
```

---

# Suggested Tech Stack

## Frontend

- Streamlit
- React (Optional)

## Backend

- FastAPI

## AI Framework

- LangGraph
- LangChain

## LLM

- OpenAI GPT
- Gemini

## Database

- SQLite

## Data Processing

- Pandas
- NumPy

## Document Processing

- PyMuPDF
- python-docx

## Visualization

- Plotly
- Matplotlib

---

# Sample Folder Structure

```text
finance-agent/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
│
├── backend/
│   ├── profile.py
│   ├── transaction_parser.py
│   ├── categorizer.py
│   ├── analyzer.py
│   ├── budget.py
│   ├── goals.py
│   ├── debt.py
│   ├── what_if.py
│   ├── alerts.py
│   ├── recommendations.py
│   ├── report_generator.py
│   ├── memory.py
│   └── utils.py
│
├── data/
│   ├── transactions.csv
│   └── sample_bank_statement.pdf
│
├── database/
│
├── reports/
│
└── docs/
    └── architecture.png
```

---

# Example End-to-End Interaction

## User

```text
My monthly income is ₹1,50,000.

I spend around ₹80,000 per month.

I want to save ₹30 lakh in the next 4 years.
```

---

## Financial Analysis Agent

```text
Monthly Income:
₹1,50,000

Monthly Expenses:
₹80,000

Current Monthly Surplus:
₹70,000

Current Savings Rate:
46.7%
```

---

## Goal Agent

```text
Financial Goal:

₹30 lakh

Timeline:

4 years
```

The agent calculates the approximate monthly savings/investment requirement based on the assumptions provided.

---

## Budget Agent

```text
Recommended Maximum Expenses:

₹70,000

Potential Monthly Investment:

₹80,000
```

---

## Reasoning Agent

```text
The goal appears achievable if the user maintains
a high savings rate and invests consistently.

The system recommends:

1. Maintain expenses below ₹70,000.
2. Build an emergency fund.
3. Invest the remaining surplus according to
   the user's risk profile.
4. Review the plan every 6 months.
```

---

## Final Response

```text
Financial Goal Status:

ON TRACK

Target:
₹30 lakh

Timeline:
4 years

Recommended Action:

Maintain consistent monthly savings and review
the investment plan periodically.
```

---

# Example Dashboard

The UI should display:

```text
┌─────────────────────────────────────────────┐
│          PERSONAL FINANCE DASHBOARD         │
├─────────────────────────────────────────────┤
│                                             │
│ Monthly Income       ₹1,50,000              │
│ Monthly Expenses     ₹80,000                │
│ Monthly Savings      ₹70,000                │
│ Savings Rate         46.7%                  │
│                                             │
├─────────────────────────────────────────────┤
│ Expense Breakdown                           │
│                                             │
│ Housing       ███████████  ₹25,000          │
│ Food          ██████       ₹14,000          │
│ Shopping      ████         ₹8,000           │
│ Travel        ███          ₹6,000           │
│ Other         █████        ₹12,000          │
│                                             │
├─────────────────────────────────────────────┤
│ Financial Goals                             │
│                                             │
│ Emergency Fund     ███████░░░ 70%           │
│ House Purchase     █████░░░░░ 50%           │
│ Retirement         ███░░░░░░░ 30%           │
│                                             │
└─────────────────────────────────────────────┘
```

---



# Success Criteria

A successful project should:

- Accept financial information from users.
- Accept transaction data.
- Automatically categorize expenses.
- Analyze income and spending.
- Detect unusual spending.
- Generate a personalized budget.
- Accept financial goals.
- Calculate goal requirements.
- Perform what-if analysis.
- Maintain conversation context.
- Generate actionable recommendations.
- Produce a structured financial report.

---


# Final Demo

The employee should demonstrate at least **5 scenarios**:

```text
Scenario 1 → Analyze monthly expenses

Scenario 2 → Create a monthly budget

Scenario 3 → Plan a financial goal

Scenario 4 → Perform what-if analysis

Scenario 5 → Detect unusual spending
```

Example:

```text
User:
"I want to save ₹20 lakh in 3 years.
Can I achieve it?"

       ↓

Profile Agent

       ↓

Expense Analysis

       ↓

Goal Agent

       ↓

What-If Agent

       ↓

Reasoning Agent

       ↓

Financial Recommendation
```

---

# Key Differentiator

The project should **not** be implemented as a simple expense tracker or chatbot.

The employee should demonstrate the following agentic workflow:

```text
UNDERSTAND FINANCIAL PROFILE
          ↓
ANALYZE TRANSACTIONS
          ↓
CATEGORIZE EXPENSES
          ↓
IDENTIFY PATTERNS
          ↓
UNDERSTAND FINANCIAL GOALS
          ↓
PLAN
          ↓
PERFORM CALCULATIONS
          ↓
RUN WHAT-IF SCENARIOS
          ↓
REASON ABOUT OPTIONS
          ↓
GENERATE RECOMMENDATIONS
          ↓
GENERATE FINANCIAL REPORT
```

The final application should demonstrate how **Agentic AI + LLM + structured data analysis + memory + reasoning + interactive dashboards** can be combined to create an intelligent personal finance assistant.

---

# Important Disclaimer
The system should clearly distinguish:

- User-provided financial data.
- Calculated values.
- AI-generated observations.
- Hypothetical projections.
- Actual financial advice from a qualified professional.

Final financial decisions should remain with the user or an appropriate qualified professional.