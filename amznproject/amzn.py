import streamlit as st
import pandas as pd

def load_csv(file_buffer=None, file_path=None):
    if file_buffer is not None:
        df = pd.read_csv(
            file_buffer,
            sep=",",
            on_bad_lines='skip',
            skiprows=7,
            header=0
        )
    elif file_path is not None and file_path.strip() != "":
        df = pd.read_csv(
            file_path.strip(),
            sep=",",
            on_bad_lines='skip',
            skiprows=7,
            header=0
        )
    else:
        st.warning("No valid CSV source specified.")
        return pd.DataFrame()

    # Convert 'total' column to numeric if present
    if 'total' in df.columns:
        df['total'] = pd.to_numeric(df['total'], errors='coerce')
    else:
        st.warning("Column 'total' not found in CSV. Some functions will fail.")

    return df


def get_type_sum(df):
    """
    Returns a DataFrame with the sum of 'total' grouped by 'type'.
    """
    df_type_sums = df.groupby('type', as_index=False)['total'].sum()
    return df_type_sums


def monthly_summary(df):
    """
    Creates a monthly summary of certain transaction 'type' values
    (Shipping Services, Refund, etc.), plus selling fees and product sales.
    """
    df['date/time'] = (
        df['date/time']
        .astype(str)
        .str.replace('PST', '', regex=False)
        .str.replace('PDT', '', regex=False)
        .str.strip()
    )
    df['date/time'] = pd.to_datetime(df['date/time'], infer_datetime_format=True, errors='coerce')
    
    start_2024 = '2024-01-01'
    end_2024 = '2024-12-31'
    df_filtered = df.loc[
        (df['date/time'] >= start_2024) & 
        (df['date/time'] <= end_2024)
    ].copy()

    # Create a 'month' column (2024 only)
    df_filtered['month'] = df_filtered['date/time'].dt.to_period('M')
    
    # Pivot by 'type'
    df_pivot = pd.pivot_table(
        df_filtered,
        index='month',
        columns='type',
        values='total',
        aggfunc='sum',
        fill_value=0
    )

    # Desired columns in the pivot
    desired_types = [
        "Shipping Services",
        "Refund",
        "FBA Inventory Fee",
        "FBA Customer Return Fee",
        "SAFE-T reimbursement"
    ]
    df_pivot = df_pivot.reindex(columns=desired_types, fill_value=0)

    # Handle selling fees
    if "selling fees" in df_filtered.columns:
        monthly_selling_fees = df_filtered.groupby('month')['selling fees'].sum()
        df_pivot = df_pivot.join(monthly_selling_fees, on='month', how='left')
        df_pivot['selling fees'] = df_pivot['selling fees'].fillna(0)
    else:
        df_pivot['selling fees'] = 0

    # Handle product sales
    if "product sales" in df_filtered.columns:
        df_filtered['product sales'] = pd.to_numeric(df_filtered['product sales'], errors='coerce')
        monthly_product_sales = df_filtered.groupby('month')['product sales'].sum()
        df_pivot = df_pivot.join(monthly_product_sales, on='month', how='left')
        df_pivot['product sales'] = df_pivot['product sales'].fillna(0)
    else:
        df_pivot['product sales'] = 0

    # Ensure we have rows for all 12 months of 2024
    all_months_2024 = pd.period_range("2024-01", "2024-12", freq="M")
    df_pivot = df_pivot.reindex(all_months_2024, fill_value=0)
    df_pivot = df_pivot.reset_index().rename(columns={"index": "month"})

    # Create 'product_minus_expenses'
    df_pivot['product_minus_expenses'] = (
        df_pivot['product sales']
        + df_pivot['SAFE-T reimbursement']
        + df_pivot['Shipping Services']
        + df_pivot['Refund']
        + df_pivot['selling fees']
        + df_pivot['FBA Inventory Fee']
        + df_pivot['FBA Customer Return Fee']
    )

    return df_pivot


def monthly_units_sold(df):
    """
    Returns a DataFrame with columns:
      - 'month'
      - 'units_sold'
    Summing the 'quantity' of items sold each month in 2024.
    """
    df['date/time'] = (
        df['date/time']
        .astype(str)
        .str.replace('PST', '', regex=False)
        .str.replace('PDT', '', regex=False)
        .str.strip()
    )
    df['date/time'] = pd.to_datetime(df['date/time'], infer_datetime_format=True, errors='coerce')
    
    start_2024 = '2024-01-01'
    end_2024 = '2024-12-31'
    df_filtered = df.loc[
        (df['date/time'] >= start_2024) & (df['date/time'] <= end_2024)
    ].copy()
    
    df_filtered['month'] = df_filtered['date/time'].dt.to_period('M')
    df_filtered['quantity'] = pd.to_numeric(df_filtered['quantity'], errors='coerce')
    
    df_units = (
        df_filtered
        .groupby('month', as_index=False)['quantity']
        .sum()
        .rename(columns={'quantity': 'units_sold'})
    )
    
    all_months_2024 = pd.period_range('2024-01', '2024-12', freq='M')
    df_all_months = pd.DataFrame({'month': all_months_2024})
    
    df_units = pd.merge(df_all_months, df_units, on='month', how='left').fillna({'units_sold': 0})
    
    return df_units


