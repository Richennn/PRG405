# User Guide: Student Daily Internet Usage Dashboard

## 1. Open the dashboard

1. Install the packages once: `pip install -r requirements.txt`
2. Start the app: `streamlit run app.py`
3. The dashboard opens in your browser on the **Overview** page.

## 2. Choose a page

Use the numbered menu on the left:

| Page | What it shows |
|---|---|
| 01 Overview | Total students, average daily hours, most-used device, and summary charts |
| 02 Usage | Group cards by gender and age, statistics table, hour distributions and box plots |
| 03 Devices | Which devices students use and daily hours by device group |
| 04 Purposes | Why students go online and hours by purpose |
| 05 Insights | Correlations, hypothesis test results, findings, recommendations and limitations |

## 3. Filter the students

In the **Explore the data** box at the top, click a **Gender** or **Age group** button.
The blue "Viewing …" line shows your selection, and every number and chart on every page updates.
Click **All** or **Clear filters** to include everyone again.

## 4. Use the audience cards (02 Usage)

Each card shows how many students are in a group and their average daily hours.
Click the **↗** on a card to filter the whole dashboard to that group. Click it again to remove the filter.

## 5. Change the charts

- On **02 Usage**, use the drop-down menus to choose the activity (total, academic, social, entertainment)
  and the group to compare (gender, age group, device group).
- Turn on **Remove IQR outliers** to hide outliers in the box plot. The caption shows how many were removed.
- On **05 Insights**, switch the breakdown between **Purposes** and **Devices**.
- The blue **EXPLORE … ↗** links on the Overview cards open the matching page.

## 6. Read the charts

Hover over bars, boxes and donut slices to see exact values. Use the chart toolbar (top right of a chart)
to zoom or save the chart as a PNG.

If a filter combination has no students, the dashboard shows **No matching responses**. Choose a different filter.

## 7. Load a different data file (optional)

Open **Data source** in the sidebar and upload the raw Google Forms CSV or the cleaned CSV.
