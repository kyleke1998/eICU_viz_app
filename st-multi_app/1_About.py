import streamlit as st
from PIL import Image



st.set_page_config(page_title="About",
page_icon=":wave:", 
layout="wide", 
initial_sidebar_state="expanded")

st.title('About')

logo = Image.open('../images/logo.jpg')
st.image(logo)
st.write("Introduction to the EICU Database Demo App")