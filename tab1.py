import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def main():

    def extract_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        data = []
        # Target the correct table inside <figure class="table">
        table = soup.select_one("figure.table table")
        if not table:
            return pd.DataFrame(columns=['Recruitment Names', 'Last Date'])

        rows = table.find_all('tr')

        for row in rows[1:]:  # skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:
                recruitment_name = cols[0].get_text(strip=True)
                last_date = cols[2].get_text(strip=True)
                data.append((recruitment_name, last_date))

        df = pd.DataFrame(data, columns=['Recruitment Names', 'Last Date'])

        # Clean date strings like "23rd August 2025" → "23 August 2025"
        df['Last Date'] = df['Last Date'].str.replace(r'(st|nd|rd|th)', '', regex=True)
        df['Last Date'] = pd.to_datetime(df['Last Date'], format='%d %B %Y', errors='coerce')

        df_sorted = df.sort_values(by='Last Date', ascending=False)
        return df_sorted

    def format_last_date(date):
        return date.strftime('%d %B %Y') if not pd.isnull(date) else ''

    url = "https://www.careerpower.in/government-jobs.html"
    response = requests.get(url)
    html_content = response.content

    df_sorted = extract_data(html_content)
    df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_last_date)

    # Split the 'Recruitment Names' column into 'Recruitment' and 'Posts'
    if not df_sorted.empty:
        df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True, n=1)
    else:
        df_sorted['Recruitment'] = []
        df_sorted['Posts'] = []

    st.title('Government Job Recruitments')
    st.dataframe(df_sorted[['Recruitment', 'Posts', 'Last Date']], height=800)

    # Refresh loop (avoid in Streamlit because it blocks the UI,
    # better to use st.button or st_autorefresh — but kept here for compatibility)
    while False:  # disabled to prevent Streamlit hang
        time.sleep(600)  # 10 minutes
        response = requests.get(url)
        html_content = response.content
        df_sorted = extract_data(html_content)
        df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_last_date)
        if not df_sorted.empty:
            df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True, n=1)
        st.dataframe(df_sorted[['Recruitment', 'Posts', 'Last Date']], height=800)

if __name__ == "__main__":
    main()
