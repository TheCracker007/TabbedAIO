import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

def fetch_jobs():
    api_key = "YOUR_SCRAPINGANT_API_KEY"  # replace with your key
    url = "https://www.careerpower.in/government-jobs.html"

    api_url = f"https://api.scrapingant.com/v2/general?url={url}&x-api-key={api_key}"
    response = requests.get(api_url)

    if response.status_code != 200:
        st.error(f"Failed to fetch jobs data (status: {response.status_code})")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")

    heading = soup.find("h2", string=lambda t: t and "Latest Govt Jobs 2025" in t)
    table = heading.find_next("table") if heading else None

    if not table:
        st.warning("⚠ Jobs table not found")
        return pd.DataFrame()

    rows = table.find_all("tr")
    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            recruitment = cols[0].get_text(strip=True)
            start = cols[1].get_text(strip=True)
            last = cols[2].get_text(strip=True)
            link_tag = cols[0].find("a")
            link = link_tag["href"] if link_tag and link_tag.has_attr("href") else ""
            data.append((recruitment, start, last, link))

    return pd.DataFrame(data, columns=["Recruitment Names", "Start Date", "Last Date", "Link"])


# Streamlit UI
st.header("Government Jobs - CareerPower.in")

df = fetch_jobs()
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No jobs available right now")
