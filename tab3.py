import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

def main():

    def scrape_page(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
    
        data = []
        table_rows = soup.select(".table-bordered tbody tr")
    
        for row in table_rows:
            columns = row.find_all("td")
            org = columns[0].text.strip()
            last_date = columns[3].text.strip()
            education = columns[2].text.strip()  # Extract the education column
            job_details = columns[1].text.strip()  # Extract the job details column
            data.append([org, last_date, education, job_details])
    
        return data
    
    def filter_jobs_by_education(data, education_levels):
        filtered_data = []
        for job in data:
            for el in education_levels:
                if el in job[2]:
                    job[2] = el  # Replace the entire education string with the matched level
                    filtered_data.append(job)
                    break  # Stop looking for other matches once one is found
        return filtered_data
    
    def clean_job_details(data):
        for job in data:
            posts_info = job[3].split('-')[-1].strip() 
            job[3] = posts_info  
        return data
    
    def scrape_all_pages(base_url, num_pages):
        all_data = []
        for page in range(1, num_pages + 1):
            url = f"{base_url}/page/{page}"
            page_data = scrape_page(url)
            all_data.extend(page_data)
        return all_data
    
    def parse_date(date_string):
        try:
            return datetime.strptime(date_string, '%d - %b - %Y')
        except ValueError:
            return datetime.min  # Return a very old date
    
    def sort_by_last_date(data):
        return sorted(data, key=lambda x: parse_date(x[1]), reverse=True)
    
    base_url = "https://allgovernmentjobs.in/latest-government-jobs"
    num_pages = 25  # Set the number of pages you want to scrape
    
    all_data = scrape_all_pages(base_url, num_pages)
    
    # Filter jobs by education level
    education_levels = ["B.E/ B.Tech", "Any Degree", "Electronics and Communication Engineering", "10th", "12th", "Intermediate (10+2)"]
    filtered_data = filter_jobs_by_education(all_data, education_levels)
    
    # Clean up the job details
    cleaned_data = clean_job_details(filtered_data)
    
    sorted_data = sort_by_last_date(cleaned_data)
    
    # Convert sorted_data into a DataFrame
    df_sorted_data = pd.DataFrame(sorted_data, columns=["Organization", "Last Date", "Education", "Job Details"])
    
    # Display the data in a Streamlit app
    st.title('Latest Government Jobs')
    
    # Add a drop-down filter for the 'Education' column
    education_option = st.selectbox(
        'Which education level you would like to display?',
         df_sorted_data['Education'].unique())
    
    # Filter the DataFrame based on the selected value
    filtered_df = df_sorted_data[df_sorted_data['Education'] == education_option]
    
    st.table(filtered_df)