def merge_monthly_units_and_summary(df):
    """
    1) Compute monthly units sold.
    2) Compute monthly summary (fees, shipping, refunds, etc.).
    3) Merge them into one DataFrame by 'month'.
    """
    # Step 1: Get monthly units sold
    df_units = monthly_units_sold(df)
    
    # Step 2: Get monthly summary
    df_summary = monthly_summary(df)

    # Step 3: Merge on 'month'
    df_merged = pd.merge(df_units, df_summary, on='month', how='outer')
    df_merged.fillna(0, inplace=True)

    # Optional: reorder columns as desired
    final_order = [
        "month",
        "product sales",
        "units_sold",
        "selling fees",
        "Shipping Services",
        "Refund",
        "FBA Inventory Fee",
        "FBA Customer Return Fee",
        "product_minus_expenses"
    ]
    existing_cols = [col for col in final_order if col in df_merged.columns]
    remainder_cols = [col for col in df_merged.columns if col not in existing_cols]
    df_merged = df_merged[existing_cols + remainder_cols]

    return df_merged


def track_all_skus_yearly(df, sort_by="Units sold"):
    """
    For each SKU, compute:
      1) 'Units sold' - cumulative units
      2) 'Cumulative product sales' - cumulative product sales
    for the year 2024, and sort descending by the chosen column.
    """
    df['date/time'] = (
        df['date/time']
        .astype(str)
        .str.replace('PST', '', regex=False)
        .str.replace('PDT', '', regex=False)
        .str.strip()
    )
    df['date/time'] = pd.to_datetime(df['date/time'], errors='coerce')

    start_2024 = '2024-01-01'
    end_2024 = '2024-12-31'
    df_2024 = df.loc[
        (df['date/time'] >= start_2024) & (df['date/time'] <= end_2024)
    ].copy()

    df_2024['quantity'] = pd.to_numeric(df_2024['quantity'], errors='coerce').fillna(0)
    df_2024['product sales'] = pd.to_numeric(df_2024['product sales'], errors='coerce').fillna(0)

    # Group by (sku, order id, date/time)
    df_grouped = (
        df_2024
        .groupby(['sku', 'order id', 'date/time'], as_index=False)
        .agg({
            'quantity': 'sum',
            'product sales': 'sum'
        })
    )

    # Sort so cumsum is chronological for each SKU
    df_grouped.sort_values(by=['sku', 'date/time'], inplace=True)

    # Build cumulative columns
    df_grouped['Units sold'] = df_grouped.groupby('sku')['quantity'].cumsum()
    df_grouped['Cumulative product sales'] = df_grouped.groupby('sku')['product sales'].cumsum()

    # Remove the per‐row columns
    df_grouped.drop(columns=['quantity', 'product sales'], inplace=True)

    # Reorder columns
    df_grouped = df_grouped[
        ['sku', 'date/time', 'Units sold', 'Cumulative product sales']
    ]

    # Sort descending by the chosen column
    df_grouped.sort_values(by=sort_by, ascending=False, inplace=True)

    return df_grouped


def main():
    st.title("Amazon Transaction Analysis (2024)")
    st.subheader("Upload your 2024 transaction CSV or specify a path:")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    or_path = st.text_input("Or enter full path to CSV (e.g. '/Users/foo/data.csv')")

    df = pd.DataFrame()

    # Button to load CSV
    if st.button("Load CSV"):
        if uploaded_file is not None:
            st.info("Loading from uploaded file...")
            df = load_csv(file_buffer=uploaded_file)
        elif or_path.strip() != "":
            st.info(f"Loading from path: {or_path}")
            df = load_csv(file_path=or_path)
        else:
            st.warning("No file provided, please upload or specify a path.")

        if not df.empty:
            st.success("Data loaded successfully!")
            st.dataframe(df.head(10))

    if not df.empty:
        # Totals by Type
        st.subheader("Totals by Type")
        type_sum = get_type_sum(df)
        st.dataframe(type_sum)

        # Monthly Summaries
        st.subheader("Monthly Summaries (2024)")
        merged_df = merge_monthly_units_and_summary(df)
        st.dataframe(merged_df)

        # Cumulative Sales by SKU
        st.subheader("Cumulative Sales in 2024")
        all_skus_cumulative = track_all_skus_yearly(df)
        st.dataframe(all_skus_cumulative)


if __name__ == "__main__":
    main()
