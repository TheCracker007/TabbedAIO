import streamlit as st
from tab1 import main as main_tab1
from tab2 import main as main_tab2

# Set the page layout to wide mode
st.set_page_config(layout="wide")

tab = st.sidebar.radio("Content", ("Source 1", "Source 2"))

if tab == "Source 1":
    main_tab1()
elif tab == "Source 2":
    main_tab2()
