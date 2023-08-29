import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
from tab1 import main as main_tab1
from tab2 import main as main_tab2

# Set the page layout to wide mode
st.set_page_config(layout="wide")

tab = st.sidebar.radio("Tabs", ("Tab 1", "Tab 2"))

if tab == "Tab 1":
    main_tab1()
elif tab == "Tab 2":
    main_tab2()
