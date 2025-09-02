import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def main():

    def extract_data(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        data = []
        # Locate the right table inside <figure class="table">
        table = soup.select_one("figure.table table")
        if not table:
            return pd.DataFrame(columns=['Recruitment Names', 'Start Date', 'Last Date'])

        rows = table.find_all('tr')

        for row in rows[1:]:  # skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:
                recruitment_name = cols[0].get_text(strip=True)
                start_date = cols[1].get_text(strip=True)
                last_date = cols[2].get_text(strip=True)

                # Get link if available
                link = cols[0].find("a")["href"] if cols[0].find("a") else ""

                data.append((recruitment_name, start_date, last_date, link))

        df = pd.DataFrame(data, columns=['Recruitment Names', 'Start Date', 'Last Date', 'Link'])

        # Clean up dates like "23rd August 2025"
        for col in ['Start Date', 'Last Date']:
            df[col] = df[col].str.replace(r'(st|nd|rd|th)', '', regex=True)
            df[col] = pd.to_datetime(df[col], format='%d %B %Y', errors='coerce')

        # Sort by Last Date (descending)
        df_sorted = df.sort_values(by='Last Date', ascending=False)
        return df_sorted

    def format_date(date):
        return date.strftime('%d %B %Y') if not pd.isnull(date) else ''

    url = "https://www.careerpower.in/government-jobs.html"
    response = requests.get(url)
    html_content = response.content

    df_sorted = extract_data(html_content)

    # Reformat dates back to strings for display
    df_sorted['Start Date'] = df_sorted['Start Date'].apply(format_date)
    df_sorted['Last Date'] = df_sorted['Last Date'].apply(format_date)

    st.title('Latest Govt Jobs 2025')
    st.dataframe(df_sorted[['Recruitment Names', 'Start Date', 'Last Date']], height=800)

if __name__ == "__main__":
    main()
