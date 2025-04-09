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

    # Clean age
    df = df[(df['Age'] >= 15) & (df['Age'] <= 100)]

    # Clean gender values
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

    # Standardize no_employees column
    df['no_employees'] = df['no_employees'].astype(str).str.strip()

    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Data")
countries = st.sidebar.multiselect("Select Country", sorted(df['Country'].unique()))
genders = st.sidebar.multiselect("Select Gender", df['Gender'].unique())
age_range = st.sidebar.slider("Select Age Range", 15, 100, (20, 40))

# Filter dataset
filtered_df = df[
    (df['Country'].isin(countries) if countries else True) &
    (df['Gender'].isin(genders) if genders else True) &
    (df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1])
]

# Display number of records
st.markdown(f"### Number of records: {filtered_df.shape[0]}")

# Chart: Treatment by Gender
st.subheader("Mental Health Treatment by Gender")
sns.set_style("whitegrid")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=filtered_df, x="Gender", hue="treatment", palette="Set2", ax=ax)
ax.set_xlabel("Gender")
ax.set_ylabel("Number of Respondents")
ax.set_title("Treatment Seeking by Gender")
st.pyplot(fig)
