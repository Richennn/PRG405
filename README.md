# Student Daily Internet Usage Dashboard

Interactive Streamlit dashboard for the PRG405 project *Analysis of Daily Internet Usage Among Students*
(Group 6, Samtse College of Education).

## Quick start

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app uses `data/cleaned_student_internet_data.csv`. You can also put the raw `Student Daily Internet.csv`
next to `app.py` (or in `data/`), or load a file from the sidebar under **Data source**.

## Files

| File | Purpose |
|---|---|
| `app.py` | The dashboard: data cleaning (same steps as the notebook), filters and 5 pages |
| `requirements.txt` | Python packages |
| `.streamlit/config.toml` | Dark navy theme matching the Figma prototype |
| `USER_GUIDE.md` | How to navigate and use the dashboard |
| `data/` | The cleaned survey CSV |

## Pages

| Page | What it shows |
|---|---|
| 01 Overview | Key numbers, box plot of daily hours, devices, purposes and hour bands |
| 02 Usage | Audience cards by gender and age group, statistics table, distributions, box plots (RQ1, RQ4) |
| 03 Devices | Device share, breakdown and hours by device group (RQ3) |
| 04 Purposes | Purpose share, breakdown and hours by purpose (RQ2) |
| 05 Insights | Correlations, hypothesis tests, findings, recommendations and limitations (RQ4, RQ5) |

## Data

The app accepts either:
- the **raw Google Forms export** (`Student Daily Internet.csv`, 30 columns). The app re-runs the notebook's
  cleaning: it drops Score/Timestamp, renames the columns, removes duplicates and missing answers, splits the
  multi-answer columns, converts hour ranges to midpoints and agree/disagree answers to 1–5, and groups rare
  categories; or
- the **cleaned CSV** saved by the notebook (`cleaned_student_internet_data.csv`).

## Analysis inside the app

- Pandas: descriptive statistics, frequencies and percentages, group comparisons, Spearman correlation matrix
- NumPy: percentiles for the 1.5 × IQR outlier rule, `select`/`where` for grouping, `triu` for the correlation matrix
- SciPy: Spearman rank correlation for H1 (gender) and H2 (age group), α = 0.05, with Mann-Whitney U and
  Kruskal-Wallis as supporting checks
