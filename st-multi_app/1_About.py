import streamlit as st
from PIL import Image
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


st.set_page_config(page_title="About",
page_icon=":wave:", 
layout="wide", 
initial_sidebar_state="expanded")


logo = Image.open('../images/logo_2.png')
st.image(logo)
st.title('About')