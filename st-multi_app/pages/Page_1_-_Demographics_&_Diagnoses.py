import altair as alt
import pandas as pd
import streamlit as st

PATH = "../data/patient.csv"


@st.cache_data
def load_data():
    data = pd.read_csv(PATH)
    data["bmi"] = data["admissionweight"] / (data["admissionheight"] / 100) ** 2
    data["bmi"] = data["bmi"].mask(data["bmi"] > 100)
    data["bmigroup"] = pd.cut(
        data["bmi"],
        bins=[0, 18.5, 25, 30, 35, 40, 100],
        labels=[
            "1-Underweight",
            "2-Normal",
            "3-Overweight",
            "4-Obese Class I",
            "5-Obese Class II",
            "6-Obese Class III",
        ],
    )
    return data


df = load_data()

# Part 1:
# ========
st.title("Demographics & Diagnoses")
st.subheader("1. Demographics & Diagnoses Between Regions")
demographic_map = {
    "Gender": "gender",
    "Age Group": "agegroup",
    "Ethnicity": "ethnicity",
    "BMI Group": "bmigroup",
}
# top: Dropdown selector for type of demographics
demographic = st.selectbox(
    label="Type of demographics",
    options=sorted(demographic_map.keys()),
    index=0,
)

demographic_df = df.value_counts(
    ["region", demographic_map[demographic], "primarydiagnosis"]
).reset_index()
demographic_df.columns = ["Region", demographic, "Diagnosis", "Count"]
demographic_df["Proportion"] = (
    demographic_df.groupby("Region")["Count"].apply(lambda x: x / x.sum()).round(4)
)

# middle: patient demographics with selector
selector1 = alt.selection_multi(fields=["Region", demographic])
chart1 = (
    alt.Chart(demographic_df, height=160)
    .mark_bar()
    .encode(
        x=alt.X("sum(Count)", title="Percentage", stack="normalize"),
        y=alt.Y("Region", sort=sorted(demographic_df["Region"].unique())),
        color=alt.condition(
            selector1,
            alt.Color(
                demographic,
                type="nominal",
                sort=sorted(demographic_df[demographic].unique()),
            ),
            alt.value("lightgray"),
        ),
        tooltip=[
            "Region",
            demographic,
            alt.Tooltip("sum(Count)", title="Count"),
            alt.Tooltip("sum(Proportion)", title="Proportion"),
        ],
    )
    .add_selection(selector1)
    .properties(width=400)
)
# bottom: diagnoses with linked transform filter
chart2 = (
    alt.Chart(demographic_df, height=160, title="Diagnosis Breakdown")
    .mark_bar()
    .encode(
        x=alt.X("sum(Count)", title="Percentage", stack="normalize"),
        y=alt.Y("Region", sort=sorted(demographic_df["Region"].unique())),
        color=alt.Color("Diagnosis:N"),
        tooltip=[
            "Region",
            "Diagnosis",
            alt.Tooltip("sum(Count)", title="Count"),
            alt.Tooltip("sum(Proportion)", title="Proportion"),
        ],
    )
    .transform_filter(selector1)
    .properties(width=400)
)
region_chart = chart1 & chart2
st.altair_chart(
    region_chart.resolve_scale(color="independent").configure_legend(labelLimit=200),
    use_container_width=True,
)


# Part 2:
# ========
st.subheader("2. Demographics & Diagnoses Between Hospitals")

region = st.radio("Region", ("Midwest", "Northeast", "South", "West"), horizontal=True)
subset = df[df["region"] == region]

# Bottom: graph of patient demographics/diagnoses between hospitals

regional_demographic_map = {
    "Gender": "gender",
    "Age Group": "agegroup",
    "Ethnicity": "ethnicity",
    "BMI Group": "bmigroup",
}

demographic1 = regional_demographic_map[
    st.selectbox(
        label="Type of categorical demographics",
        options=sorted(regional_demographic_map.keys()),
        index=3,
    )
]
selector2 = alt.selection_multi(fields=["hospitalid"])
chart3 = (
    alt.Chart(subset, height=200)
    .mark_bar(width=5)
    .encode(
        x=alt.X("hospitalid:N", title="Hospital ID"),
        y=alt.Y("count()"),
        color=alt.condition(
            selector2,
            alt.Color(demographic1, type="nominal"),
            alt.value("lightgray"),
        ),
        tooltip=[demographic1, "count()"],
    )
    .add_selection(selector2)
    .properties(height=400, width=600)
)
chart4 = (
    alt.Chart(subset, height=200, title="Count of diagnoses in hospitals")
    .mark_bar()
    .encode(
        y=alt.Y(
            "primarydiagnosis:N",
            title="Diagnosis",
            axis=alt.Axis(labelLimit=150),
            sort="-x",
        ),
        x=alt.X("count()"),
        tooltip=["primarydiagnosis", "count()"],
    )
    .transform_filter(selector2)
    .properties(height=400, width=600)
)

st.altair_chart((chart3 & chart4))


regional_demographic_map1 = {"Age": "age", "BMI": "bmi"}

demographic2 = regional_demographic_map1[
    st.selectbox(
        label="Type of numerical demographics",
        options=sorted(regional_demographic_map1.keys()),
        index=0,
    )
]

# Part 2.1: Boxplot of numerical demographics between hospitals 
# isolated out because selectors do not work with boxplot:
# https://github.com/altair-viz/altair/issues/2255
chart5 = (
    alt.Chart(subset)
    .mark_boxplot(size=400 / subset["hospitalid"].nunique())
    .encode(
        x=alt.X("hospitalid:N", title="Hospital ID"),
        y=alt.Y(
            demographic2,
            type="quantitative",
            scale=alt.Scale(domain=(0, subset[demographic2].max() + 10)),
        ),
        tooltip=alt.Tooltip([demographic2, "hospitalid"]),
    )
    .properties(height=400, width=600)
)
st.altair_chart(chart5)
