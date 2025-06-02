"""
File: external_view.py
Function: Streamlit page for JCPAO directory (EXTERNAL view for COURTS)
Author: Joseph Cho, ujcho@jacksongov.org
Date: April 30, 2025
"""

import streamlit as st
from pathlib import Path 
import pandas as pd

# from initialize_st import initialize_session_state
from database import get_database_session, get_apa_data
from photo import load_photo


# --- Configure Streamlit page settings --- 
jcpao_logo = Path("assets/logo/jcpao_logo_500x500.png")

# --- JCPAO Streamlit page logo --- 
st.logo(jcpao_logo, size="large", link="https://www.jacksoncountyprosecutor.com")

# Establish NEON database connection (via psycopg2)
database_url = st.secrets["neonDB"]["database_url"]

try:
    db_connection = get_database_session(database_url)
except Exception as e:
    print(f"{e}")
    st.stop()

def parse_enum(array):
    if pd.isna(array):
        return []
    array = array.strip('{}')
    return array.split(',') if array else []

apa_data = get_apa_data(db_connection) # "emp_view" / apa_data
apa_data['Assigned Unit'] = apa_data['Assigned Unit'].apply(parse_enum) # unit_enum[]
apa_data['Race'] = apa_data['Race'].apply(parse_enum) # race_enum[]


# --- Initialize session state --- 

if "selected_position" not in st.session_state:
    st.session_state["selected_position"] = "All"

if "selected_unit" not in st.session_state:
    st.session_state["selected_unit"] = "All"

if "selected_location" not in st.session_state:
    st.session_state["selected_location"] = "All"

# st.session_state.setdefault("searched_text", "")
if "searched_text" not in st.session_state: # 'search_name'
    st.session_state["searched_text"] = ""

if "view" not in st.session_state:
    st.session_state["view"] = "Main Directory"


# --- Define callback functions --- 

# Define update_df() function
def update_df():

    filtered_df = apa_data.copy()

    if st.session_state["selected_position"] != 'All':
        filtered_df = filtered_df[filtered_df['Position']==st.session_state["selected_position"]].reset_index(drop=True)
    if st.session_state["selected_unit"] != 'All':
        filtered_df = filtered_df[filtered_df['Assigned Unit'].apply(lambda x: st.session_state["selected_unit"] in x)].reset_index(drop=True)
    if st.session_state["selected_location"] != 'All': 
        filtered_df = filtered_df[filtered_df['Office Location']==st.session_state["selected_location"]].reset_index(drop=True)
    if st.session_state["searched_text"]: # Added searched_text to main clickback action 
        searched_text = st.session_state["searched_text"].strip().lower()
        search_cols = ["Full Name", "First Name", "Middle Name", "Last Name", "Suffix", "Preferred Name"]
        filtered_df = filtered_df[
            filtered_df[search_cols].apply(lambda row: any(searched_text in str(value).lower() for value in row), axis=1)
        ].reset_index(drop=True)

    st.session_state["filtered_df"] = filtered_df.reset_index(drop=True)

# Reset filters button
def reset_filters():
    st.session_state["selected_position"] = "All"
    st.session_state["selected_unit"] = "All"
    st.session_state["selected_location"] = "All"
    st.session_state["searched_text"] = ""
    filtered_df = apa_data.copy()
    st.session_state["filtered_df"] = filtered_df

# Callback function for which directory to view
def view_directory():
    st.session_state['view'] = st.session_state["directory_view"]

# --- Sidebar Filter functions --- 

