import streamlit as st
from tab1 import main as main_tab1
from tab2 import main as main_tab2
from tab3 import main as main_tab3
from tab4 import main as main_tab4

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Add custom CSS from GitHub
custom_css_url = "https://raw.githubusercontent.com/TheCracker007/TabbedAIO/main/custom.css"
st.markdown(f'<link rel="stylesheet" href="{custom_css_url}">', unsafe_allow_html=True)

# Your content goes here
st.title("Streamlit App with Custom Scroll Bar")

tab = st.sidebar.radio("Content", ("Source 1", "Source 2", "Source 3", "Source 4"))

if tab == "Source 1":
    main_tab1()
elif tab == "Source 2":
    main_tab2()
elif tab == "Source 3":
    main_tab3()
elif tab == "Source 4":
    main_tab4()
