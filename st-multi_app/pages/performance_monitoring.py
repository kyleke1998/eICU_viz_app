import altair as alt
import pandas as pd
import streamlit as st
import datetime
from sklearn.metrics import accuracy_score, roc_curve, auc
from sklearn.metrics import recall_score, precision_score
import numpy as np
import matplotlib.pyplot as plt
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))
#PATH = "C:/Users/kylek/OneDrive - Harvard University/BMI706/project/eICU_viz_app/data/patient.csv"
PATH = "../../data/patient.csv"



@st.cache_data(persist=True)
def load_data():
    ## {{ CODE HERE }} ##
    df = pd.read_csv(PATH)

    # remove all NA for hospital mortality, ICU/hospital length of stay
    df = df.dropna(subset=["actualhospitalmortality", "predictedhospitalmortality","predictedhospitallos","actualhospitallos","predictediculos","actualiculos","region","ethnicity"])
    # turn hospital mortality into binary
    df["actualhospitalmortality"] = df["actualhospitalmortality"].apply(lambda x: 1 if x == 'EXPIRED' else 0)
    # drop all negative ones in actual hospital mortality
    df = df.drop(df[df["predictedhospitalmortality"] == -1].index)
    return df



@st.cache_data(persist=True)
def find_best_classification_cutoff(df):
    
# Generate predictions for different cutoff values and evaluate their performance
    fpr, tpr, thresholds = roc_curve(df['actualhospitalmortality'], df['predictedhospitalmortality'])
    

        
    # Compute AUC
    auc_score = auc(fpr, tpr)

    # Find optimal threshold that maximizes AUC
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]
    return optimal_threshold, auc_score


@st.cache_data(persist=True)
def group_accuracy(df):
    true_values = df['actualhospitalmortality']
    predicted_values = df['predictedhospitalmortality']
    recall = recall_score(true_values,predicted_values)
    precision = precision_score(true_values,predicted_values)
    results = pd.concat([pd.Series({'Accuracy': accuracy_score(true_values, predicted_values)}),pd.Series({"Recall": recall}),pd.Series({"Precision": precision})])
    return results


# load in data
df = load_data()

# get the best cutoff and auc_score
best_cutoff,auc = find_best_classification_cutoff(df)

# create a y_pred column based on the best cutoff
df["predictedhospitalmortality"] = df["predictedhospitalmortality"].apply(lambda x: 1 if x >= best_cutoff else 0)
# Create hospital residual column 

# Get residuals for ICU LOS and hospital LOS
df["hospitallos_residual"] = df["actualhospitallos"] - df["predictedhospitallos"]
df["iculos_residual"] = df["actualiculos"] - df["predictediculos"]

df['hospitaladmittime24'] = pd.to_datetime(df['hospitaladmittime24'])

# Page Header
st.title("Performance Monitoring")


# Select demographics to stratify by
demographic = st.radio('Demographics to Stratify by', ('gender', 'ethnicity'))


# select region
default_region = 'All'
regions = np.array(['Midwest', 'All', 'South', 'West', 'Northeast'])
region = st.selectbox('Regions',options = regions, index=1)


if region != default_region:
    subset = df.query("region == @region")
else:
    subset = df

metrics_all = subset.groupby(subset['hospitaladmittime24'].dt.hour).apply(group_accuracy).reset_index()
metrics_all = metrics_all.melt(id_vars=['hospitaladmittime24'], var_name="Metric", value_name="Rate")





st.subheader('1. Predicted Hospital Mortality Performance')


mortality_pred_by_hour = alt.Chart(metrics_all).mark_line().encode(
    x=alt.X("hospitaladmittime24", title="Hour of Admission",type="quantitative", axis=alt.Axis(tickCount=24)),
    y=alt.Y("Rate", title="Rate",type="quantitative"),
    color=alt.Color("Metric",type="nominal"),tooltip=["Metric","Rate"]).properties(title="Predicted Hospital Mortality Performance by Hour of Admission (Filtered by Regions Only)",width=800,height=400)

st.altair_chart(mortality_pred_by_hour)





metrics = subset.groupby([demographic]).apply(group_accuracy).reset_index()
metrics = metrics.melt(id_vars=[demographic], var_name="Metric", value_name="Rate")



chart = alt.Chart(metrics).mark_bar().encode(
    y=alt.Y("Rate", title="Rate",type="quantitative"),
    x=alt.X(demographic,title=demographic, type="nominal", sort="y"),
    column=alt.Column('Metric', title='Metric', type="nominal"),
    color=alt.Color(demographic,type="nominal"), tooltip=["Rate:Q"]).properties(
    title=f"Predicted Hospital Mortality Performance by {demographic}",width=200,height=400)



st.altair_chart(chart)

st.subheader('2.Predicted Hospital and ICU Length of Stay Performance')

jitter_1 =  alt.Chart().mark_circle(size=14).encode(
    x=alt.X(
        'jitter:Q',
        title=None,
        axis=alt.Axis(ticks=True, grid=False, labels=False),
        scale=alt.Scale(),
    ),
    y=alt.Y('hospitallos_residual',title='Hospital Length of Stay Residual', type="quantitative"),
    color=alt.Color(demographic,type="nominal"),tooltip = alt.Tooltip(["hospitallos_residual:Q","actualhospitallos:Q","predictedhospitallos:Q"])
  ).transform_calculate(
    # Generate Gaussian jitter with a Box-Muller transform
    jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
).properties(height=400, width=100)


jitter_median_1 = alt.layer(
    jitter_1,
    alt.Chart().mark_rule().encode(
        y='median(hospitallos_residual)',
        x=alt.X(),
        color=alt.Color(demographic,type="nominal"))
).properties(
    width=100
).facet(
    data=subset,
    column=alt.Column(
        demographic,type="nominal",
        header=alt.Header(
            titleOrient='bottom',
            labelOrient='bottom',
            labelPadding=0,
        )
    )
).properties(title=f"Hospital Length of Stay Residual by {demographic} (Predicted - Actual)")



jitter_2 =  alt.Chart().mark_circle(size=14).encode(
    x=alt.X(
        'jitter:Q',
        title=None,
        axis=alt.Axis(ticks=True, grid=False, labels=False),
        scale=alt.Scale(),
    ),
    y=alt.Y('iculos_residual',title='ICU Length of Stay Residual', type="quantitative"),
    color=alt.Color(demographic,type="nominal"),tooltip = alt.Tooltip(["iculos_residual:Q","actualiculos:Q","predictediculos:Q"])
  ).transform_calculate(
    # Generate Gaussian jitter with a Box-Muller transform
    jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
).properties(height=400, width=100)


jitter_median_2 = alt.layer(
    jitter_1,
    alt.Chart().mark_rule().encode(
        y='median(iculos_residual)',
        x=alt.X(),
        color=alt.Color(demographic,type="nominal")),
).properties(
    width=100
).facet(
    data=subset,
    column=alt.Column(
        demographic,type="nominal",
        header=alt.Header(
            titleOrient='bottom',
            labelOrient='bottom',
            labelPadding=0,
        ),
    )
).properties(title=f"ICU Length of Stay Residual by {demographic} (Predicted - Actual)")

if demographic == 'gender':
    st.altair_chart(alt.hconcat(jitter_median_1, jitter_median_2))
elif demographic == 'ethnicity':
    st.altair_chart(alt.vconcat(jitter_median_1, jitter_median_2))
