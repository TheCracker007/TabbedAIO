import streamlit as st
from tab1 import main as main_tab1
from tab2 import main as main_tab2
#from tab3 import main as main_tab3
#from tab4 import main as main_tab4
#from tab5 import main as main_tab5

# Set the page layout to wide mode
st.set_page_config(layout="wide")

#tab = st.sidebar.radio("Tabs", ("Tab 1", "Tab 2", "Tab 3", "Tab 4", "Tab 5"))
tab = st.sidebar.radio("Content", ("Source 1", "Source 2"))

if tab == "Source 1":
    main_tab1()
elif tab == "Source 2":
    main_tab2()
#elif tab == "Tab 3":
#    main_tab3()
#elif tab == "Tab 4":
#    main_tab4()
#elif tab == "Tab 5":
#    main_tab5()

# Add a button to rerun the app
if st.button('Rerun App'):
    st.experimental_rerun()