with st.sidebar:
    # Select options: position / unit / location / birthday month 
    st.title("Jackson County Prosecuting Attorney's Office")
    st.write("***Assistant Prosecuting Attorney Directory***")
    st.divider()
    st.write("Please use navigate the JCPAO APA directory to view information on all active attorneys in the Jackson County Prosecuting Attorney's Office.")
    st.divider()
    st.selectbox(
            "Select the directory to view",
            options=['Main Directory','Contact Directory'],
            key="directory_view",
            on_change=view_directory
        )
    st.divider()
    # Filter by job position: 
    positions_dict = {
        'All': 'All Job Positions', 
        'Exec': 'Executive Staff', 
        'CTA': 'Chief Trial Attorneys', 
        'TTL': 'Team Trial Leaders', 
        'APA': 'Assistant Prosecuting Attorneys',
        # 'I': 'Investigators',
        # 'VA': 'Victim Advocates',
        # 'LA': 'Legal Assistants',
        # 'SS': 'Support Staff'
    }
    position_options = st.selectbox(
        label= "Filter by Position:", 
        options=positions_dict.keys(), # ('All', 'Exec', 'CTA', 'TTL', 'APA', 'I', 'VA', 'LA', 'SS')
        index=0, # All
        format_func=lambda x: positions_dict[x],
        key='selected_position',
        placeholder="Select position to filter",
        on_change=update_df,
    )

    # Filter by unit_enum[]: 
    units_dict = {
        'All': 'All Units',
        'Exec': 'Executive Staff',
        'GCU': 'General Crimes Unit (GCU)',
        'SVU': 'Special Victims Unit (SVU)',
        'VCU': 'Violent Crimes Unit (VCU)',
        'CSU': 'Crime Strategies Unit (CSU)',
        # 'COMBAT': 'COMBAT',
        'Drug': 'Drug Court',
        'FSD': 'Family Support Division'
    }
    unit_options = st.selectbox(
        label="Filter by Assigned Unit:",
        options=units_dict.keys(), # ('Exec', 'GCU', 'SVU', 'VCU', 'CSU', 'COMBAT', 'Drug', 'FSD')
        index=0, # All
        format_func=lambda x: units_dict[x],
        key='selected_unit',
        placeholder="Select unit to filter",
        on_change=update_df,
    )

    # Filter by location: 
    locations_dict = {
        'All': 'All Office Locations',
        'Dt-11': 'Downtown Courthouse, 11th floor',
        'Dt-10': 'Downtown Courthouse, 10th floor',
        # 'Dt-9': 'Downtown Courthouse, 9th floor (COMBAT)',
        'Dt-7M': 'Downtown Courthouse, 7M',
        'Indy': 'Eastern Jackson Courthouse, Independence',
        'FSD': 'Family Support Division'
    }
    location_options = st.selectbox(
        label="Filter by Office Location:",
        options=locations_dict.keys(), # ('Dt-11', 'Dt-10', 'Dt-9', 'Dt-7M', 'Indy', 'FSD')
        index=0, # All
        format_func=lambda x: locations_dict[x],
        key='selected_location',
        placeholder="Select office location to filter",
        on_change=update_df,
    )

    # Reset filters 
    refresh = st.button(
        label="Reset Filters",
        key="filter_reset",
        on_click=reset_filters,
        type="secondary",
        icon="🔄",
    )

    # Logout 
    logout = st.button(
        label="Logout",
        key="logout",
        on_click=lambda: st.session_state.clear(), # Clear session state
        type="secondary",
        icon=":material/logout:"
    )

    # st.write(
    #     """
    #         Color Legend:
    #         :red-badge[**Executive Staff**]
    #         :orange-badge[**Chief Trial Attorneys**]
    #         :green-badge[**Trial Team Leaders**]
    #         :blue-badge[**Assistant Prosecuting Attorneys**]
    #     """
    # )


# --- Internal Directory HELPER funcs --- 

def configure_badge(row):

    # Only possible st.badge colors: blue, green, orange, red, violet, gray/grey, or primary
    
    # 'Assigned Unit' - 'Exec' / 'GCU' / 'SVU' / 'VCU' / 'CSU' / 'COMBAT' / 'Drug' / 'FSD'
    if row['Assigned Unit']:
        unit = ' / '.join(row['Assigned Unit'])
    else:
        unit = 'N/A'
    
    # Drug Court 
    if 'Drug Court' in unit:
        unit = unit.replace("Drug", "Drug Court")
    
    # 'Position' - 'Exec' / 'CTA' / 'TTL' / 'APA'
    if row['Position'] == 'Exec':
        if row['Position'] == unit:
            position_badge = f":red-badge[**Executive Staff**]"
        else:
            position_badge = f":red-badge[**Executive Staff - {unit}**]"
    elif row['Position'] == 'CTA':
        position_badge = f":orange-badge[**Chief Trial Attorney - {unit}**]"
    elif row['Position'] == 'TTL':
        position_badge = f":green-badge[**Trial Team Leader - {unit}**]"
    elif row['Position'] == 'APA':
        position_badge = f":blue-badge[**Assistant Prosecuting Attorney - {unit}**]"
    
    return position_badge

