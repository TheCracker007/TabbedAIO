import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def main():
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def extract_data(html_content):
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            data = []
            
            # Find the table with job listings
            table = soup.find('figure', class_='table')
            if table:
                table = table.find('table')
            else:
                # Fallback: look for any table
                table = soup.find('table')
            
            if table is None:
                st.error("No job table found on the webpage. The website structure may have changed.")
                return pd.DataFrame()
            
            # Get table body
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
            else:
                rows = table.find_all('tr')
            
            if len(rows) <= 1:
                st.warning("No data rows found in the table.")
                return pd.DataFrame()
            
            # Skip header row and extract data
            for row in rows[1:]:  # Skip header row
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # Extract recruitment name (remove <a> tags but keep text)
                    recruitment_cell = cols[0]
                    if recruitment_cell.find('a'):
                        recruitment_name = recruitment_cell.find('a').get_text(strip=True)
                        job_link = recruitment_cell.find('a').get('href', '')
                    else:
                        recruitment_name = recruitment_cell.get_text(strip=True)
                        job_link = ''
                    
                    # Extract start date and last date
                    start_date = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                    last_date = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                    
                    data.append({
                        'Recruitment Names': recruitment_name,
                        'Start Date': start_date,
                        'Last Date': last_date,
                        'Job Link': job_link
                    })
            
            if not data:
                st.warning("No valid job data found in the table.")
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            
            # Parse dates safely
            def parse_date_safe(date_str):
                if not date_str or date_str in ['--', 'TBA', '']:
                    return None
                
                try:
                    # Handle various date formats
                    date_str = date_str.strip()
                    
                    # Remove ordinal suffixes (1st, 2nd, 3rd, etc.)
                    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
                    
                    # Try different date formats
                    formats = [
                        '%d %B %Y',      # 14 September 2025
                        '%d %b %Y',      # 14 Sep 2025
                        '%d/%m/%Y',      # 14/09/2025
                        '%d-%m-%Y',      # 14-09-2025
                        '%Y-%m-%d',      # 2025-09-14
                    ]
                    
                    for fmt in formats:
                        try:
                            return pd.to_datetime(date_str, format=fmt)
                        except:
                            continue
                    
                    # If none work, try pandas' flexible parser
                    return pd.to_datetime(date_str, errors='coerce')
                    
                except Exception as e:
                    return None
            
            # Parse dates
            df['Start Date Parsed'] = df['Start Date'].apply(parse_date_safe)
            df['Last Date Parsed'] = df['Last Date'].apply(parse_date_safe)
            
            # Sort by last date (most recent first, with null dates at the end)
            df = df.sort_values('Last Date Parsed', ascending=False, na_position='last')
            
            return df
            
        except Exception as e:
            st.error(f"Error extracting data: {str(e)}")
            return pd.DataFrame()

    def format_date_display(date):
        """Format date for display"""
        try:
            if pd.isnull(date):
                return 'Not specified'
            return date.strftime('%d %B %Y')
        except:
            return 'Not specified'

    # Main UI
    st.title('🏛️ Government Job Recruitments 2025')
    
    # Add refresh button and info
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        refresh_button = st.button("🔄 Refresh Data")
    with col3:
        st.info("📅 Data from CareerPower.in")
    
    # Show loading spinner
    with st.spinner('🔍 Fetching latest government jobs...'):
        try:
            url = "https://www.careerpower.in/government-jobs.html"
            
            # Headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            df = extract_data(response.content)
            
            if not df.empty:
                # Split recruitment names to separate title and posts
                def split_recruitment_name(name):
                    try:
                        # Look for patterns like "for X Vacancies", "for X Posts"
                        if ' for ' in name:
                            parts = name.rsplit(' for ', 1)
                            return parts[0].strip(), parts[1].strip()
                        elif 'Notification Out' in name:
                            # Handle "Name Notification Out for X Vacancies"
                            clean_name = name.replace('Notification Out', '').strip()
                            if ' for ' in clean_name:
                                parts = clean_name.rsplit(' for ', 1)
                                return parts[0].strip(), parts[1].strip()
                            return clean_name, ''
                        else:
                            return name, ''
                    except:
                        return name, ''
                
                # Apply the splitting function
                df[['Job Title', 'Vacancy Info']] = df['Recruitment Names'].apply(
                    lambda x: pd.Series(split_recruitment_name(x))
                )
                
                # Format dates for display
                df['Start Date Display'] = df['Start Date Parsed'].apply(format_date_display)
                df['Last Date Display'] = df['Last Date Parsed'].apply(format_date_display)
                
                # Filter options
                st.subheader("📋 Filter Jobs")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filter by upcoming deadlines
                    today = datetime.now().date()
                    upcoming_only = st.checkbox("Show only upcoming deadlines")
                    
                with col2:
                    # Search filter
                    search_term = st.text_input("Search jobs", placeholder="Enter keywords...")
                
                # Apply filters
                filtered_df = df.copy()
                
                if upcoming_only:
                    filtered_df = filtered_df[
                        (filtered_df['Last Date Parsed'].dt.date >= today) | 
                        (filtered_df['Last Date Parsed'].isna())
                    ]
                
                if search_term:
                    filtered_df = filtered_df[
                        filtered_df['Job Title'].str.contains(search_term, case=False, na=False) |
                        filtered_df['Vacancy Info'].str.contains(search_term, case=False, na=False)
                    ]
                
                # Display results
                st.subheader(f"📊 Found {len(filtered_df)} Government Jobs")
                
                if not filtered_df.empty:
                    # Create display dataframe
                    display_df = filtered_df[['Job Title', 'Vacancy Info', 'Start Date Display', 'Last Date Display']].copy()
                    display_df.columns = ['Job Title', 'Vacancies', 'Start Date', 'Last Date']
                    
                    # Style the dataframe
                    st.dataframe(
                        display_df,
                        height=600,
                        use_container_width=True,
                        column_config={
                            "Job Title": st.column_config.TextColumn(
                                "Job Title",
                                width="large"
                            ),
                            "Vacancies": st.column_config.TextColumn(
                                "Vacancies",
                                width="medium"
                            ),
                            "Start Date": st.column_config.TextColumn(
                                "Start Date",
                                width="medium"
                            ),
                            "Last Date": st.column_config.TextColumn(
                                "Last Date",
                                width="medium"
                            ),
                        }
                    )
                    
                    # Statistics
                    st.subheader("📈 Quick Stats")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Jobs", len(filtered_df))
                    
                    with col2:
                        upcoming_count = len(filtered_df[
                            (filtered_df['Last Date Parsed'].dt.date >= today) & 
                            (filtered_df['Last Date Parsed'].notna())
                        ])
                        st.metric("Upcoming Deadlines", upcoming_count)
                    
                    with col3:
                        # Count jobs with vacancy numbers
                        vacancy_jobs = len(filtered_df[
                            filtered_df['Vacancy Info'].str.contains('Vacanc', case=False, na=False)
                        ])
                        st.metric("Jobs with Vacancies", vacancy_jobs)
                    
                else:
                    st.warning("No jobs match your current filters.")
                
                st.success(f"✅ Successfully loaded {len(df)} job listings from CareerPower")
                
            else:
                st.error("❌ No job data found. Please check the website or try again later.")
                
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again later.")
        except requests.exceptions.ConnectionError:
            st.error("🌐 Connection error. Please check your internet connection.")
        except requests.exceptions.HTTPError as e:
            st.error(f"🚫 HTTP error occurred: {e}")
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {str(e)}")
    
    # Footer information
    st.markdown("---")
    st.markdown("**Source:** [CareerPower Government Jobs](https://www.careerpower.in/government-jobs.html)")
    st.markdown("**Note:** Data is refreshed every 10 minutes. Click 'Refresh Data' for immediate updates.")

if __name__ == "__main__":
    main()
