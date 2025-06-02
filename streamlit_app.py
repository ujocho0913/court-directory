"""
File: streamlit_app.py
Function: Main Python script that runs the EXTERNAL DIRECTORY (for 16th Circuit Court)
Author: Joseph Cho, ujcho@jacksongov.org
Date: April 12, 2025
"""

from pathlib import Path
import time
import streamlit as st
from psycopg2 import pool, OperationalError
# import pandas as pd
# from datetime import datetime, timezone

from database import external_log_activity
from photo import load_photo


# --- Configure Streamlit page settings --- 

jcpao_logo = Path("assets/logo/jcpao_logo_500x500.png")

st.set_page_config(
    page_title="JCPAO Court Directory", # court-view only
    page_icon=jcpao_logo, # cloudinary.CloudinaryImage('jcpao_logo_200x200').build_url()
    layout="wide", # "centered" or "wide"
    initial_sidebar_state="expanded",
    menu_items={
        # 'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "mailto:ujcho@jacksongov.org", # To report a bug, please email
        'About': "The JCPAO Portal was built by Joseph Cho and the Crime Strategies Unit (CSU) of the Jackson County Prosecuting Attorney's Office."
    }
)


# --- Initialize requisite functions --- 

# Define get_database_session() 
@st.cache_resource
def get_database_session(database_url):
    try: 
        # Create a database session object that points to the URL.
        return pool.SimpleConnectionPool(1, 10, database_url) # Initialize connection pool
    except OperationalError as e:
        st.error("Network is blocking connection to the database server. Please try again on a different network/internet connection, or reach out to admin at ujcho@jacksongov.org.")
        return None

# Establish NEON database connection (via psycopg2)
database_url = st.secrets["neonDB"]["database_url"]

try:
    db_connection = get_database_session(database_url)
except Exception as e:
    print(f"{e}")
    st.stop()


# --- Initialize session state ---
if "verified" not in st.session_state:
    st.session_state["verified"] = False

if "verified_email" not in st.session_state:
    st.session_state["verified_email"] = None

if "security_code" not in st.session_state:
    st.session_state["security_code"] = None


# --- Initialize st callback functions --- 

# Define attempt_verification()
def verify_attempt():

    # COURTS PORTAL 
    if ("@courts.mo.gov" in st.session_state["verified_email"] or ("@jacksongov.org" in st.session_state["verified_email"])) and (st.session_state["security_code"] == st.secrets["security_codes"]["court"]):
        external_log_activity(db_connection, "courts_log", st.session_state["verified_email"], st.context.ip_address)
        success_message = st.success(f"{st.session_state['verified_email']} successfully verified.")
        time.sleep(2)
        success_message.empty()
        st.session_state["verified"] = True
    else:
        fail_message = st.error("Failed to verify user. Please try again with an authorized email and security code.")
        time.sleep(2)
        fail_message.empty()


# --- Verification Portal --- 

# Define display_verification_portal()
def display_verification_portal():
    """Display COURT verification portal"""

    tabs = st.columns([1, 2, 1], gap="medium")

    with tabs[1]:

        with st.container(border=True):

            # Display JCPAO logo
            jcpao_logo = load_photo("jcpao_logo_200x200")
            st.markdown(f"<img src='{jcpao_logo}' width='200' style='display: block; margin: 0 auto;'>", unsafe_allow_html=True)

            # Display center title: JCPAO Portal
            st.markdown("<h1 style='text-align: center; color: black;'>JCPAO APA Directory (Courts)</h1>", unsafe_allow_html=True)
            
            st.divider()

            # Verification form
            with st.form("verify_court"):
                st.subheader(":material/gavel: 16th Circuit Court of Jackson County, Missouri")
                st.divider()

                # Email
                verified_email = st.text_input(
                    label="Enter email",
                    placeholder=None,
                    help=None,
                    key="verified_email",
                    disabled=st.session_state["verified"],
                )

                # Security code
                security_code = st.text_input(
                    label="Enter authorized security code",
                    placeholder=None,
                    help=None,
                    key="security_code",
                    disabled=st.session_state["verified"],
                    type="password",
                )

                # Submit 
                verify_button = st.form_submit_button(
                    label="Verify", # :material/keyboard_return: 
                    icon=":material/keyboard_return:",
                    disabled=st.session_state["verified"],
                    on_click=verify_attempt,
                    # kwargs=dict(security_code=security_code), # portal_type=portal_type, email=email, 
                    type="primary"
                )


# --- RUN STREAMLIT APP --- 

if not st.session_state["verified"]:
    display_verification_portal()

else:
    # Display APA Directory 
    court_pages = [
        st.Page("court_view.py", title="JCPAO Attorney Directory", icon=":material/contact_page:"),
    ]

    court_pg = st.navigation(court_pages)
    court_pg.run()