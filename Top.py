import streamlit as st
from tab1 import main as main_tab1
from tab2 import main as main_tab2
from tab3 import main as main_tab3
from tab4 import main as main_tab4

# Set the page layout to wide mode
st.set_page_config(layout="wide")

st.title("All Content")

st.header("Tab 1")
main_tab1()

st.header("Tab 2")
main_tab2()

st.header("Tab 3")
main_tab3()

st.header("Tab 4")
main_tab4()
