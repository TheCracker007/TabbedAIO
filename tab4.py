import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import datetime, timedelta

def main():
    st.title("Latest Notification")

    url = 'https://www.sarkariresult.app/latest-jobs/'
    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    # Create a list to store the job opportunities
    jobs = []

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
        last_date_str = job_details.replace('Last Date:', '').replace('(', '').replace(')', '').strip()
        try:
            last_date = datetime.strptime(last_date_str, '%d %B %Y')
        except ValueError:
            last_date = None

        # Check if last date is not None and is on or after today's date minus 1 day
        if last_date and (last_date == datetime.now().date() or last_date == datetime.now().date() - timedelta(days=1)):
            # Add the job opportunity to the list
            jobs.append({
                'title': title,
                'num_posts': num_posts,
                'last_date': last_date,
                'last_date_str': last_date_str,
                'job_link': job_link
            })

    # Sort the jobs by last date in ascending order
    jobs.sort(key=lambda x: x['last_date'] or datetime.max, reverse=False)

    # Create the table header
    table = '| Job Title | Vacancies | Last Date | Link |\n'
    table += '| --- | --- | --- | --- |\n'

    # Add the rows to the table
    for job in jobs:
        table += f"| {job['title']} | {job['num_posts']} | {job['last_date_str']} | {job['job_link']} |\n"

    # Display the table in Streamlit
    st.markdown(table, unsafe_allow_html=True)
