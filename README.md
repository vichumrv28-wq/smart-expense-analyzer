# Smart Expense Analyzer

A beginner-friendly Python data analytics app that explores transaction spending, displays interactive charts, filters expenses, and flags potentially unusual transaction amounts using Isolation Forest.

## Features

- Load the included sample CSV or upload your own CSV
- Total spending, average transaction, transaction count, and unusual-transaction count
- Interactive category pie chart and daily spending line chart
- Filter transactions by category and date range
- Review transactions flagged as unusual
- Download filtered data as a CSV

## Tech stack

- Python
- Pandas
- Streamlit
- Plotly
- scikit-learn (Isolation Forest)

## Requirements

Python 3.10 or newer is recommended. Install Python from [python.org](https://www.python.org/downloads/macos/) if it is not already installed.

## Run locally on macOS

1. Download or clone this repository.
2. Open Terminal and move into the project folder:

   ```bash
   cd smart-expense-analyzer
   ```

3. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

4. Activate it:

   ```bash
   source .venv/bin/activate
   ```

5. Install the packages:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   streamlit run app.py
   ```

The app should open in your browser. If it does not, use the local URL printed in Terminal (usually `http://localhost:8501`).

## CSV format

Your CSV must contain these columns:

| Column | Meaning | Example |
|---|---|---|
| `Date` | Transaction date | `2026-01-05` |
| `Description` | What the transaction was for | `Groceries` |
| `Category` | Spending category | `Food` |
| `Amount` | Numeric amount in rupees | `850` |
| `Payment_Method` | Payment type | `UPI` |

Use `sample_expenses.csv` as a template. Invalid dates and non-numeric amounts are discarded. Negative amounts are excluded in this simple version.

## How the anomaly detection works

The app uses scikit-learn's Isolation Forest on transaction amounts. It flags values that differ from the other amounts in the loaded dataset. A flag is only a prompt for manual review: a large transaction may be completely legitimate. The model does not detect fraud reliably and does not use labeled fraud data.

## Test checklist

- [ ] App opens using `streamlit run app.py`
- [ ] Sample data displays four summary metrics
- [ ] Category filter changes the displayed totals and charts
- [ ] Date filter changes the displayed transactions
- [ ] Uploading a correctly formatted CSV works
- [ ] Uploading a CSV without a required column shows an error
- [ ] CSV download creates `filtered_expenses.csv`
- [ ] Unusual transaction flags appear when enough rows are loaded

## Project structure

```text
smart-expense-analyzer/
├── app.py
├── sample_expenses.csv
├── requirements.txt
├── .gitignore
└── README.md
```

## Limitations and future improvements

- Current anomaly detection uses only transaction amount.
- Sample data is fictional and for demonstration only.
- Currency formatting is set to Indian rupees (₹).
- Future work: monthly budget alerts, recurring expense detection, category prediction, and evaluation against a labeled dataset.

## Resume bullet (use only after running and verifying)

Built a Python-based expense analytics dashboard using Pandas, Streamlit, and Plotly to summarize transactions, visualize category and daily spending, filter CSV data, and export results. Implemented an Isolation Forest baseline to flag potentially unusual transaction amounts for manual review.
