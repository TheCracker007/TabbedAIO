import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def main():

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
        df_sorted = df.sort_values(by='Last Date', ascending=False)

        return df_sorted

    def format_last_date(date):
        return date.strftime('%d %B %Y') if not pd.isnull(date) else ''

    # Use ScrapingAnt API instead of direct request
    api_key = "762ca47deab845f8a88b16d0cce54e03"  # <-- replace with your real key
    target_url = "https://www.careerpower.in/government-jobs.html"
    api_url = f"https://api.scrapingant.com/v2/general?url={target_url}&x-api-key={api_key}"

    response = requests.get(api_url)
    html_content = response.text

    df_sorted = extract_data(html_content)
    if df_sorted.empty:
        st.error("⚠ Could not extract jobs data")
        return

    df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_last_date)
    df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True)

    st.title('Government Job Recruitments')
    st.dataframe(df_sorted[['Recruitment', 'Posts', 'Last Date']], height=800)

    # Refresh loop (optional: can be removed if not needed)
    while False:  # set to True if you want background refresh inside Streamlit (not recommended)
        time.sleep(600)  # Sleep for 10 minutes
        response = requests.get(api_url)
        html_content = response.text
        df_sorted = extract_data(html_content)
        df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_last_date)
        df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True)
        st.dataframe(df_sorted[['Recruitment', 'Posts', 'Last Date']], height=800)
