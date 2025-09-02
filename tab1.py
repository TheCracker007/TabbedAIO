import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def main():

    def extract_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        data = []
        # Find the heading "Latest Govt Jobs 2025" and then its following table
        heading = soup.find("h2", string=lambda t: t and "Latest Govt Jobs 2025" in t)
        table = heading.find_next("table") if heading else None

        if not table:
            return pd.DataFrame(columns=['Recruitment Names', 'Start Date', 'Last Date', 'Link'])

        rows = table.find_all('tr')

        for row in rows[1:]:  # skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:
                recruitment_name = cols[0].get_text(strip=True)
                start_date = cols[1].get_text(strip=True)
                last_date = cols[2].get_text(strip=True)

                # Extract link if present
                link = cols[0].find("a")["href"] if cols[0].find("a") else ""

                data.append((recruitment_name, start_date, last_date, link))

        df = pd.DataFrame(data, columns=['Recruitment Names', 'Start Date', 'Last Date', 'Link'])

        # Clean date strings like "23rd August 2025"
        for col in ['Start Date', 'Last Date']:
            df[col] = df[col].str.replace(r'(st|nd|rd|th)', '', regex=True)
            df[col] = pd.to_datetime(df[col], format='%d %B %Y', errors='coerce')

        # Sort by Last Date (latest first)
        df_sorted = df.sort_values(by='Last Date', ascending=False)
        return df_sorted

    def format_date(date):
        return date.strftime('%d %B %Y') if not pd.isnull(date) else ''

    url = "https://www.careerpower.in/government-jobs.html"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    html_content = response.content

    df_sorted = extract_data(html_content)

    # Convert datetime back to formatted string for display
    for col in ['Start Date', 'Last Date']:
        df_sorted[col] = df_sorted[col].apply(format_date)

    st.title('Latest Govt Jobs 2025')
    st.dataframe(df_sorted[['Recruitment Names', 'Start Date', 'Last Date']], height=800)

if __name__ == "__main__":
    main()
