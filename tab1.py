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
    # Replace "URL_OF_THE_WEBSITE" with the actual URL of the website you want to scrape
    url = "https://www.careerpower.in/government-jobs.html"
    response = requests.get(url)
    html_content = response.content
    df_sorted = extract_data(html_content)
    df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_last_date)  # Format the date
    # Split the 'Recruitment Names' column into two columns: 'Recruitment' and 'Posts'
    df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True)
    st.title('Government Job Recruitments')
    st.dataframe(df_sorted[['Recruitment', 'Posts', 'Last Date']], height=800)
    # Refresh the data in the background
    while True:
        time.sleep(600)  # Sleep for 10 minutes (600 seconds)
        response = requests.get(url)
        html_content = response.content
        df_sorted = extract_data(html_content)
        df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_last_date)
        df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True)
        st.dataframe(df_sorted[['Recruitment', 'Posts', 'Last Date']], height=800)
