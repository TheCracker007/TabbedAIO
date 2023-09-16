import streamlit as st
from tab1 import main as main_tab1
from tab2 import main as main_tab2
from tab3 import main as main_tab3
from tab4 import main as main_tab4

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Your content goes here
st.title("Streamlit App with Scroll to Bottom")

# Add content to your app
for i in range(100):
    st.write(f"This is some content #{i+1}")

# Add a "Scroll to Bottom" button
if st.button("Scroll to Bottom"):
    # Use JavaScript to scroll to the bottom of the page
    st.write('<script>window.scrollTo(0, document.body.scrollHeight);</script>', unsafe_allow_html=True)

tab = st.sidebar.radio("Content", ("Source 1", "Source 2", "Source 3", "Source 4"))

if tab == "Source 1":
    main_tab1()
elif tab == "Source 2":
    main_tab2()
elif tab == "Source 3":
    main_tab3()
elif tab == "Source 4":
    main_tab4()
