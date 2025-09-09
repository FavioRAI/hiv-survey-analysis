import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
from scipy.stats import chi2
import warnings
import io
import base64
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="HIV Service Disruption Survey Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        border-bottom: 3px solid #1f77b4;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .concern-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336 !important;
    }
    .concern-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800 !important;
    }
    .concern-low {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50 !important;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .research-question {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .statistical-summary {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #9c27b0;
        margin: 1rem 0;
    }
    .interpretation-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Indicator Sets Configuration
INDICATOR_SETS = {
    'set1': {
        'title': "HIV Service Disruptions and Most Affected Populations",
        'question': "What types of HIV services have been disrupted in the past 6 months, and which populations have been most affected by these disruptions?",
        'service_disruptions': [
            'Gender-Affirming Care', 'HIV Testing', 'HIV Treatment', 'Housing-related Support Services',
            'Linkage to HIV Care', 'Mental Health Care', 'Navigation or Case Management',
            'PrEP or PEP Access', 'Rapid START or Same-Day ART Initiation',
            'Routine HIV Clinical Monitoring and Care', 'Substance Use Disorder Services', 'Transportation Support'
        ],
        'populations_affected': [
            'Black/African American', 'Latinx/Hispanic', 'Transgender',
            'Homeless/Unstable Housing', 'Immigrants/Undocumented'
        ],
        'independents': [
            'Professional Role', 'Ryan White Clinic', 'Community Health Center',
            'Hospital-Based Clinic', 'Federal Government Funding', 'Medicaid Funding'
        ]
    },
    'set2': {
        'title': "Ancillary Services Access (Mental Health, Substance Use, Housing)",
        'question': "How accessible are ancillary services (mental health, substance use treatment, housing support) for people with HIV, and what barriers exist for key populations?",
        'outcomes': [
            'Mental Health Services Access', 'Substance Use Services Access',
            'Housing Instability Observations', 'Barriers for Transgender Individuals',
            'Decline in Care Among Undocumented Individuals'
        ],
        'independents': [
            'Professional Role', 'Community Health Center Setting',
            'Hospital-Based Setting', 'Years in HIV Practice'
        ]
    },
    'set3': {
        'title': "Key Populations and HIV System Strain",
        'question': "What specific barriers do key populations face in accessing HIV services, and is there evidence of increased loss to follow-up among vulnerable groups?",
        'outcomes': [
            'Transgender Barriers: HIV Testing', 'Transgender Barriers: PrEP/PEP Access',
            'Transgender Barriers: Gender-Affirming Care', 'Housing Instability',
            'Loss to Follow-Up: Transgender', 'Loss to Follow-Up: Migrants',
            'Loss to Follow-Up: Homeless'
        ],
        'independents': [
            'Professional Role', 'Serves Transgender Population',
            'Serves Immigrants/Undocumented', 'Medicaid Funding'
        ]
    },
    'set4': {
        'title': "Anticipated HIV Service Disruptions and Concern Levels",
        'question': "What level of HIV service disruptions do providers anticipate in the next 6-18 months, and how concerned are they about potential cuts to Medicaid and federal HIV programs?",
        'outcomes': [
            'Anticipated Disruptions (6-12 months)', 'Anticipated Disruptions (12-18 months)',
            'Concern About Medicaid Cuts', 'Concern About AETC Cuts'
        ],
        'independents': [
            'Professional Role', 'Ryan White Clinic', 'Community Health Center',
            'Medicaid Funding', 'Serves Key Populations'
        ]
    },
    'set5': {
        'title': "Reliance on and Trust in Federal HIV Guidance",
        'question': "How frequently do HIV providers use federal guidelines, and have they observed changes in access to or quality of federal HIV guidance and resources?",
        'outcomes': [
            'Frequency of Using Federal Guidelines', 'Guidelines Access Delays',
            'Guidelines Less Clear', 'Concern: AETC Training Resources',
            'Concern: CDC Information Resources'
        ],
        'independents': [
            'Professional Role', 'Ryan White Clinic', 'Years in HIV Practice',
            'Concern About Federal Cuts'
        ]
    }
}

@st.cache_data
def load_sample_data():
    """Create comprehensive sample data based on the cross-tabulation provided"""
    
    # Professional roles and their counts from the document
    role_data = {
        'Case Manager': 31,
        'Clinical Social Worker': 22,
        'Mental Health Provider': 19,
        'Nurse Practitioner (NP)': 99,
        'Other (Please Specify)': 76,
        'Peer Navigator/Linkage Coordinator': 10,
        'Pharmacist': 40,
        'Physician (MD/DO)': 160,
        'Physician Assistant/Associate (PA)': 15,
        'Registered Nurse (RN)': 54
    }
    
    # Service disruption data from the cross-tab table
    disruption_data = {
        'Case Manager': {
            'Gender-Affirming Care': 4, 'HIV Testing': 4, 'HIV Treatment': 3,
            'Housing-related Support Services': 11, 'Linkage to HIV Care': 6,
            'Mental Health Care': 5, 'Navigation or Case Management': 7,
            'PrEP or PEP Access': 4, 'Rapid START or Same-Day ART Initiation': 5,
            'Routine HIV Clinical Monitoring and Care': 4, 'Substance Use Disorder Services': 1,
            'Transportation Support': 7, 'No disruptions': 12
        },
        'Clinical Social Worker': {
            'Gender-Affirming Care': 9, 'HIV Testing': 7, 'HIV Treatment': 3,
            'Housing-related Support Services': 7, 'Linkage to HIV Care': 3,
            'Mental Health Care': 7, 'Navigation or Case Management': 4,
            'PrEP or PEP Access': 5, 'Rapid START or Same-Day ART Initiation': 1,
            'Routine HIV Clinical Monitoring and Care': 0, 'Substance Use Disorder Services': 4,
            'Transportation Support': 7, 'No disruptions': 4
        },
        'Mental Health Provider': {
            'Gender-Affirming Care': 6, 'HIV Testing': 2, 'HIV Treatment': 2,
            'Housing-related Support Services': 4, 'Linkage to HIV Care': 4,
            'Mental Health Care': 4, 'Navigation or Case Management': 2,
            'PrEP or PEP Access': 5, 'Rapid START or Same-Day ART Initiation': 1,
            'Routine HIV Clinical Monitoring and Care': 2, 'Substance Use Disorder Services': 1,
            'Transportation Support': 3, 'No disruptions': 6
        },
        'Nurse Practitioner (NP)': {
            'Gender-Affirming Care': 38, 'HIV Testing': 12, 'HIV Treatment': 15,
            'Housing-related Support Services': 22, 'Linkage to HIV Care': 18,
            'Mental Health Care': 19, 'Navigation or Case Management': 18,
            'PrEP or PEP Access': 28, 'Rapid START or Same-Day ART Initiation': 8,
            'Routine HIV Clinical Monitoring and Care': 12, 'Substance Use Disorder Services': 9,
            'Transportation Support': 16, 'No disruptions': 35
        },
        'Other (Please Specify)': {
            'Gender-Affirming Care': 19, 'HIV Testing': 19, 'HIV Treatment': 12,
            'Housing-related Support Services': 19, 'Linkage to HIV Care': 11,
            'Mental Health Care': 16, 'Navigation or Case Management': 10,
            'PrEP or PEP Access': 21, 'Rapid START or Same-Day ART Initiation': 4,
            'Routine HIV Clinical Monitoring and Care': 6, 'Substance Use Disorder Services': 8,
            'Transportation Support': 17, 'No disruptions': 23
        },
        'Peer Navigator/Linkage Coordinator': {
            'Gender-Affirming Care': 2, 'HIV Testing': 4, 'HIV Treatment': 3,
            'Housing-related Support Services': 5, 'Linkage to HIV Care': 5,
            'Mental Health Care': 3, 'Navigation or Case Management': 4,
            'PrEP or PEP Access': 5, 'Rapid START or Same-Day ART Initiation': 4,
            'Routine HIV Clinical Monitoring and Care': 4, 'Substance Use Disorder Services': 0,
            'Transportation Support': 3, 'No disruptions': 1
        },
        'Pharmacist': {
            'Gender-Affirming Care': 15, 'HIV Testing': 3, 'HIV Treatment': 11,
            'Housing-related Support Services': 9, 'Linkage to HIV Care': 7,
            'Mental Health Care': 6, 'Navigation or Case Management': 8,
            'PrEP or PEP Access': 17, 'Rapid START or Same-Day ART Initiation': 7,
            'Routine HIV Clinical Monitoring and Care': 5, 'Substance Use Disorder Services': 4,
            'Transportation Support': 6, 'No disruptions': 9
        },
        'Physician (MD/DO)': {
            'Gender-Affirming Care': 61, 'HIV Testing': 24, 'HIV Treatment': 28,
            'Housing-related Support Services': 42, 'Linkage to HIV Care': 30,
            'Mental Health Care': 45, 'Navigation or Case Management': 41,
            'PrEP or PEP Access': 37, 'Rapid START or Same-Day ART Initiation': 13,
            'Routine HIV Clinical Monitoring and Care': 20, 'Substance Use Disorder Services': 20,
            'Transportation Support': 25, 'No disruptions': 46
        },
        'Physician Assistant/Associate (PA)': {
            'Gender-Affirming Care': 4, 'HIV Testing': 1, 'HIV Treatment': 2,
            'Housing-related Support Services': 3, 'Linkage to HIV Care': 2,
            'Mental Health Care': 3, 'Navigation or Case Management': 4,
            'PrEP or PEP Access': 2, 'Rapid START or Same-Day ART Initiation': 2,
            'Routine HIV Clinical Monitoring and Care': 1, 'Substance Use Disorder Services': 1,
            'Transportation Support': 3, 'No disruptions': 5
        },
        'Registered Nurse (RN)': {
            'Gender-Affirming Care': 15, 'HIV Testing': 10, 'HIV Treatment': 3,
            'Housing-related Support Services': 16, 'Linkage to HIV Care': 11,
            'Mental Health Care': 14, 'Navigation or Case Management': 17,
            'PrEP or PEP Access': 8, 'Rapid START or Same-Day ART Initiation': 4,
            'Routine HIV Clinical Monitoring and Care': 5, 'Substance Use Disorder Services': 5,
            'Transportation Support': 10, 'No disruptions': 18
        }
    }
    
    # Create sample dataset
    sample_data = []
    response_id = 1
    
    for role, count in role_data.items():
        for i in range(count):
            record = {
                'ResponseID': f'R_{response_id}',
                'Progress': 100,  # Complete surveys only
                'Q2_Professional_Role': role,
                'Q3_Setting_Ryan_White': np.random.choice([0, 1], p=[0.6, 0.4]),
                'Q3_Setting_Community_Health': np.random.choice([0, 1], p=[0.5, 0.5]),
                'Q3_Setting_Hospital_Based': np.random.choice([0, 1], p=[0.7, 0.3]),
                'Q4_Funding_Federal': np.random.choice([0, 1], p=[0.4, 0.6]),
                'Q4_Funding_Medicaid': np.random.choice([0, 1], p=[0.3, 0.7]),
                'Q5_Years_HIV_Practice': np.random.choice(['0-2 years', '3-5 years', '6-10 years', '10+ years']),
                'Q6_Serve_Transgender': np.random.choice([0, 1], p=[0.6, 0.4]),
                'Q6_Serve_Homeless': np.random.choice([0, 1], p=[0.4, 0.6]),
                'Q6_Serve_Immigrants': np.random.choice([0, 1], p=[0.5, 0.5]),
            }
            
            # Add service disruptions based on the cross-tab data
            for service, disrupted_count in disruption_data[role].items():
                if service != 'No disruptions':
                    # Calculate probability based on actual data
                    prob_disrupted = disrupted_count / count
                    is_disrupted = np.random.choice([0, 1], p=[1-prob_disrupted, prob_disrupted])
                    record[f'Q9_{service}'] = is_disrupted
            
            # Add other outcome variables
            record['Q21_Mental_Health_Access'] = np.random.choice(['Not accessible', 'Somewhat accessible', 'Very accessible'])
            record['Q22_Substance_Use_Access'] = np.random.choice(['Limited', 'Moderate', 'Excellent'])
            record['Q23_Housing_Instability'] = np.random.choice(['Never', 'Rarely', 'Sometimes', 'Frequently'])
            record['Q11_Anticipate_6_12_months'] = np.random.choice(['None', 'Minor', 'Moderate', 'Significant'])
            record['Q12_Anticipate_12_18_months'] = np.random.choice(['None', 'Minor', 'Moderate', 'Significant'])
            record['Q13_Concern_Medicaid'] = np.random.choice(['Not concerned', 'Somewhat concerned', 'Very concerned'])
            record['Q15_Concern_AETC'] = np.random.choice(['Not concerned', 'Somewhat concerned', 'Very concerned'])
            record['Q18_Federal_Guidelines_Use'] = np.random.choice(['Never', 'Rarely', 'Sometimes', 'Often', 'Always'])
            
            sample_data.append(record)
            response_id += 1
    
    return pd.DataFrame(sample_data)

@st.cache_data
def load_data():
    """Load survey data from uploaded file or use sample data"""
    # For deployment, we'll use the sample data
    # In production, you would load from uploaded file
    return load_sample_data()

def filter_complete_surveys(df):
    """Filter for completed surveys only"""
    if 'Progress' in df.columns:
        complete_df = df[df['Progress'] == 100].copy()
        excluded_count = len(df) - len(complete_df)
        return complete_df, excluded_count, len(df)
    else:
        return df, 0, len(df)

def calculate_descriptive_stats(df, indicator_set):
    """Calculate descriptive statistics for outcome variables"""
    stats_results = []
    
    if indicator_set == 'set1':
        # Handle service disruptions
        service_cols = [col for col in df.columns if col.startswith('Q9_') and 'No disruptions' not in col]
        for col in service_cols:
            if col in df.columns:
                total_responses = df[col].notna().sum()
                positive_responses = df[col].sum()
                percentage = (positive_responses / total_responses * 100) if total_responses > 0 else 0
                
                service_name = col.replace('Q9_', '').replace('_', ' ')
                
                stats_results.append({
                    'variable': col,
                    'name': service_name,
                    'category': 'Service Disruptions',
                    'type': 'Binary',
                    'total': total_responses,
                    'positive': positive_responses,
                    'percentage': percentage,
                    'concern_level': 'high' if percentage > 40 else 'medium' if percentage > 25 else 'low'
                })
    
    else:
        # Handle other indicator sets
        outcome_vars = [col for col in df.columns if any(prefix in col for prefix in ['Q21', 'Q22', 'Q23', 'Q11', 'Q12', 'Q13', 'Q15', 'Q18'])]
        for var in outcome_vars:
            if var in df.columns:
                total_responses = df[var].notna().sum()
                
                if df[var].dtype in ['int64', 'float64'] and df[var].nunique() <= 2:
                    # Binary variable
                    positive_responses = df[var].sum()
                    percentage = (positive_responses / total_responses * 100) if total_responses > 0 else 0
                    
                    stats_results.append({
                        'variable': var,
                        'name': var.replace('_', ' '),
                        'category': 'Outcome',
                        'type': 'Binary',
                        'total': total_responses,
                        'positive': positive_responses,
                        'percentage': percentage,
                        'concern_level': 'high' if percentage > 40 else 'medium' if percentage > 25 else 'low'
                    })
                else:
                    # Categorical variable
                    value_counts = df[var].value_counts()
                    concerning_responses = value_counts.get('Very concerned', 0) + value_counts.get('Significant', 0) + value_counts.get('Frequently', 0)
                    percentage = (concerning_responses / total_responses * 100) if total_responses > 0 else 0
                    
                    stats_results.append({
                        'variable': var,
                        'name': var.replace('_', ' '),
                        'category': 'Outcome',
                        'type': 'Categorical',
                        'total': total_responses,
                        'categories': value_counts.to_dict(),
                        'percentage': percentage,
                        'concern_level': 'high' if percentage > 40 else 'medium' if percentage > 25 else 'low'
                    })
    
    return sorted(stats_results, key=lambda x: x.get('percentage', 0), reverse=True)

def create_cross_tabulation(df, outcome_var, independent_var):
    """Create cross-tabulation with statistical tests"""
    if outcome_var not in df.columns or independent_var not in df.columns:
        return None
    
    # Filter out missing values
    clean_df = df[[outcome_var, independent_var]].dropna()
    
    if len(clean_df) == 0:
        return None
    
    # Create cross-tabulation
    crosstab = pd.crosstab(clean_df[independent_var], clean_df[outcome_var], margins=True)
    
    # Calculate percentages
    crosstab_pct = pd.crosstab(clean_df[independent_var], clean_df[outcome_var], 
                               normalize='index') * 100
    
    # Statistical tests
    chi2_stat = None
    p_value = None
    cramers_v = None
    
    try:
        # Remove margins for statistical test
        test_crosstab = crosstab.iloc[:-1, :-1]
        if test_crosstab.shape[0] > 1 and test_crosstab.shape[1] > 1:
            chi2_stat, p_value, dof, expected = chi2_contingency(test_crosstab)
            
            # Calculate Cramér's V
            n = test_crosstab.sum().sum()
            cramers_v = np.sqrt(chi2_stat / (n * (min(test_crosstab.shape) - 1)))
    except:
        pass
    
    return {
        'crosstab': crosstab,
        'percentages': crosstab_pct,
        'chi2_stat': chi2_stat,
        'p_value': p_value,
        'cramers_v': cramers_v,
        'sample_size': len(clean_df)
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 HIV Service Disruption Survey Analysis</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading survey data..."):
        df = load_data()
        complete_df, excluded_count, total_surveys = filter_complete_surveys(df)
    
    # Sidebar
    st.sidebar.markdown('<p class="sidebar-header">📊 Analysis Options</p>', unsafe_allow_html=True)
    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type:",
        ["🏠 Overview", "🎯 Indicator Set Analysis", "📊 Cross-Tabulation", "🔬 Custom Analysis", "📋 Data Explorer"]
    )
    
    # File upload option
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Upload Your Data")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Excel file (optional)",
        type=['xlsx', 'xls'],
        help="Upload your survey data to replace sample data"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            complete_df, excluded_count, total_surveys = filter_complete_surveys(df)
            st.sidebar.success(f"✅ Loaded {len(complete_df)} records from uploaded file")
        except Exception as e:
            st.sidebar.error(f"Error loading file: {str(e)}")
    else:
        st.sidebar.info("Using sample data based on your cross-tabulation table")
    
    # Main content area
    if analysis_type == "🏠 Overview":
        show_overview(complete_df, excluded_count, total_surveys)
    
    elif analysis_type == "🎯 Indicator Set Analysis":
        show_indicator_analysis(complete_df)
    
    elif analysis_type == "📊 Cross-Tabulation":
        show_cross_tabulation(complete_df)
    
    elif analysis_type == "🔬 Custom Analysis":
        show_custom_analysis(complete_df)
    
    elif analysis_type == "📋 Data Explorer":
        show_data_explorer(complete_df)

def show_overview(df, excluded_count, total_surveys):
    """Display overview dashboard"""
    st.markdown("## 📈 Survey Overview Dashboard")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="✅ Completed Surveys",
            value=len(df),
            help="Surveys with 100% completion rate"
        )
    
    with col2:
        st.metric(
            label="❌ Excluded Surveys",
            value=excluded_count,
            help="Incomplete survey responses"
        )
    
    with col3:
        st.metric(
            label="📋 Total Submitted",
            value=total_surveys,
            help="All survey attempts"
        )
    
    with col4:
        completion_rate = (len(df) / total_surveys * 100) if total_surveys > 0 else 0
        st.metric(
            label="📊 Completion Rate",
            value=f"{completion_rate:.1f}%",
            help="Quality threshold achievement"
        )
    
    # Survey quality alert
    if excluded_count > 0:
        st.markdown(f"""
        <div class="warning-box">
            ⚠️ <strong>Data Quality Note:</strong> {excluded_count} incomplete surveys excluded from analysis to ensure data quality and statistical validity.
        </div>
        """, unsafe_allow_html=True)
    
    # Quick insights
    st.markdown("## 🔍 Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Professional role distribution
        if 'Q2_Professional_Role' in df.columns:
            role_counts = df['Q2_Professional_Role'].value_counts()
            fig = px.pie(
                values=role_counts.values, 
                names=role_counts.index,
                title="Distribution by Professional Role"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top service disruptions
        disruption_cols = [col for col in df.columns if col.startswith('Q9_') and 'No disruptions' not in col]
        if disruption_cols:
            disruption_rates = []
            for col in disruption_cols:
                rate = df[col].mean() * 100
                service_name = col.replace('Q9_', '').replace('_', ' ')
                disruption_rates.append({'Service': service_name, 'Disruption_Rate': rate})
            
            disruption_df = pd.DataFrame(disruption_rates).sort_values('Disruption_Rate', ascending=True)
            
            fig = px.bar(
                disruption_df.tail(8), 
                x='Disruption_Rate', 
                y='Service',
                orientation='h',
                title="Top Service Disruptions (%)",
                color='Disruption_Rate',
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Indicator sets overview
    st.markdown("## 🎯 Indicator Sets Overview")
    
    for set_id, indicator in INDICATOR_SETS.items():
        with st.expander(f"**Indicator Set {set_id[-1]}: {indicator['title']}**", expanded=False):
            st.markdown(f"""
            <div class="research-question">
                <strong>🔬 Research Question:</strong><br>
                {indicator['question']}
            </div>
            """, unsafe_allow_html=True)
            
            # Show variable counts
            if set_id == 'set1':
                outcome_count = len(indicator.get('service_disruptions', []))
                pop_count = len(indicator.get('populations_affected', []))
                st.markdown(f"📊 **Service Disruptions:** {outcome_count} | **Populations:** {pop_count}")
            else:
                outcome_count = len(indicator.get('outcomes', []))
                st.markdown(f"📊 **Outcome Variables:** {outcome_count}")
            
            independent_count = len(indicator.get('independents', []))
            st.markdown(f"🔍 **Independent Variables:** {independent_count}")
            
            # Quick preview button
            if st.button(f"Analyze Set {set_id[-1]}", key=f"analyze_{set_id}"):
                st.session_state['analysis_type'] = '🎯 Indicator Set Analysis'
                st.session_state['selected_indicator'] = set_id
                st.experimental_rerun()

def show_indicator_analysis(df):
    """Display indicator set analysis"""
    st.markdown("## 🎯 Indicator Set Analysis")
    
    # Select indicator set
    selected_set = st.selectbox(
        "Select Indicator Set:",
        options=list(INDICATOR_SETS.keys()),
        format_func=lambda x: f"Set {x[-1]}: {INDICATOR_SETS[x]['title']}"
    )
    
    indicator = INDICATOR_SETS[selected_set]
    
    # Display research question
    st.markdown(f"""
    <div class="research-question">
        <strong>🔬 Research Question:</strong><br>
        {indicator['question']}
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate descriptive statistics
    stats_results = calculate_descriptive_stats(df, selected_set)
    
    if stats_results:
        st.markdown("## 📊 Descriptive Analysis")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Summary Results", "📈 Visualizations", "📄 Detailed Report"])
        
        with tab1:
            # Display results with enhanced styling
            for idx, result in enumerate(stats_results):
                concern_class = f"concern-{result['concern_level']}"
                
                # Determine icon based on concern level
                concern_icon = "🔴" if result['concern_level'] == 'high' else "🟡" if result['concern_level'] == 'medium' else "🟢"
                
                # Create columns for better layout
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card {concern_class}">
                        <h4>{concern_icon} {result['name']}</h4>
                        <p><strong>Category:</strong> {result['category']} | <strong>Type:</strong> {result['type']}</p>
                        <p><strong>Rank:</strong> #{idx + 1} by prevalence</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if result['type'] == 'Binary':
                        st.metric("Affected", f"{result['positive']}")
                    else:
                        st.metric("Responses", f"{result['total']}")
                
                with col3:
                    st.metric("Total", f"{result['total']}")
                
                with col4:
                    if result['type'] == 'Binary':
                        st.metric("Rate", f"{result['percentage']:.1f}%")
                    else:
                        st.metric("Concern", f"{result['percentage']:.1f}%")
                
                # Show categories for categorical variables
                if result['type'] == 'Categorical' and 'categories' in result:
                    with st.expander(f"View category breakdown for {result['name']}"):
                        cat_df = pd.DataFrame(list(result['categories'].items()), columns=['Category', 'Count'])
                        cat_df['Percentage'] = (cat_df['Count'] / cat_df['Count'].sum() * 100).round(1)
                        st.dataframe(cat_df, use_container_width=True)
        
        with tab2:
            # Create visualizations
            if any(r['type'] == 'Binary' for r in stats_results):
                binary_results = [r for r in stats_results if r['type'] == 'Binary']
                binary_df = pd.DataFrame(binary_results)
                
                # Bar chart
                fig = px.bar(
                    binary_df.sort_values('percentage'),
                    x='percentage',
                    y='name',
                    orientation='h',
                    title=f"Service Disruption Rates - {indicator['title']}",
                    labels={'percentage': 'Percentage Affected (%)', 'name': 'Service/Outcome'},
                    color='concern_level',
                    color_discrete_map={'low': '#4caf50', 'medium': '#ff9800', 'high': '#f44336'}
                )
                fig.update_layout(height=max(400, len(binary_df) * 30))
                st.plotly_chart(fig, use_container_width=True)
                
                # Heatmap for concern levels
                concern_matrix = binary_df.pivot_table(
                    index='category', 
                    columns='concern_level', 
                    values='percentage', 
                    aggfunc='mean'
                ).fillna(0)
                
                if not concern_matrix.empty:
                    fig_heatmap = px.imshow(
                        concern_matrix,
                        title="Concern Level Distribution by Category",
                        labels=dict(color="Average Percentage"),
                        aspect="auto"
                    )
                    st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with tab3:
            # Detailed report
            st.markdown("### 📄 Comprehensive Analysis Report")
            
            # Summary statistics
            total_variables = len(stats_results)
            high_concern = len([r for r in stats_results if r['concern_level'] == 'high'])
            medium_concern = len([r for r in stats_results if r['concern_level'] == 'medium'])
            
            st.markdown(f"""
            <div class="statistical-summary">
                <h4>📊 Summary Statistics</h4>
                <ul>
                    <li><strong>Total Variables Analyzed:</strong> {total_variables}</li>
                    <li><strong>High Concern Areas:</strong> {high_concern} ({high_concern/total_variables*100:.1f}%)</li>
                    <li><strong>Medium Concern Areas:</strong> {medium_concern} ({medium_concern/total_variables*100:.1f}%)</li>
                    <li><strong>Sample Size:</strong> {len(df)} completed surveys</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Top findings
            if high_concern > 0:
                st.markdown("#### 🚨 High Priority Findings")
                high_concern_items = [r for r in stats_results if r['concern_level'] == 'high'][:3]
                for item in high_concern_items:
                    st.markdown(f"- **{item['name']}**: {item.get('percentage', 0):.1f}% affected")
            
            # Recommendations
            st.markdown(f"""
            <div class="interpretation-box">
                <h4>💡 Key Insights & Recommendations</h4>
                <p>Based on the analysis of {indicator['title'].lower()}, the following patterns emerge:</p>
                <ul>
                    <li><strong>Priority Areas:</strong> Focus immediate attention on the {high_concern} high-concern areas identified.</li>
                    <li><strong>Monitoring:</strong> Continue monitoring the {medium_concern} medium-concern areas for potential escalation.</li>
                    <li><strong>System Impact:</strong> Consider cross-system effects when addressing individual service disruptions.</li>
                    <li><strong>Further Analysis:</strong> Conduct cross-tabulation analysis to identify vulnerable populations and settings.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

def show_cross_tabulation(df):
    """Display cross-tabulation analysis"""
    st.markdown("## 📊 Cross-Tabulation Analysis")
    
    st.markdown("""
    <div class="research-question">
        <strong>🎯 Purpose:</strong> Examine relationships between outcome variables and independent factors to identify patterns, 
        vulnerable populations, and settings most affected by service disruptions.
    </div>
    """, unsafe_allow_html=True)
    
    # Variable selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Select Outcome Variable")
        outcome_categories = {
            "Service Disruptions": [col for col in df.columns if col.startswith('Q9_') and 'No disruptions' not in col],
            "Access & Barriers": [col for col in df.columns if col.startswith(('Q21', 'Q22', 'Q23'))],
            "Future Concerns": [col for col in df.columns if col.startswith(('Q11', 'Q12', 'Q13', 'Q15'))],
            "Federal Guidance": [col for col in df.columns if col.startswith('Q18')]
        }
        
        outcome_category = st.selectbox("Select Category:", list(outcome_categories.keys()))
        available_outcomes = outcome_categories[outcome_category]
        
        if available_outcomes:
            outcome_var = st.selectbox(
                "Select Outcome Variable:", 
                available_outcomes,
                format_func=lambda x: x.replace('Q9_', '').replace('_', ' ').title()
            )
        else:
            outcome_var = None
            st.warning("No variables available in this category")
    
    with col2:
        st.markdown("### 🔍 Select Independent Variable")
        independent_categories = {
            "Professional Characteristics": ['Q2_Professional_Role', 'Q5_Years_HIV_Practice'],
            "Clinical Settings": [col for col in df.columns if 'Setting' in col],
            "Funding Sources": [col for col in df.columns if 'Funding' in col],
            "Populations Served": [col for col in df.columns if 'Serve' in col]
        }
        
        independent_category = st.selectbox("Select Category:", list(independent_categories.keys()))
        available_independents = independent_categories[independent_category]
        
        if available_independents:
            independent_var = st.selectbox(
                "Select Independent Variable:", 
                available_independents,
                format_func=lambda x: x.replace('Q2_', '').replace('Q5_', '').replace('_', ' ').title()
            )
        else:
            independent_var = None
            st.warning("No variables available in this category")
    
    # Generate cross-tabulation
    if st.button("🔬 Generate Cross-Tabulation Analysis", type="primary"):
        if outcome_var and independent_var:
            with st.spinner("Performing statistical analysis..."):
                result = create_cross_tabulation(df, outcome_var, independent_var)
                
                if result:
                    # Display statistical summary
                    st.markdown("## 📈 Statistical Analysis Results")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Sample Size", result['sample_size'])
                    
                    with col2:
                        if result['chi2_stat']:
                            st.metric("Chi-Square", f"{result['chi2_stat']:.3f}")
                        else:
                            st.metric("Chi-Square", "N/A")
                    
                    with col3:
                        if result['p_value'] is not None:
                            significance = "Significant" if result['p_value'] < 0.05 else "Not Significant"
                            color = "green" if result['p_value'] < 0.05 else "red"
                            st.metric("P-Value", f"{result['p_value']:.3f}")
                            st.markdown(f"<span style='color:{color};font-weight:bold'>{significance}</span>", unsafe_allow_html=True)
                        else:
                            st.metric("P-Value", "N/A")
                    
                    with col4:
                        if result['cramers_v']:
                            effect_size = "Strong" if result['cramers_v'] > 0.3 else "Medium" if result['cramers_v'] > 0.15 else "Weak"
                            st.metric("Cramér's V", f"{result['cramers_v']:.3f}")
                            st.markdown(f"**{effect_size} Effect**")
                        else:
                            st.metric("Cramér's V", "N/A")
                    
                    # Statistical interpretation
                    if result['p_value'] is not None:
                        if result['p_value'] < 0.05:
                            st.markdown(f"""
                            <div class="interpretation-box">
                                <h4>✅ Significant Association Found</h4>
                                <p>There is a statistically significant relationship between <strong>{independent_var.replace('_', ' ')}</strong> 
                                and <strong>{outcome_var.replace('_', ' ')}</strong> (p < 0.05).</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h4>ℹ️ No Significant Association</h4>
                                <p>No statistically significant relationship was detected between these variables (p ≥ 0.05).</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Display cross-tabulation tables
                    st.markdown("## 📋 Cross-Tabulation Tables")
                    
                    tab1, tab2, tab3 = st.tabs(["📊 Frequency Counts", "📈 Row Percentages", "🎨 Visualization"])
                    
                    with tab1:
                        st.markdown("### Frequency Counts")
                        st.dataframe(result['crosstab'], use_container_width=True)
                    
                    with tab2:
                        st.markdown("### Row Percentages")
                        # Style the percentage table
                        styled_pct = result['percentages'].style.format("{:.1f}%").background_gradient(cmap='Reds', subset=result['percentages'].columns[:-1])
                        st.dataframe(styled_pct, use_container_width=True)
                        
                        # Highlight concerning values
                        concerning_cells = []
                        for idx, row in result['percentages'].iterrows():
                            if idx != 'All':  # Skip margin row
                                for col in result['percentages'].columns:
                                    if col != 'All' and row[col] > 50:  # Threshold for concern
                                        concerning_cells.append(f"{idx} × {col}: {row[col]:.1f}%")
                        
                        if concerning_cells:
                            st.markdown("#### ⚠️ High-Risk Combinations (>50%)")
                            for cell in concerning_cells[:5]:  # Show top 5
                                st.markdown(f"- **{cell}**")
                    
                    with tab3:
                        # Create visualization
                        if result['crosstab'].shape[0] <= 12 and result['crosstab'].shape[1] <= 12:
                            # Remove margins for visualization
                            viz_data = result['percentages'].iloc[:-1, :-1]
                            
                            if not viz_data.empty:
                                fig = px.imshow(
                                    viz_data,
                                    title=f"Cross-Tabulation Heatmap",
                                    labels=dict(color="Percentage", x=outcome_var.replace('_', ' '), y=independent_var.replace('_', ' ')),
                                    aspect="auto",
                                    color_continuous_scale="Reds"
                                )
                                fig.update_layout(height=max(400, viz_data.shape[0] * 40))
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Table too large for heatmap visualization. Please refer to the tables above.")
                    
                    # Clinical interpretation and recommendations
                    st.markdown("## 💡 Clinical Interpretation & Recommendations")
                    
                    if result['p_value'] and result['p_value'] < 0.05:
                        if result['cramers_v'] and result['cramers_v'] > 0.3:
                            interpretation = "strong practical significance"
                        elif result['cramers_v'] and result['cramers_v'] > 0.15:
                            interpretation = "moderate practical significance"
                        else:
                            interpretation = "limited practical significance despite statistical significance"
                        
                        st.markdown(f"""
                        <div class="interpretation-box">
                            <h4>🔬 Clinical Significance</h4>
                            <p>The relationship between <strong>{independent_var.replace('_', ' ')}</strong> and 
                            <strong>{outcome_var.replace('_', ' ')}</strong> shows <em>{interpretation}</em>.</p>
                            
                            <h5>📋 Recommended Actions:</h5>
                            <ul>
                                <li><strong>Targeted Interventions:</strong> Focus resources on the highest-risk combinations identified</li>
                                <li><strong>Monitoring:</strong> Implement regular monitoring for vulnerable groups</li>
                                <li><strong>Resource Allocation:</strong> Consider differential resource allocation based on risk profiles</li>
                                <li><strong>Further Research:</strong> Investigate underlying causes of observed associations</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Export functionality
                    st.markdown("## 📥 Export Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Create downloadable CSV
                        csv_data = result['crosstab'].to_csv()
                        st.download_button(
                            label="📊 Download Frequency Table (CSV)",
                            data=csv_data,
                            file_name=f"crosstab_{outcome_var}_{independent_var}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Create downloadable percentage table
                        pct_csv = result['percentages'].to_csv()
                        st.download_button(
                            label="📈 Download Percentage Table (CSV)",
                            data=pct_csv,
                            file_name=f"crosstab_pct_{outcome_var}_{independent_var}.csv",
                            mime="text/csv"
                        )
                
                else:
                    st.error("❌ Unable to generate cross-tabulation. Please check your variable selections and ensure sufficient data is available.")
        else:
            st.warning("⚠️ Please select both outcome and independent variables to proceed with analysis.")

def show_custom_analysis(df):
    """Display custom analysis options"""
    st.markdown("## 🔬 Custom Analysis")
    
    st.markdown("""
    <div class="research-question">
        <strong>🎯 Purpose:</strong> Perform customized analysis with flexible filtering, comparison, and visualization options
        tailored to your specific research questions.
    </div>
    """, unsafe_allow_html=True)
    
    # Custom filters section
    st.markdown("### 🔧 Apply Custom Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Q2_Professional_Role' in df.columns:
            all_roles = df['Q2_Professional_Role'].unique()
            selected_roles = st.multiselect(
                "Filter by Professional Role:",
                options=all_roles,
                default=all_roles,
                help="Select specific professional roles to include in analysis"
            )
        else:
            selected_roles = None
    
    with col2:
        if 'Q5_Years_HIV_Practice' in df.columns:
            all_experience = df['Q5_Years_HIV_Practice'].unique()
            selected_experience = st.multiselect(
                "Filter by Experience Level:",
                options=all_experience,
                default=all_experience,
                help="Filter by years of HIV practice experience"
            )
        else:
            selected_experience = None
    
    with col3:
        # Setting filters
        setting_cols = [col for col in df.columns if 'Setting' in col]
        if setting_cols:
            selected_setting = st.selectbox(
                "Filter by Clinical Setting:",
                options=['All Settings'] + setting_cols,
                help="Focus analysis on specific clinical settings"
            )
        else:
            selected_setting = 'All Settings'
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_roles:
        filtered_df = filtered_df[filtered_df['Q2_Professional_Role'].isin(selected_roles)]
    
    if selected_experience:
        filtered_df = filtered_df[filtered_df['Q5_Years_HIV_Practice'].isin(selected_experience)]
    
    if selected_setting != 'All Settings' and selected_setting in df.columns:
        filtered_df = filtered_df[filtered_df[selected_setting] == 1]
    
    # Display filter results
    filter_reduction = len(df) - len(filtered_df)
    st.markdown(f"""
    <div class="metric-card">
        <strong>📊 Filtered Dataset:</strong> {len(filtered_df):,} records 
        ({filter_reduction:,} records filtered out)
    </div>
    """, unsafe_allow_html=True)
    
    if len(filtered_df) == 0:
        st.error("❌ No records match the selected filters. Please adjust your filter criteria.")
        return
    
    # Analysis options
    st.markdown("### 📊 Select Analysis Type")
    
    analysis_option = st.selectbox(
        "Choose Analysis:",
        [
            "Distribution Analysis",
            "Comparative Analysis", 
            "Correlation Matrix",
            "Trend Analysis",
            "Risk Assessment"
        ]
    )
    
    # Execute selected analysis
    if analysis_option == "Distribution Analysis":
        st.markdown("#### 📈 Distribution Analysis")
        
        selected_var = st.selectbox(
            "Select Variable to Analyze:", 
            [col for col in filtered_df.columns if not col.startswith('ResponseID')]
        )
        
        if selected_var:
            col1, col2 = st.columns(2)
            
            with col1:
                if filtered_df[selected_var].dtype in ['object', 'category']:
                    # Categorical variable
                    value_counts = filtered_df[selected_var].value_counts()
                    fig = px.pie(
                        values=value_counts.values, 
                        names=value_counts.index, 
                        title=f"Distribution of {selected_var.replace('_', ' ')}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Numerical variable
                    fig = px.histogram(
                        filtered_df, 
                        x=selected_var, 
                        title=f"Distribution of {selected_var.replace('_', ' ')}",
                        nbins=20
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Summary statistics
                if filtered_df[selected_var].dtype in ['object', 'category']:
                    st.markdown("**Summary Statistics:**")
                    value_counts = filtered_df[selected_var].value_counts()
                    for val, count in value_counts.items():
                        percentage = (count / len(filtered_df)) * 100
                        st.metric(str(val), f"{count} ({percentage:.1f}%)")
                else:
                    st.markdown("**Summary Statistics:**")
                    st.metric("Mean", f"{filtered_df[selected_var].mean():.2f}")
                    st.metric("Median", f"{filtered_df[selected_var].median():.2f}")
                    st.metric("Std Dev", f"{filtered_df[selected_var].std():.2f}")
    
    elif analysis_option == "Comparative Analysis":
        st.markdown("#### 📊 Comparative Analysis")
        
        # Compare disruption rates across groups
        if 'Q2_Professional_Role' in filtered_df.columns:
            disruption_cols = [col for col in filtered_df.columns if col.startswith('Q9_') and 'No disruptions' not in col]
            
            if disruption_cols:
                selected_disruptions = st.multiselect(
                    "Select Service Disruptions to Compare:",
                    disruption_cols,
                    default=disruption_cols[:5],
                    format_func=lambda x: x.replace('Q9_', '').replace('_', ' ').title()
                )
                
                if selected_disruptions:
                    # Calculate disruption rates by role
                    comparison_data = []
                    
                    for role in filtered_df['Q2_Professional_Role'].unique():
                        role_data = filtered_df[filtered_df['Q2_Professional_Role'] == role]
                        for col in selected_disruptions:
                            if col in role_data.columns:
                                rate = role_data[col].mean() * 100
                                comparison_data.append({
                                    'Professional Role': role,
                                    'Service': col.replace('Q9_', '').replace('_', ' ').title(),
                                    'Disruption Rate (%)': rate,
                                    'Sample Size': len(role_data)
                                })
                    
                    if comparison_data:
                        comparison_df = pd.DataFrame(comparison_data)
                        
                        # Create grouped bar chart
                        fig = px.bar(
                            comparison_df, 
                            x='Professional Role', 
                            y='Disruption Rate (%)', 
                            color='Service',
                            title="Service Disruption Rates by Professional Role",
                            barmode='group'
                        )
                        fig.update_xaxes(tickangle=45)
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show data table
                        st.markdown("**Detailed Comparison Table:**")
                        pivot_table = comparison_df.pivot_table(
                            index='Professional Role', 
                            columns='Service', 
                            values='Disruption Rate (%)',
                            aggfunc='mean'
                        ).round(1)
                        st.dataframe(pivot_table, use_container_width=True)
    
    elif analysis_option == "Correlation Matrix":
        st.markdown("#### 🔗 Correlation Matrix")
        
        # Select numerical variables for correlation
        numerical_cols = [col for col in filtered_df.columns if 
                         filtered_df[col].dtype in ['int64', 'float64'] and 
                         col not in ['ResponseID', 'Progress']]
        
        if len(numerical_cols) > 1:
            selected_vars = st.multiselect(
                "Select Variables for Correlation Analysis:",
                numerical_cols,
                default=numerical_cols[:min(8, len(numerical_cols))]
            )
            
            if len(selected_vars) > 1:
                # Calculate correlation matrix
                corr_matrix = filtered_df[selected_vars].corr()
                
                # Create heatmap
                fig = px.imshow(
                    corr_matrix,
                    title="Correlation Matrix",
                    color_continuous_scale='RdBu',
                    aspect="auto"
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show correlation table
                st.markdown("**Correlation Coefficients:**")
                st.dataframe(corr_matrix.round(3), use_container_width=True)
        else:
            st.info("Insufficient numerical variables for correlation analysis.")
    
    elif analysis_option == "Risk Assessment":
        st.markdown("#### ⚠️ Risk Assessment Analysis")
        
        # Identify high-risk combinations
        disruption_cols = [col for col in filtered_df.columns if col.startswith('Q9_') and 'No disruptions' not in col]
        
        if disruption_cols and 'Q2_Professional_Role' in filtered_df.columns:
            st.markdown("**High-Risk Professional Role & Service Combinations:**")
            
            risk_data = []
            
            for role in filtered_df['Q2_Professional_Role'].unique():
                role_data = filtered_df[filtered_df['Q2_Professional_Role'] == role]
                
                for service in disruption_cols:
                    if len(role_data) > 0:
                        disruption_rate = role_data[service].mean() * 100
                        sample_size = len(role_data)
                        
                        # Define risk level
                        if disruption_rate >= 50:
                            risk_level = "Very High"
                        elif disruption_rate >= 35:
                            risk_level = "High"
                        elif disruption_rate >= 20:
                            risk_level = "Medium"
                        else:
                            risk_level = "Low"
                        
                        risk_data.append({
                            'Professional Role': role,
                            'Service': service.replace('Q9_', '').replace('_', ' ').title(),
                            'Disruption Rate (%)': disruption_rate,
                            'Risk Level': risk_level,
                            'Sample Size': sample_size
                        })
            
            risk_df = pd.DataFrame(risk_data)
            
            # Filter for high-risk combinations
            high_risk = risk_df[risk_df['Risk Level'].isin(['Very High', 'High'])].sort_values('Disruption Rate (%)', ascending=False)
            
            if not high_risk.empty:
                st.markdown("**🚨 Priority Interventions Needed:**")
                
                for _, row in high_risk.head(10).iterrows():
                    risk_color = "red" if row['Risk Level'] == 'Very High' else "orange"
                    st.markdown(f"""
                    <div style="border-left: 4px solid {risk_color}; padding: 10px; margin: 5px 0; background-color: #f9f9f9;">
                        <strong>{row['Professional Role']}</strong> - {row['Service']}<br>
                        <span style="color: {risk_color}; font-weight: bold;">{row['Disruption Rate (%)']:.1f}% disruption rate</span>
                        (n={row['Sample Size']})
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ No high-risk combinations identified in the filtered dataset.")

def show_data_explorer(df):
    """Display data exploration interface"""
    st.markdown("## 📋 Data Explorer")
    
    st.markdown("""
    <div class="research-question">
        <strong>🔍 Purpose:</strong> Explore the raw survey data, view variable distributions, 
        and export data for external analysis.
    </div>
    """, unsafe_allow_html=True)
    
    # Data overview
    st.markdown("### 📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(df))
    
    with col2:
        st.metric("Total Variables", len(df.columns))
    
    with col3:
        missing_values = df.isnull().sum().sum()
        st.metric("Missing Values", f"{missing_values:,}")
    
    with col4:
        missing_pct = (missing_values / (len(df) * len(df.columns))) * 100
        st.metric("Missing %", f"{missing_pct:.1f}%")
    
    # Variable explorer
    st.markdown("### 🔍 Variable Explorer")
    
    # Categorize variables
    variable_categories = {
        "Demographics & Characteristics": [col for col in df.columns if col.startswith(('Q2_', 'Q5_'))],
        "Clinical Settings": [col for col in df.columns if 'Setting' in col],
        "Funding Sources": [col for col in df.columns if 'Funding' in col],
        "Populations Served": [col for col in df.columns if 'Serve' in col],
        "Service Disruptions": [col for col in df.columns if col.startswith('Q9_')],
        "Access & Barriers": [col for col in df.columns if col.startswith(('Q21', 'Q22', 'Q23'))],
        "Future Concerns": [col for col in df.columns if col.startswith(('Q11', 'Q12', 'Q13', 'Q15'))],
        "Federal Guidance": [col for col in df.columns if col.startswith('Q18')]
    }
    
    selected_category = st.selectbox("Select Variable Category:", list(variable_categories.keys()))
    
    if variable_categories[selected_category]:
        selected_variable = st.selectbox(
            "Select Variable:", 
            variable_categories[selected_category],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_variable:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Variable distribution
                if df[selected_variable].dtype in ['object', 'category']:
                    value_counts = df[selected_variable].value_counts()
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f"Distribution: {selected_variable.replace('_', ' ').title()}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = px.histogram(
                        df, 
                        x=selected_variable,
                        title=f"Distribution: {selected_variable.replace('_', ' ').title()}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Variable statistics
                st.markdown("**Variable Information:**")
                st.text(f"Type: {df[selected_variable].dtype}")
                st.text(f"Non-null: {df[selected_variable].notna().sum()}")
                st.text(f"Missing: {df[selected_variable].isnull().sum()}")
                st.text(f"Unique: {df[selected_variable].nunique()}")
                
                if df[selected_variable].dtype in ['object', 'category']:
                    st.markdown("**Value Counts:**")
                    value_counts = df[selected_variable].value_counts()
                    for val, count in value_counts.head(5).items():
                        pct = (count / len(df)) * 100
                        st.text(f"{val}: {count} ({pct:.1f}%)")
    
    # Data table viewer
    st.markdown("### 📋 Data Table Viewer")
    
    # Column selector
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select Columns to Display:",
        all_columns,
        default=all_columns[:10] if len(all_columns) > 10 else all_columns
    )
    
    if selected_columns:
        # Row filter
        max_rows = len(df)
        num_rows = st.slider("Number of Rows to Display:", 1, min(max_rows, 1000), min(100, max_rows))
        
        # Display filtered data
        display_df = df[selected_columns].head(num_rows)
        st.dataframe(display_df, use_container_width=True)
        
        # Export options
        st.markdown("### 📥 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV export
            csv_data = display_df.to_csv(index=False)
            st.download_button(
                label="📊 Download as CSV",
                data=csv_data,
                file_name="hiv_survey_data.csv",
                mime="text/csv"
            )
        
        with col2:
            # Excel export would require additional libraries
            st.info("💡 Excel export available in full version")
        
        with col3:
            # Summary report
            if st.button("📄 Generate Summary Report"):
                summary_data = {
                    'Variable': [],
                    'Type': [],
                    'Non_Null': [],
                    'Missing': [],
                    'Unique_Values': []
                }
                
                for col in selected_columns:
                    summary_data['Variable'].append(col)
                    summary_data['Type'].append(str(df[col].dtype))
                    summary_data['Non_Null'].append(df[col].notna().sum())
                    summary_data['Missing'].append(df[col].isnull().sum())
                    summary_data['Unique_Values'].append(df[col].nunique())
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)

if __name__ == "__main__":
    main()
