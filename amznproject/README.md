# Amazon-Transaction-Analysis

This repository contains a Streamlit application designed to analyze Amazon transaction data for the year 2024. It provides:

Totals by Type: Summaries of transactions grouped by their type.
Monthly Summaries: Aggregated breakdown of product sales, fees, shipping, refunds, and more across each month of 2024.
Cumulative Sales: A view of cumulative units sold and sales value per SKU, for the entire year, in descending order by units sold (or whichever column you choose).
Features
Load CSV

Skip specified rows and parse the data from Amazon transaction export files.
Automatically convert certain columns (e.g., total, product sales) to numeric for analysis.
Monthly Units & Summaries

Summarize by month to see how many units were sold and how product sales, shipping, refunds, and fees vary over time.
SKU Tracking

View a cumulative total of units sold and product sales by SKU, ensuring no double-counting of partial line items in the same order.
Streamlit UI

Simple button to Load CSV (either via file uploader or file path).
Interactive tables displayed within the Streamlit app.
Installation
Clone or Download this repository:

bash
Copy code
git clone https://github.com/<username>/amazon-transaction-analysis.git
or download it as a ZIP file and unzip it locally.

Navigate to the project directory:

bash
Copy code
cd amazon-transaction-analysis
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Make sure requirements.txt includes at least:

Copy code
streamlit
pandas
(And any other packages you rely on.)

Usage
Run the Streamlit App:

bash
Copy code
streamlit run main.py
By default, Streamlit will start a local server (usually at http://localhost:8501).

Load Your CSV:

Upload a CSV file directly from your computer, or
Provide the full path to the CSV (e.g. /Users/foo/data.csv)
Then click Load CSV.
Explore:

Totals by Type: Summaries of total column grouped by type.
Monthly Summaries (2024): Product sales, refunds, fees, etc., aggregated by month.
Cumulative Sales in 2024: See how many units and how much product revenue each SKU has accumulated throughout the year.
Project Structure
bash
Copy code
.
├── main.py               # Main Streamlit app file
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── ...                   # Additional scripts, data, etc.
Contributing
Pull Requests are welcome. For major changes, please open an issue first to discuss your proposed modification.
Ensure that any code style changes are consistent with the rest of the project.
License
You may include a license of your choosing here (e.g., MIT, Apache, etc.). If you’re not sure, choosealicense.com can help.
