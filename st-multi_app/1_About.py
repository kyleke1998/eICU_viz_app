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

st.markdown('''
    ---
    This is a Streamlit web application that aims to provide a user-friendly interface for exploring
     the demo eICU-CRD dataset, which consists of 2500 patient stays in the ICU between 2014-2015. 
     The web application is targted at regional hopital administrators who are responsible for 
     monitoring and improving the performance of healthcare systems within a certain region of the 
     US (e.g. North-East, South-West etc.). Our app will allow these individuals to visualize trends 
     in such things as demographics, patient flow and APACHE score prediction, which will be used to 
     guide policy-making and hospital management.
''')

st.markdown('''
    The visualizatons are divided into three pages:

    1. **Demographics and Diagnosis**: This page allows the user to explore the demographics and 
    diagnosis of patients between regions and between hospitals within each region. 

    2. **Time Spent**: This page allows the user to explore the patient flow between regions and 
    between hospitals within each region. We explored the time spent in the ICU and the hospital, 
    and also racial disparities in length of stays. 

    3. **Performance Monitoring**: This page allows the user to explore the performance of the 
    APACHE model in predicting hospital mortality and length of stay. We also explored disparities
    in prediction performance at different times of the day, and between gender and ethnic groups. 
''')

st.markdown('''
    ---
    **References:**
    ---

    1. Johnson, A., Pollard, T., Badawi, O., & Raffa, J. (2021). eICU Collaborative Research 
    Database Demo (version 2.0.1). PhysioNet. https://doi.org/10.13026/4mxk-na84.

    2. Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., ... & 
    Stanley, H. E. (2000). PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research 
    resource for complex physiologic signals. Circulation [Online]. 101 (23), pp. e215–e220. 


''')


st.markdown('''
    **Done by:**
    ---
    
    Kyle Ke, Qassi Gaba and Boshen Yan for BMI 706: Data Visualization for Biomedical 
    Applications at Harvard University.
''')