import streamlit as st
import requests
from bs4 import BeautifulSoup

# Streamlit app title
st.title("Sarkari Result Latest Jobs")

url = 'https://www.sarkariresult.app/latest-jobs/'
response = requests.get(url)
html = response.text

soup = BeautifulSoup(html, 'html.parser')

# Create the table header
table = '| Job Title | Number of Posts | Last Date | Link |\n'
table += '| --- | --- | --- | --- |\n'

# Find all the job opportunities listed on the page
for element in soup.select('ul.su-posts li.su-post')[2:]:
    # Extract the job title, details, and link
    job_title = element.a.get_text(strip=True)
    job_details = element.span.get_text(strip=True) if element.span else ''
    job_link = element.a['href']
    
    # Split the job title into title and number of posts
    split_title = job_title.rsplit(' ', 2)
    title = ' '.join(split_title[:-2])
    num_posts = ' '.join(split_title[-2:]) if len(split_title) > 2 else ''
    
    # Extract the last date from the job details
    last_date = job_details.replace('Last Date:', '').strip()
    
    # Add a row to the table
    table += f'| {title} | {num_posts} | {last_date} | {job_link} |\n'

# Display the table in Streamlit
st.markdown(table, unsafe_allow_html=True)