def reformat_location(row):

    # 'Office Location' - 'Dt-11' / 'Dt-10' / 'Dt-9' / 'Dt-7M' / 'Indy' / 'FSD'
    if row['Office Location'] == 'Dt-11':
        office_location = "Downtown Courthouse, 11th floor"
    elif row['Office Location'] == 'Dt-10':
        office_location = "Downtown Courthouse, 10th floor"
    elif row['Office Location'] == 'Dt-9':
        office_location = "Downtown Courthouse, 9th floor (COMBAT)"
    elif row['Office Location'] == 'Dt-7M':
        office_location = "Downtown Courthouse, 7M"
    elif row['Office Location'] == 'Indy':
        office_location = "Eastern Jackson Courthouse, Independence"
    elif row['Office Location'] == 'FSD':
        office_location = "Family Support Division"

    return office_location

def reformat_phone_num(phone_num):
    # Handle NaN values or non-string types 
    if not isinstance(phone_num, str) or pd.isna(phone_num):
        return phone_num
    
    # Check length is 10-digits, then reformat 
    if len(phone_num) == 10:
        return f"{phone_num[:3]}-{phone_num[3:6]}-{phone_num[6:]}"
    else:
        return phone_num

def display_attorney(row):

    with st.container():

        col1, col2 = st.columns([1,1.25], gap="small", vertical_alignment="center")

        with col1:
            
            # Headshot Photo (if None, JCPAO logo)
            if row['PhotoID'] is None: 
                st.image(jcpao_logo, width=400)
            else:
                headshot_path = "JCPAO_headshots/"+row['PhotoID']
                attorney_headshot = load_photo(headshot_path)
                st.image(attorney_headshot, width=400)

        with col2:

            # Employee Name
            st.header(f"{row['Full Name']}")

            # Job Title
            st.subheader(f"{row['Job Title']}")

            # Position
            position_badge = configure_badge(row)
            st.markdown(position_badge)
            
            # Office Location
            office_location = reformat_location(row)
            st.write(f"**Office Location:** {office_location}")

            # Work Email Address
            st.write(f"**Email Address:** {row['Work Email Address']}")

            # Work Phone Number 
            work_phone = reformat_phone_num(row['Work Phone #'])
            if str(row['Work Phone #']).startswith("816881"):
                st.write(f"**Work Phone:** {work_phone} (ext. {str(row['Work Phone #'])[-4:]})")
            else:
                st.write(f"**Work Phone:** {work_phone}")
            
        st.divider()


# --- Display INTERNAL Directory ---
st.markdown("<h1 style='text-align: center; color: black;'>JCPAO Assistant Prosecuting Attorney Directory</h1>", unsafe_allow_html=True)
st.divider()

def main_directory():

    df = st.session_state.get("filtered_df", apa_data)

    # Text search
    searched_text = st.text_input(
        "Search attorney name:",
        key="searched_text",
        # on_change=update_df,
    )

    text_search = st.button(
        "Search",
        icon="🔎",
        on_click=update_df,
        key="text_search",
    )

    st.divider()

    if df.empty:
        st.warning("No attorneys found matching the search criteria.")
    else:
        for i, row in df.iterrows():
            display_attorney(row)


def contact_directory():

    # NO Text Search -- ignore 'searched_text' 
    st.session_state["searched_text"] = ""

    df = st.session_state.get("filtered_df", apa_data)

    # Reformat df
    df = df.sort_values(by=['Last Name'])
    attorney_contacts = df[['Full Name','Work Email Address', 'Work Phone #']].copy()
    attorney_contacts['Work Phone #'] = attorney_contacts['Work Phone #'].apply(reformat_phone_num)
    attorney_contacts.rename(columns={
        'Full Name': 'Attorney Name',
        'Work Email Address': 'Email Address',
        'Work Phone #': 'Phone Number'
    })
    st.dataframe(attorney_contacts, hide_index=True, height=int(35.2 * (len(df) + 1)))


if st.session_state['view'] == 'Main Directory':
    main_directory()
elif st.session_state['view'] == 'Contact Directory':
    contact_directory()

