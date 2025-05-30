import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Tabs for visualization
tabs = st.tabs(["Overview", "Data Table & Correlation", "Download"])

with tabs[0]:
    st.subheader("Overview of Key Distributions")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Treatment by Gender")
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.countplot(data=filtered_df, x="Gender", hue="treatment", palette=['#84c084', '#e07b7b'], ax=ax)
        ax.set_xlabel("Gender")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    with col2:
        st.markdown("#### Age Distribution")
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.histplot(filtered_df['Age'], bins=20, kde=True, color="#91bcd3", ax=ax)
        ax.set_xlabel("Age")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Family History vs Treatment")
        fig, ax = plt.subplots(figsize=(4, 3))
        sns.countplot(data=filtered_df, x="family_history", hue="treatment", palette='Set2', ax=ax)
        ax.set_xlabel("Family History")
        ax.set_ylabel("Count")
        st.pyplot(fig)

    with col4:
        st.markdown("#### Company Size Distribution")
        fig, ax = plt.subplots(figsize=(4, 3))
        order = ['1-5', '6-25', '26-100', '100-500', '500-1000', 'More than 1000', 'Not specified']
        sns.countplot(data=filtered_df, x='no_employees', order=order, palette='Greens', ax=ax)
        ax.set_xlabel('Company Size')
        ax.set_ylabel('Count')
        plt.xticks(rotation=45)
        st.pyplot(fig)

with tabs[1]:
    st.subheader("Filtered Data Table")
    st.dataframe(filtered_df.head(50))

    st.subheader("Correlation Heatmap")

    # Create numeric versions of categorical variables for correlation
    numeric_df = filtered_df.copy()
    mapping = {'Yes': 1, 'No': 0, 'Not specified': None}
    numeric_df['treatment_num'] = numeric_df['treatment'].map(mapping)
    numeric_df['family_history_num'] = numeric_df['family_history'].map(mapping)

    # Select relevant columns for correlation
    corr_columns = ['Age', 'treatment_num', 'family_history_num']
    corr = numeric_df[corr_columns].corr()

    fig, ax = plt.subplots(figsize=(4, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, annot_kws={"size": 10})
    ax.set_title("Correlation Between Age, Treatment & Family History", fontsize=10)
    st.pyplot(fig)

with tabs[2]:
    st.subheader("Download Filtered Dataset")
    st.download_button("Download CSV", filtered_df.to_csv(index=False), file_name="filtered_mental_health_data.csv")
