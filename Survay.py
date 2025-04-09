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

    # Clean 'no_employees' column
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

    # Normalize specific fields (capitalize Yes/No responses)
    df['treatment'] = df['treatment'].astype(str).str.strip().str.capitalize()
    df['family_history'] = df['family_history'].astype(str).str.strip().str.capitalize()

    # Clean NaNs and whitespace in categorical fields
    text_fields = ['self_employed', 'treatment', 'work_interfere', 'family_history', 'mental_health_interview']
    for field in text_fields:
        df[field] = df[field].fillna('Not specified').astype(str).str.strip().str.capitalize()

    # Drop rows with missing critical values
    df.dropna(subset=['Gender', 'treatment', 'family_history'], inplace=True)

    # Convert to categorical
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

# Filter dataset
filtered_df = df[
    (df['Country'].isin(countries) if countries else True) &
    (df['Gender'].isin(genders) if genders else True) &
    (df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1])
]

# Display number of records
st.markdown(f"### Number of records: {filtered_df.shape[0]}")

# Palettes
yes_no_palette = {key: color for key, color in zip(filtered_df['treatment'].unique(), ['green', 'red', 'gray'])}
self_employed_palette = {key: color for key, color in zip(filtered_df['self_employed'].unique(), ['green', 'red', 'gray', 'blue'])}

# Chart 1: Treatment by Gender
st.subheader("Mental Health Treatment by Gender")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=filtered_df, x="Gender", hue="treatment", palette=yes_no_palette, ax=ax)
ax.set_title("Treatment Seeking by Gender")
st.pyplot(fig)

# Chart 2: Age Distribution
st.subheader("Age Distribution")
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(data=filtered_df, x="Age", kde=True, color="skyblue", ax=ax)
ax.set_title("Age Distribution of Respondents")
st.pyplot(fig)

# Chart 3: Self-Employment Status
st.subheader("Self-Employment Status")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=filtered_df, x="self_employed", palette=self_employed_palette, ax=ax)
ax.set_title("Self-Employment Status of Respondents")
st.pyplot(fig)

# Chart 4: How Mental Health Affects Work
st.subheader("How Mental Health Affects Work")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=filtered_df, x="work_interfere", palette="coolwarm", ax=ax)
ax.set_title("How Mental Health Affects Work Productivity")
st.pyplot(fig)

# Chart 5: Family History vs Treatment
st.subheader("Family History vs Treatment")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=filtered_df, x="family_history", hue="treatment", palette=yes_no_palette, ax=ax)
ax.set_title("Relationship Between Family History and Seeking Treatment")
st.pyplot(fig)

# Chart 6: Mental Health Benefits at Work
st.subheader("Mental Health Benefits at Work")
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=filtered_df, x="mental_health_interview", palette="crest", ax=ax)
ax.set_title("Does the Company Offer Mental Health Benefits?")
st.pyplot(fig)

# Chart 7: Company Size Distribution
st.subheader("Company Size Distribution")
order = ['1-5', '6-25', '26-100', '100-500', '500-1000', 'More than 1000', 'Not specified']
fig, ax = plt.subplots(figsize=(10, 6))
sns.countplot(data=filtered_df, x="no_employees", order=order, palette="viridis", ax=ax)
ax.set_title("Distribution of Respondents Based on Company Size")
st.pyplot(fig)

# Bonus Features
st.sidebar.markdown("---")
if st.sidebar.button("Download Filtered CSV"):
    st.download_button("Download CSV", filtered_df.to_csv(index=False), file_name="filtered_mental_health_data.csv")
