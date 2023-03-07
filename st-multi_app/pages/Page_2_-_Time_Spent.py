import altair as alt
import pandas as pd
import streamlit as st
import numpy as np

PATH = "../data/patient.csv"

# Page Header
st.title("Efficiency of Healthcare Delivery")

@st.cache_data(persist=True)
def load_data():
    df = pd.read_csv(PATH)
    # remove all NA for ICU/hospital length of stay, region and ethnicity
    df = df.dropna(subset=["actualhospitallos","actualiculos","region","ethnicity"])
    return df

# load in data
df = load_data()

# wrangle data for chart 1

df_grouped = df.groupby(['region']).mean()
df_grouped.index.name = 'region'
df_grouped.reset_index(inplace=True)
df_grouped.rename(columns={'actualiculos': 'ICU', 'actualhospitallos': 'hospital'}, inplace=True)
df_grouped_long = pd.melt(df_grouped, id_vars=['region'], value_vars = ['ICU', 'hospital'], var_name= "Location", value_name = "Length of stay (days)")
df_grouped_long = round(df_grouped_long, 2)

#create chart 1

# add subheader to chart
st.subheader('1. Time in ICU and hospital by region')

chart = alt.Chart(df_grouped_long, height = 200, title = "Average length of stay by region").mark_bar().encode(
    x = alt.X('region:N', title = 'Region'),
    y = alt.Y('sum(Length of stay (days))', title = "Average length of stay in days"),
    color = 'Location',
    tooltip=['Location', 'Length of stay (days)'],
    ).properties(height=400, width=800)


st.altair_chart(chart)

# create selectbox to filter charts 2 and 3

regions = np.array(['Midwest', 'South', 'West', 'Northeast'])
region = st.selectbox('Region',options = regions, index=0)
subset = df.query("region == @region")

# wrangle data for chart 2

st.subheader('2. Time in ICU and hospital within a region')


df_grouped_byhospital = subset.groupby(['hospitalid', 'region']).mean()
df_grouped_byhospital.index.name = 'hospitalid'
df_grouped_byhospital.reset_index(inplace=True)
df_grouped_byhospital.rename(columns={'actualiculos': 'ICU', 'actualhospitallos': 'hospital'}, inplace=True)


df_perhospital_long = pd.melt(df_grouped_byhospital, id_vars=['hospitalid', 'region'], value_vars = ['ICU', 'hospital'], var_name = "Location", value_name = "Length of stay (days)")
df_perhospital_long = round(df_perhospital_long, 2)
nrows_each = len(df_perhospital_long[df_perhospital_long["Location"]=="ICU"])
no_hospital_1 = np.arange(1,nrows_each+1).tolist()
no_hospital_2 = np.arange(1,nrows_each+1).tolist()
total_no_hospital = no_hospital_1 + no_hospital_1
df_perhospital_long["hospital number"] = total_no_hospital

# create chart 2

chart_2 = alt.Chart(df_perhospital_long, height = 200, title = "Average length of stay within a region by hospital").mark_bar().encode(
    x= alt.X('hospital number:O', title = "Hospital"),
    y= alt.Y('sum(Length of stay (days))', title = "Average length of stay in days"),
    color = 'Location',
    tooltip=["Location", 'Length of stay (days)', 'region']
).properties(height = 400, width = 600)

# wrangle data for chart 3

df_grouped_byethnicity = subset.groupby(['ethnicity', 'region']).mean()
df_grouped_byethnicity.index.name = 'ethnicity'
df_grouped_byethnicity.reset_index(inplace=True)
df_grouped_byethnicity.rename(columns={'actualiculos': 'ICU', 'actualhospitallos': 'hospital'}, inplace=True)


df_perethnicity_long = pd.melt(df_grouped_byethnicity, id_vars=['ethnicity', 'region'], value_vars = ['ICU', 'hospital'], var_name = "Location", value_name = "Length of stay (days)")
df_perethnicity_long = round(df_perethnicity_long, 2)

# create chart 3

chart_3 = alt.Chart(df_perethnicity_long, height = 200, title = "Average length of stay within a region by ethnicity").mark_bar().encode(
    x=alt.X('ethnicity:N', title = "Ethnicity"),
    y=alt.Y('sum(Length of stay (days))', title = "Average length of stay in days"),
    color = 'Location',
    tooltip=["Location", "Length of stay (days)", 'region'],
).properties(height = 400, width = 600)

st.altair_chart(alt.vconcat(chart_2, chart_3))