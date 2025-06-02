import streamlit as st
import cloudinary

config = cloudinary.config(
    cloud_name = st.secrets["cloudinary"]["CLOUD_NAME"], 
    api_key = st.secrets["cloudinary"]["API_KEY"],
    api_secret = st.secrets["cloudinary"]["API_SECRET"],
    secure = True
)

# import cloudinary.uploader
# import cloudinary.api

# Define load_photo() 
def load_photo(public_id):
    """Loads photo from Cloudinary with the provided public ID; returns img src URL that can be read into st.image()/st.markdown()"""
    return cloudinary.CloudinaryImage(public_id).build_url()