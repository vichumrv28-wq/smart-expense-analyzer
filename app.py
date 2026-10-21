
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import IsolationForest

st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💸",
    layout="wide",
)

REQUIRED_COLUMNS = [
    "Date",
    "Description",
    "Category",
    "Amount",
    "Payment_Method",
]

st.title("💸 Smart Expense Analyzer")
st.caption("Explore spending patterns and flag unusual transactions.")


@st.cache_data
def load_sample_data():
    return pd.read_csv("sample_expenses.csv")


def prepare_data(data):
    data = data.copy()

    missing = [
        col for col in REQUIRED_COLUMNS
        if col not in data.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    data["Date"] = pd.to_datetime(
        data["Date"], errors="coerce"
    )
    data["Amount"] = pd.to_numeric(
        data["Amount"], errors="coerce"
    )
    data["Description"] = (
        data["Description"].fillna("Unknown").astype(str)
    )
    data["Category"] = (
        data["Category"].fillna("Uncategorized").astype(str)
    )
    data["Payment_Method"] = (
        data["Payment_Method"].fillna("Unknown").astype(str)
    )

    data = data.dropna(subset=["Date", "Amount"])
    data = data[data["Amount"] >= 0]

    if data.empty:
        raise ValueError(
            "No valid rows found. Check the Date and Amount columns."
        )

    return data.sort_values("Date")


def flag_anomalies(data):
    result = data.copy()
    result["Unusual"] = False

    if len(result) >= 5:
        model = IsolationForest(
            contamination="auto",
            random_state=42,
        )

        features = result[["Amount"]].values
        result["Unusual"] = model.fit_predict(features) == -1

    return result


# Sidebar: upload data
with st.sidebar:
    st.header("Data source")

    uploaded_file = st.file_uploader(
        "Upload expenses (CSV)",
        type=["csv"],
    )

    st.caption(
        "Required columns: Date, Description, Category, "
        "Amount, Payment_Method"
    )

    st.divider()

    st.markdown(
        "**Example:** `2026-01-05,Groceries,Food,850,UPI`"
    )


# Load and validate data
try:
    if uploaded_file is not None:
        raw_data = pd.read_csv(uploaded_file)
        source_label = uploaded_file.name
    else:
        raw_data = load_sample_data()
        source_label = "sample_expenses.csv"

    expenses = prepare_data(raw_data)

except Exception as exc:
    st.error(f"Could not load data: {exc}")
    st.stop()


# Detect unusual transactions
expenses = flag_anomalies(expenses)


# Sidebar: filters
with st.sidebar:
    st.success(
        f"Loaded {len(expenses)} valid transactions"
    )

    categories = sorted(
        expenses["Category"].unique().tolist()
    )

    selected_categories = st.multiselect(
        "Filter categories",
        categories,
        default=categories,
    )

    min_date = expenses["Date"].min().date()
    max_date = expenses["Date"].max().date()

    date_range = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )


# Apply filters
filtered = expenses[
    expenses["Category"].isin(selected_categories)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = filtered[
        (filtered["Date"].dt.date >= start_date)
        & (filtered["Date"].dt.date <= end_date)
    ]

if filtered.empty:
    st.warning(
        "No transactions match your filters. "
        "Change the category or date range."
    )
    st.stop()


# Summary metrics
total_spend = filtered["Amount"].sum()
average_spend = filtered["Amount"].mean()
transaction_count = len(filtered)
unusual_count = int(filtered["Unusual"].sum())

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Total spending",
    f"₹{total_spend:,.2f}",
)
m2.metric(
    "Average transaction",
    f"₹{average_spend:,.2f}",
)
m3.metric(
    "Transactions",
    f"{transaction_count:,}",
)
m4.metric(
    "Unusual flagged",
    f"{unusual_count:,}",
)

st.divider()


# Charts
left, right = st.columns(2)

with left:
    st.subheader("Spending by category")

    category_totals = (
        filtered.groupby("Category", as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
    )

    fig = px.pie(
        category_totals,
        names="Category",
        values="Amount",
        hole=0.45,
        title="Share of spending",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


with right:
    st.subheader("Spending over time")

    daily = (
        filtered.assign(
            DateOnly=filtered["Date"].dt.date
        )
        .groupby("DateOnly", as_index=False)["Amount"]
        .sum()
        .rename(columns={"DateOnly": "Date"})
    )

    fig = px.line(
        daily,
        x="Date",
        y="Amount",
        markers=True,
        title="Daily Spending Trend",
        labels={
            "Amount": "Amount (₹)",
            "Date": "Date",
        },
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# Transaction details
st.subheader("Transaction details")

show_unusual_only = st.checkbox(
    "Show only transactions flagged as unusual"
)

if show_unusual_only:
    table_data = filtered[filtered["Unusual"]].copy()
else:
    table_data = filtered.copy()

display_data = table_data.copy()

display_data["Date"] = (
    display_data["Date"].dt.strftime("%Y-%m-%d")
)

display_data["Status"] = display_data["Unusual"].map(
    {
        True: "Review",
        False: "Normal",
    }
)

st.dataframe(
    display_data[
        [
            "Date",
            "Description",
            "Category",
            "Amount",
            "Payment_Method",
            "Status",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)


# Anomaly detection explanation
if len(filtered) < 5:
    st.info(
        "Add at least 5 valid transactions for the "
        "anomaly detection demo."
    )
else:
    st.caption(
        "Anomaly flags are statistical suggestions based on "
        "transaction amounts, not proof of fraud or an incorrect "
        "transaction. Review them manually."
    )


# Download filtered transactions
csv_bytes = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download filtered transactions as CSV",
    data=csv_bytes,
    file_name="filtered_expenses.csv",
    mime="text/csv",
)


# How it works
with st.expander("How anomaly detection works"):
    st.write(
        "Isolation Forest is an unsupervised machine-learning "
        "algorithm. It attempts to isolate observations that differ "
        "from the rest. This demo uses transaction amount only, so "
        "a high amount may be flagged even when it is legitimate. "
        "The result is a prompt to review, not a financial or fraud "
        "determination."
    )


# Footer
st.caption(
    f"Data source: {source_label} · Built with Python, Pandas, "
    "Streamlit, Plotly and scikit-learn."
)
