import streamlit as st
import pandas as pd

# Function to process data and calculate differences
def process_data(df, start_date_1, end_date_1, start_date_2, end_date_2):
    # Convert start and end dates to pandas timestamps
    start_date_1 = pd.Timestamp(start_date_1)
    end_date_1 = pd.Timestamp(end_date_1)
    start_date_2 = pd.Timestamp(start_date_2)
    end_date_2 = pd.Timestamp(end_date_2)

    # Filter data for both date ranges
    mask1 = (df['date'] >= start_date_1) & (df['date'] <= end_date_1)
    mask2 = (df['date'] >= start_date_2) & (df['date'] <= end_date_2)
    df1 = df.loc[mask1].groupby(['page', 'query', 'country', 'device']).agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'position': 'mean'
    }).reset_index().rename(columns={
        'clicks': 'clicks_1st_range',
        'impressions': 'imp_1st_range',
        'ctr': 'ctr_1st_range',
        'position': 'position_1st_range'
    })

    df2 = df.loc[mask2].groupby(['page', 'query', 'country', 'device']).agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': 'mean',
        'position': 'mean'
    }).reset_index().rename(columns={
        'clicks': 'clicks_2nd_range',
        'impressions': 'imp_2nd_range',
        'ctr': 'ctr_2nd_range',
        'position': 'position_2nd_range'
    })

    # Merge the two DataFrames on the common columns
    combined_df = pd.merge(df1, df2, on=['page', 'query', 'country', 'device'], how='outer')

    # Calculate differences
    combined_df['Clicks Diff'] = combined_df['clicks_2nd_range'] - combined_df['clicks_1st_range']
    combined_df['Imp. Diff'] = combined_df['imp_2nd_range'] - combined_df['imp_1st_range']
    combined_df['ctr Diff'] = combined_df['ctr_2nd_range'] - combined_df['ctr_1st_range']
    combined_df['position Diff'] = combined_df['position_2nd_range'] - combined_df['position_1st_range']

    return combined_df

# Streamlit app
def main():
    st.title("CSV Date Range Comparison Tool")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['date'] = pd.to_datetime(df['date'])  # Convert date column to datetime

        # Minimum and maximum dates in the dataset
        min_date, max_date = df['date'].min(), df['date'].max()

        # Date range selectors using st.date_input
        st.subheader("First Date Range")
        start_date_1, end_date_1 = st.date_input(
            "Select range for first period",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range_1"
        )

        st.subheader("Second Date Range")
        start_date_2, end_date_2 = st.date_input(
            "Select range for second period",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="date_range_2"
        )

        if st.button("Process Data"):
            # Processing data
            final_df = process_data(df, start_date_1, end_date_1, start_date_2, end_date_2)

            # Show processed data
            st.write("Processed Data:")
            st.write(final_df)

            # Convert DataFrame to CSV for download
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Processed Data as CSV",
                csv,
                "processed_data.csv",
                "text/csv",
                key='download-csv'
            )

if __name__ == "__main__":
    main()
