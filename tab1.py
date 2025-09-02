import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

@st.cache_data(ttl=21600)  # cache for 6 hours
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

                # Extract link
                link_tag = cols[0].find("a")
                link = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""

                data.append((recruitment_name, last_date, link))

        df = pd.DataFrame(data, columns=['Recruitment Names', 'Last Date', 'Link'])
        df['Last Date'] = pd.to_datetime(df['Last Date'], format='%dth %B %Y', errors='coerce')
        return df.sort_values(by='Last Date', ascending=False)

    api_key = "YOUR_SCRAPINGANT_API_KEY"
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

    # Split Recruitment into "Recruitment" and "Posts"
    df_sorted[['Recruitment', 'Posts']] = df_sorted['Recruitment Names'].str.split(' for ', expand=True)

    # Reorder for display
    df_display = df_sorted[['Recruitment', 'Posts', 'Last Date', 'Link']]

    # Show dataframe with clickable link column + autosize
    st.dataframe(
        df_display,
        use_container_width=True,
        column_config={
            "Link": st.column_config.LinkColumn("Details", display_text="🔗"),
        }
    )
