import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Mental Health Dashboard", layout="wide")
st.title("Mental Health Dashboard")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("survey.csv")

    df = df[(df['Age'] >= 15) & (df['Age'] <= 100)]

    def clean_gender(g):
        g = str(g).strip().lower()
        male_terms = ['male', 'm', 'man', 'cis male', 'cis man', 'msle', 'malr', 'mail', 'maile', 'make', 'mal', 'male-ish']
        female_terms = ['female', 'f', 'woman', 'cis female', 'femake', 'femail', 'cis-female/femme', 'female (cis)', 'female ', 'female (trans)']
        trans_terms = ['trans', 'trans-female', 'trans woman']
        if any(term in g for term in male_terms):
            return 'Male'
        elif any(term in g for term in female_terms):
            return 'Female'
        elif any(term in g for term in trans_terms):
            return 'Trans'
        else:
            return 'Other'

    df['Gender'] = df['Gender'].apply(clean_gender)

    def clean_employees(value):
        value = str(value).strip().lower()
        if '1-5' in value:
            return '1-5'
        elif '6-25' in value:
            return '6-25'
        elif '26-100' in value:
            return '26-100'
        elif '100-500' in value:
            return '100-500'
        elif '500-1000' in value:
            return '500-1000'
        elif 'more than 1000' in value or '1000+' in value:
            return 'More than 1000'
        else:
            return 'Not specified'

    df['no_employees'] = df['no_employees'].apply(clean_employees)

    df['treatment'] = df['treatment'].astype(str).str.strip().str.capitalize()
    df['family_history'] = df['family_history'].astype(str).str.strip().str.capitalize()

    text_fields = ['self_employed', 'treatment', 'work_interfere', 'family_history', 'mental_health_interview']
    for field in text_fields:
        df[field] = df[field].fillna('Not specified').astype(str).str.strip().str.capitalize()

    df.dropna(subset=['Gender', 'treatment', 'family_history'], inplace=True)

    categorical_cols = ['Gender', 'self_employed', 'treatment', 'family_history',
                        'work_interfere', 'mental_health_interview', 'no_employees']
    for col in categorical_cols:
        df[col] = df[col].astype('category')

    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Data")
countries = st.sidebar.multiselect("Select Country", sorted(df['Country'].dropna().unique()))
genders = st.sidebar.multiselect("Select Gender", df['Gender'].cat.categories)
age_range = st.sidebar.slider("Select Age Range", 15, 100, (20, 40))

filtered_df = df[
    (df['Country'].isin(countries) if countries else True) &
    (df['Gender'].isin(genders) if genders else True) &
    (df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1])
]

# KPIs
st.markdown("### Key Performance Indicators")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Responses", len(filtered_df))
kpi2.metric("Treatment %", f"{(filtered_df['treatment'] == 'Yes').mean() * 100:.1f}%")
kpi3.metric("Family History %", f"{(filtered_df['family_history'] == 'Yes').mean() * 100:.1f}%")

# Tabs for sections
tabs = st.tabs(["Overview", "Charts", "Download"])

# Palettes
yes_no_palette = {key: color for key, color in zip(filtered_df['treatment'].unique(), ['green', 'red', 'gray'])}
self_employed_palette = {key: color for key, color in zip(filtered_df['self_employed'].unique(), ['green', 'red', 'gray', 'blue'])}

with tabs[0]:
    st.subheader("Treatment by Gender")
    fig1 = px.histogram(filtered_df, x="Gender", color="treatment", barmode='group')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Age Distribution")
    fig2 = px.histogram(filtered_df, x="Age", nbins=20, marginal="box")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Self-Employment Status")
    fig3 = px.pie(filtered_df, names="self_employed", title="Self-Employment Breakdown")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("How Mental Health Affects Work")
    fig4 = px.bar(filtered_df['work_interfere'].value_counts().reset_index(), x='index', y='work_interfere',
                 labels={'index': 'Interference Level', 'work_interfere': 'Count'}, color='index')
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Family History vs Treatment")
    family_treatment = filtered_df.groupby(['family_history', 'treatment']).size().reset_index(name='count')
    fig5 = px.sunburst(family_treatment, path=['family_history', 'treatment'], values='count')
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("Mental Health Benefits at Work")
    fig6 = px.bar(filtered_df['mental_health_interview'].value_counts().reset_index(), x='index', y='mental_health_interview',
                 labels={'index': 'Interview Status', 'mental_health_interview': 'Count'})
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Company Size Distribution")
    order = ['1-5', '6-25', '26-100', '100-500', '500-1000', 'More than 1000', 'Not specified']
    company_size = filtered_df['no_employees'].value_counts().reindex(order).reset_index()
    fig7 = px.bar(company_size, x='index', y='no_employees', labels={'index': 'Company Size', 'no_employees': 'Count'})
    st.plotly_chart(fig7, use_container_width=True)

with tabs[1]:
    st.subheader("All Charts Above")
    st.dataframe(filtered_df.head())

with tabs[2]:
    st.subheader("Download Filtered Dataset")
    st.download_button("Download CSV", filtered_df.to_csv(index=False), file_name="filtered_mental_health_data.csv")
