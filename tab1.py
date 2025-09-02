import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

@st.cache_data(ttl=21600)  # cache for 6 hours (21600 seconds)
def fetch_jobs():
    def extract_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        data = []
        table = soup.find('table')
        if not table:
            return pd.DataFrame()

        rows = table.find_all('tr')
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 3:
                recruitment_name = cols[0].get_text(strip=True)
                last_date = cols[2].get_text(strip=True)
                data.append((recruitment_name, last_date))

        df = pd.DataFrame(data, columns=['Recruitment Names', 'Last Date'])
        df['Last Date'] = pd.to_datetime(df['Last Date'], format='%dth %B %Y', errors='coerce')
        return df.sort_values(by='Last Date', ascending=False)

    api_key = "762ca47deab845f8a88b16d0cce54e03"
    target_url = "https://www.careerpower.in/government-jobs.html"
    api_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={api_key}"

    response = requests.get(api_url)
    html_content = response.text

    return extract_data(html_content)

def main():
    st.title('Government Job Recruitments')

    df_sorted = fetch_jobs()
    if df_sorted.empty:
        st.error("⚠ Could not extract jobs data")
        return

    def format_last_date(date):
        return date.strftime('%d %B %Y') if not pd.isnull(date) else ''

    df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_last_date)
    df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True)

    st.dataframe(df_sorted[['Recruitment', 'Posts', 'Last Date']], height=800)
