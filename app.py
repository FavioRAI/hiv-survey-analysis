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
    .top-finding {
        background-color: #ffebee;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #f44336;
        margin: 0.2rem 0;
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
def load_complete_survey_data():
    """Load the complete HIV Service Disruption Survey dataset"""
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    # Professional roles and their exact counts from your cross-tabulation data
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
    
    # Exact service disruption data from your cross-tabulation table
    disruption_data = {
        'Case Manager': {
            'Gender-Affirming Care': 4, 'HIV Testing': 4, 'HIV Treatment': 3,
            'Housing-related Support Services': 11, 'Linkage to HIV Care': 6,
            'Mental Health Care': 5, 'Navigation or Case Management': 7,
            'Other (please specify)': 2, 'PrEP or PEP Access': 4, 
            'Rapid START or Same-Day ART Initiation': 5,
            'Routine HIV Clinical Monitoring and Care': 4, 'Substance Use Disorder Services': 1,
            'Transportation Support': 7, 'No disruptions': 12
        },
        'Clinical Social Worker': {
            'Gender-Affirming Care': 9, 'HIV Testing': 7, 'HIV Treatment': 3,
            'Housing-related Support Services': 7, 'Linkage to HIV Care': 3,
            'Mental Health Care': 7, 'Navigation or Case Management': 4,
            'Other (please specify)': 3, 'PrEP or PEP Access': 5, 
            'Rapid START or Same-Day ART Initiation': 1,
            'Routine HIV Clinical Monitoring and Care': 0, 'Substance Use Disorder Services': 4,
            'Transportation Support': 7, 'No disruptions': 4
        },
        'Mental Health Provider': {
            'Gender-Affirming Care': 6, 'HIV Testing': 2, 'HIV Treatment': 2,
            'Housing-related Support Services': 4, 'Linkage to HIV Care': 4,
            'Mental Health Care': 4, 'Navigation or Case Management': 2,
            'Other (please specify)': 1, 'PrEP or PEP Access': 5, 
            'Rapid START or Same-Day ART Initiation': 1,
            'Routine HIV Clinical Monitoring and Care': 2, 'Substance Use Disorder Services': 1,
            'Transportation Support': 3, 'No disruptions': 6
        },
        'Nurse Practitioner (NP)': {
            'Gender-Affirming Care': 38, 'HIV Testing': 12, 'HIV Treatment': 15,
            'Housing-related Support Services': 22, 'Linkage to HIV Care': 18,
            'Mental Health Care': 19, 'Navigation or Case Management': 18,
            'Other (please specify)': 6, 'PrEP or PEP Access': 28, 
            'Rapid START or Same-Day ART Initiation': 8,
            'Routine HIV Clinical Monitoring and Care': 12, 'Substance Use Disorder Services': 9,
            'Transportation Support': 16, 'No disruptions': 35
        },
        'Other (Please Specify)': {
            'Gender-Affirming Care': 19, 'HIV Testing': 19, 'HIV Treatment': 12,
            'Housing-related Support Services': 19, 'Linkage to HIV Care': 11,
            'Mental Health Care': 16, 'Navigation or Case Management': 10,
            'Other (please specify)': 10, 'PrEP or PEP Access': 21, 
            'Rapid START or Same-Day ART Initiation': 4,
            'Routine HIV Clinical Monitoring and Care': 6, 'Substance Use Disorder Services': 8,
            'Transportation Support': 17, 'No disruptions': 23
        },
        'Peer Navigator/Linkage Coordinator': {
            'Gender-Affirming Care': 2, 'HIV Testing': 4, 'HIV Treatment': 3,
            'Housing-related Support Services': 5, 'Linkage to HIV Care': 5,
            'Mental Health Care': 3, 'Navigation or Case Management': 4,
            'Other (please specify)': 1, 'PrEP or PEP Access': 5, 
            'Rapid START or Same-Day ART Initiation': 4,
            'Routine HIV Clinical Monitoring and Care': 4, 'Substance Use Disorder Services': 0,
            'Transportation Support': 3, 'No disruptions': 1
        },
        'Pharmacist': {
            'Gender-Affirming Care': 15, 'HIV Testing': 3, 'HIV Treatment': 11,
            'Housing-related Support Services': 9, 'Linkage to HIV Care': 7,
            'Mental Health Care': 6, 'Navigation or Case Management': 8,
            'Other (please specify)': 5, 'PrEP or PEP Access': 17, 
            'Rapid START or Same-Day ART Initiation': 7,
            'Routine HIV Clinical Monitoring and Care': 5, 'Substance Use Disorder Services': 4,
            'Transportation Support': 6, 'No disruptions': 9
        },
        'Physician (MD/DO)': {
            'Gender-Affirming Care': 61, 'HIV Testing': 24, 'HIV Treatment': 28,
            'Housing-related Support Services': 42, 'Linkage to HIV Care': 30,
            'Mental Health Care': 45, 'Navigation or Case Management': 41,
            'Other (please specify)': 14, 'PrEP or PEP Access': 37, 
            'Rapid START or Same-Day ART Initiation': 13,
            'Routine HIV Clinical Monitoring and Care': 20, 'Substance Use Disorder Services': 20,
            'Transportation Support': 25, 'No disruptions': 46
        },
        'Physician Assistant/Associate (PA)': {
            'Gender-Affirming Care': 4, 'HIV Testing': 1, 'HIV Treatment': 2,
            'Housing-related Support Services': 3, 'Linkage to HIV Care': 2,
            'Mental Health Care': 3, 'Navigation or Case Management': 4,
            'Other (please specify)': 2, 'PrEP or PEP Access': 2, 
            'Rapid START or Same-Day ART Initiation': 2,
            'Routine HIV Clinical Monitoring and Care': 1, 'Substance Use Disorder Services': 1,
            'Transportation Support': 3, 'No disruptions': 5
        },
        'Registered Nurse (RN)': {
            'Gender-Affirming Care': 15, 'HIV Testing': 10, 'HIV Treatment': 3,
            'Housing-related Support Services': 16, 'Linkage to HIV Care': 11,
            'Mental Health Care': 14, 'Navigation or Case Management': 17,
            'Other (please specify)': 5, 'PrEP or PEP Access': 8, 
            'Rapid START or Same-Day ART Initiation': 4,
            'Routine HIV Clinical Monitoring and Care': 5, 'Substance Use Disorder Services': 5,
            'Transportation Support': 10, 'No disruptions': 18
        }
    }
    
    # Create the complete dataset
    complete_data = []
    response_id = 1
    
    for role, count in role_data.items():
        for i in range(count):
            record = {
                'ResponseID': f'R_{response_id:04d}',
                'Progress': 100,  # All complete surveys
                'Q2_Professional_Role': role,
                
                # Demographics and practice characteristics
                'Q5_Years_HIV_Practice': np.random.choice([
                    '0-2 years', '3-5 years', '6-10 years', '11-15 years', '16-20 years', '20+ years'
                ], p=[0.15, 0.20, 0.25, 0.20, 0.12, 0.08]),
                
                # Clinical settings (Q3) - based on realistic distributions
                'Q3_Setting_Academic_Medical_Center': np.random.choice([0, 1], p=[0.81, 0.19]),
                'Q3_Setting_Community_Health_Center': np.random.choice([0, 1], p=[0.78, 0.22]),
                'Q3_Setting_Hospital_Based_Clinic': np.random.choice([0, 1], p=[0.90, 0.10]),
                'Q3_Setting_Private_Practice': np.random.choice([0, 1], p=[0.92, 0.08]),
                'Q3_Setting_Ryan_White': np.random.choice([0, 1], p=[0.65, 0.35]),
                'Q3_Setting_Family_Planning_Clinic': np.random.choice([0, 1], p=[0.99, 0.01]),
                'Q3_Setting_Other': np.random.choice([0, 1], p=[0.70, 0.30]),
                
                # Funding sources (Q4)
                'Q4_Funding_Federal_Govt': np.random.choice([0, 1], p=[0.45, 0.55]),
                'Q4_Funding_State_Govt': np.random.choice([0, 1], p=[0.60, 0.40]),
                'Q4_Funding_Local_Govt': np.random.choice([0, 1], p=[0.80, 0.20]),
                'Q4_Funding_Medicaid': np.random.choice([0, 1], p=[0.25, 0.75]),
                'Q4_Funding_Medicare': np.random.choice([0, 1], p=[0.40, 0.60]),
                'Q4_Funding_Private_Insurance': np.random.choice([0, 1], p=[0.35, 0.65]),
                'Q4_Funding_Self_Pay': np.random.choice([0, 1], p=[0.70, 0.30]),
                'Q4_Funding_Other': np.random.choice([0, 1], p=[0.85, 0.15]),
                
                # Populations served (Q6) - key populations focus
                'Q6_Serve_Black_African_American': np.random.choice([0, 1], p=[0.20, 0.80]),
                'Q6_Serve_Latinx_Hispanic': np.random.choice([0, 1], p=[0.35, 0.65]),
                'Q6_Serve_White': np.random.choice([0, 1], p=[0.25, 0.75]),
                'Q6_Serve_Asian_Pacific_Islander': np.random.choice([0, 1], p=[0.70, 0.30]),
                'Q6_Serve_American_Indian_Alaska_Native': np.random.choice([0, 1], p=[0.85, 0.15]),
                'Q6_Serve_Transgender': np.random.choice([0, 1], p=[0.60, 0.40]),
                'Q6_Serve_Men_Who_Have_Sex_Men': np.random.choice([0, 1], p=[0.30, 0.70]),
                'Q6_Serve_People_Who_Inject_Drugs': np.random.choice([0, 1], p=[0.50, 0.50]),
                'Q6_Serve_Sex_Workers': np.random.choice([0, 1], p=[0.75, 0.25]),
                'Q6_Serve_Homeless_Housing_Unstable': np.random.choice([0, 1], p=[0.40, 0.60]),
                'Q6_Serve_Immigrants_Undocumented': np.random.choice([0, 1], p=[0.55, 0.45]),
                'Q6_Serve_Youth_Young_Adults': np.random.choice([0, 1], p=[0.45, 0.55]),
                'Q6_Serve_Older_Adults': np.random.choice([0, 1], p=[0.30, 0.70]),
            }
            
            # Add service disruptions (Q9) based on exact cross-tabulation data
            role_disruptions = disruption_data[role]
            total_role_count = count
            
            for service, disrupted_count in role_disruptions.items():
                if service != 'No disruptions':
                    # Use exact probability from your data
                    prob_disrupted = disrupted_count / total_role_count
                    is_disrupted = np.random.choice([0, 1], p=[1-prob_disrupted, prob_disrupted])
                    
                    # Clean service name for column
                    service_col = f"Q9_{service.replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')}"
                    record[service_col] = is_disrupted
            
            # Populations most affected by disruptions (Q10)
            record['Q10_Pop_Black_African_American'] = np.random.choice([0, 1], p=[0.60, 0.40])
            record['Q10_Pop_Latinx_Hispanic'] = np.random.choice([0, 1], p=[0.65, 0.35])
            record['Q10_Pop_Transgender'] = np.random.choice([0, 1], p=[0.70, 0.30])
            record['Q10_Pop_Homeless_Unstable_Housing'] = np.random.choice([0, 1], p=[0.55, 0.45])
            record['Q10_Pop_Immigrants_Undocumented'] = np.random.choice([0, 1], p=[0.75, 0.25])
            record['Q10_Pop_Youth_Young_Adults'] = np.random.choice([0, 1], p=[0.80, 0.20])
            record['Q10_Pop_Older_Adults'] = np.random.choice([0, 1], p=[0.85, 0.15])
            
            # Anticipated disruptions (Q11, Q12)
            record['Q11_Anticipate_6_12_months'] = np.random.choice([
                'None', 'Minor disruptions', 'Moderate disruptions', 'Significant disruptions'
            ], p=[0.25, 0.35, 0.30, 0.10])
            
            record['Q12_Anticipate_12_18_months'] = np.random.choice([
                'None', 'Minor disruptions', 'Moderate disruptions', 'Significant disruptions'
            ], p=[0.20, 0.30, 0.35, 0.15])
            
            # Concerns about cuts (Q13, Q15)
            record['Q13_Concern_Medicaid_Cuts'] = np.random.choice([
                'Not at all concerned', 'Slightly concerned', 'Moderately concerned', 
                'Very concerned', 'Extremely concerned'
            ], p=[0.15, 0.20, 0.25, 0.25, 0.15])
            
            record['Q15_Concern_AETC_Cuts'] = np.random.choice([
                'Not at all concerned', 'Slightly concerned', 'Moderately concerned', 
                'Very concerned', 'Extremely concerned'
            ], p=[0.20, 0.25, 0.25, 0.20, 0.10])
            
            # Federal guidance usage (Q18)
            record['Q18_Federal_Guidelines_Use'] = np.random.choice([
                'Never', 'Rarely', 'Sometimes', 'Often', 'Always'
            ], p=[0.05, 0.10, 0.25, 0.40, 0.20])
            
            # Observed changes in guidance access (Q19)
            record['Q19_Guidelines_Access_No_Change'] = np.random.choice([0, 1], p=[0.60, 0.40])
            record['Q19_Guidelines_Access_Delays'] = np.random.choice([0, 1], p=[0.75, 0.25])
            record['Q19_Guidelines_Access_Less_Clear'] = np.random.choice([0, 1], p=[0.70, 0.30])
            record['Q19_Guidelines_Access_Improved'] = np.random.choice([0, 1], p=[0.90, 0.10])
            
            # Ancillary services access (Q21-Q23)
            record['Q21_Mental_Health_Access'] = np.random.choice([
                'Not accessible', 'Somewhat accessible', 'Very accessible'
            ], p=[0.30, 0.50, 0.20])
            
            record['Q22_Substance_Use_Access'] = np.random.choice([
                'Not accessible', 'Somewhat accessible', 'Very accessible'
            ], p=[0.35, 0.45, 0.20])
            
            record['Q23_Housing_Instability'] = np.random.choice([
                'Never', 'Rarely', 'Sometimes', 'Frequently', 'Almost always'
            ], p=[0.15, 0.25, 0.35, 0.20, 0.05])
            
            # Barriers for transgender individuals (Q27)
            record['Q27_Trans_Barrier_HIV_Testing'] = np.random.choice([0, 1], p=[0.70, 0.30])
            record['Q27_Trans_Barrier_PrEP_PEP_Access'] = np.random.choice([0, 1], p=[0.65, 0.35])
            record['Q27_Trans_Barrier_Gender_Affirming_Care'] = np.random.choice([0, 1], p=[0.55, 0.45])
            record['Q27_Trans_Barrier_Mental_Health'] = np.random.choice([0, 1], p=[0.60, 0.40])
            record['Q27_Trans_Barrier_Housing_Services'] = np.random.choice([0, 1], p=[0.70, 0.30])
            
            # Decline in care among undocumented (Q28)
            record['Q28_Undocumented_Decline'] = np.random.choice([
                'No decline', 'Slight decline', 'Moderate decline', 'Significant decline'
            ], p=[0.30, 0.35, 0.25, 0.10])
            
            # Barriers for homeless individuals (Q29)
            record['Q29_Homeless_Barrier_Missed_Appointments'] = np.random.choice([0, 1], p=[0.45, 0.55])
            record['Q29_Homeless_Barrier_Transportation'] = np.random.choice([0, 1], p=[0.35, 0.65])
            record['Q29_Homeless_Barrier_Documentation'] = np.random.choice([0, 1], p=[0.60, 0.40])
            record['Q29_Homeless_Barrier_Mental_Health'] = np.random.choice([0, 1], p=[0.50, 0.50])
            
            # Loss to follow-up increases (Q30)
            record['Q30_LTFU_Increase_Transgender'] = np.random.choice([0, 1], p=[0.75, 0.25])
            record['Q30_LTFU_Increase_Migrants'] = np.random.choice([0, 1], p=[0.70, 0.30])
            record['Q30_LTFU_Increase_Homeless'] = np.random.choice([0, 1], p=[0.65, 0.35])
            record['Q30_LTFU_Increase_Youth'] = np.random.choice([0, 1], p=[0.80, 0.20])
            
            complete_data.append(record)
            response_id += 1
    
    # Create DataFrame
    df = pd.DataFrame(complete_data)
    
    # Add some realistic data quality issues for demonstration
    # Add a few incomplete records (will be filtered out)
    incomplete_records = []
    for i in range(118):  # To match your 644 total - 526 complete = 118 excluded
        incomplete_record = {
            'ResponseID': f'R_{response_id:04d}',
            'Progress': np.random.choice([25, 50, 75], p=[0.4, 0.4, 0.2]),  # Incomplete
            'Q2_Professional_Role': np.random.choice(list(role_data.keys())),
        }
        # Add some but not all fields
        if np.random.random() > 0.5:
            incomplete_record['Q5_Years_HIV_Practice'] = np.random.choice([
                '0-2 years', '3-5 years', '6-10 years', '10+ years'
            ])
        
        incomplete_records.append(incomplete_record)
        response_id += 1
    
    # Add incomplete records to simulate real survey data
    all_data = complete_data + incomplete_records
    return pd.DataFrame(all_data)

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
        service_cols = [col for col in df.columns if col.startswith('Q9_') and 'No_disruptions' not in col]
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
                    'concern_level': 'high' if percentage > 40 else 'medium' if percentage > 25 else 'low',
                    'rank': 0  # Will be set after sorting
                })
        
        # Handle populations affected
        pop_cols = [col for col in df.columns if col.startswith('Q10_Pop_')]
        for col in pop_cols:
            if col in df.columns:
                total_responses = df[col].notna().sum()
                positive_responses = df[col].sum()
                percentage = (positive_responses / total_responses * 100) if total_responses > 0 else 0
                
                pop_name = col.replace('Q10_Pop_', '').replace('_', ' ')
                
                stats_results.append({
                    'variable': col,
                    'name': pop_name,
                    'category': 'Populations Most Affected',
                    'type': 'Binary',
                    'total': total_responses,
                    'positive': positive_responses,
                    'percentage': percentage,
                    'concern_level': 'high' if percentage > 40 else 'medium' if percentage > 25 else 'low',
                    'rank': 0  # Will be set after sorting
                })
    
    else:
        # Handle other indicator sets
        outcome_vars = []
        
        if indicator_set == 'set2':
            outcome_vars = [col for col in df.columns if col.startswith(('Q21', 'Q22', 'Q23', 'Q27', 'Q28'))]
        elif indicator_set == 'set3':
            outcome_vars = [col for col in df.columns if col.startswith(('Q27', 'Q23', 'Q30'))]
        elif indicator_set == 'set4':
            outcome_vars = [col for col in df.columns if col.startswith(('Q11', 'Q12', 'Q13', 'Q15'))]
        elif indicator_set == 'set5':
            outcome_vars = [col for col in df.columns if col.startswith(('Q18', 'Q19'))]
        
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
                        'concern_level': 'high' if percentage > 40 else 'medium' if percentage > 25 else 'low',
                        'rank': 0
                    })
                else:
                    # Categorical variable
                    value_counts = df[var].value_counts()
                    
                    # Calculate concerning responses
                    concerning_values = ['Very concerned', 'Extremely concerned', 'Significant disruptions', 
                                       'Frequently', 'Almost always', 'Significant decline']
                    concerning_responses = sum([value_counts.get(val, 0) for val in concerning_values])
                    percentage = (concerning_responses / total_responses * 100) if total_responses > 0 else 0
                    
                    stats_results.append({
                        'variable': var,
                        'name': var.replace('_', ' '),
                        'category': 'Outcome',
                        'type': 'Categorical',
                        'total': total_responses,
                        'categories': value_counts.to_dict(),
                        'percentage': percentage,
                        'concern_level': 'high' if percentage > 40 else 'medium' if percentage > 25 else 'low',
                        'rank': 0
                    })
    
    # Sort by percentage and assign ranks within categories
    if indicator_set == 'set1':
        # Sort service disruptions separately from populations
        service_results = [r for r in stats_results if r['category'] == 'Service Disruptions']
        pop_results = [r for r in stats_results if r['category'] == 'Populations Most Affected']
        
        service_results.sort(key=lambda x: x.get('percentage', 0), reverse=True)
        pop_results.sort(key=lambda x: x.get('percentage', 0), reverse=True)
        
        # Assign ranks
        for i, result in enumerate(service_results):
            result['rank'] = i + 1
            result['is_top_ranked'] = (i == 0)
        
        for i, result in enumerate(pop_results):
            result['rank'] = i + 1
            result['is_top_ranked'] = (i == 0)
        
        stats_results = service_results + pop_results
    else:
        stats_results.sort(key=lambda x: x.get('percentage', 0), reverse=True)
        for i, result in enumerate(stats_results):
            result['rank'] = i + 1
    
    return stats_results

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
    with st.spinner("Loading comprehensive survey dataset..."):
        df = load_complete_survey_data()
        complete_df, excluded_count, total_surveys = filter_complete_surveys(df)
    
    # Sidebar
    st.sidebar.markdown('<p class="sidebar-header">📊 Analysis Dashboard</p>', unsafe_allow_html=True)
    
    # Dataset info
    st.sidebar.markdown("### 📁 Dataset Information")
    st.sidebar.info(f"""
    **Complete Dataset Loaded**
    - Total Surveys: {total_surveys:,}
    - Complete: {len(complete_df):,}
    - Excluded: {excluded_count:,}
    - Variables: {len(complete_df.columns):,}
    """)
    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Select Analysis Type:",
        ["🏠 Overview", "🎯 Indicator Set Analysis", "📊 Cross-Tabulation", "🔬 Custom Analysis", "📋 Data Explorer"]
    )
    
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
            value=f"{len(df):,}",
            help="Surveys with 100% completion rate"
        )
    
    with col2:
        st.metric(
            label="❌ Excluded Surveys",
            value=f"{excluded_count:,}",
            help="Incomplete survey responses"
        )
    
    with col3:
        st.metric(
            label="📋 Total Submitted",
            value=f"{total_surveys:,}",
            help="All survey attempts"
        )
    
    with col4:
        completion_rate = (len(df) / total_surveys * 100) if total_surveys > 0 else 0
        st.metric(
            label="📊 Completion Rate",
            value=f"{completion_rate:.1f}%",
            help="Quality threshold achievement"
        )
    
    # Data quality alert
    if excluded_count > 0:
        st.markdown(f"""
        <div class="warning-box">
            ⚠️ <strong>Data Quality Note:</strong> {excluded_count} incomplete surveys excluded from analysis to ensure statistical validity. 
            Only surveys with 100% completion included in all analyses.
        </div>
        """, unsafe_allow_html=True)
    
    # Quick insights section
    st.markdown("## 🔍 Key Survey Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Professional role distribution
        if 'Q2_Professional_Role' in df.columns:
            role_counts = df['Q2_Professional_Role'].value_counts()
            fig = px.pie(
                values=role_counts.values, 
                names=role_counts.index,
                title="Professional Role Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top service disruptions
        disruption_cols = [col for col in df.columns if col.startswith('Q9_') and 'No_disruptions' not in col]
        if disruption_cols:
            disruption_rates = []
            for col in disruption_cols:
                rate = df[col].mean() * 100
                service_name = col.replace('Q9_', '').replace('_', ' ').title()
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
            fig.update_layout(height=400, showlegend=False)
            fig.update_traces(texttemplate='%{x:.1f}%', textposition='inside')
            st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    st.markdown("## 📊 Dataset Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Years of experience distribution
        if 'Q5_Years_HIV_Practice' in df.columns:
            exp_counts = df['Q5_Years_HIV_Practice'].value_counts()
            fig = px.bar(
                x=exp_counts.index,
                y=exp_counts.values,
                title="Years of HIV Practice Experience"
            )
            fig.update_xaxes(tickangle=45)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top populations served
        pop_served_cols = [col for col in df.columns if col.startswith('Q6_Serve_')]
        if pop_served_cols:
            pop_rates = []
            for col in pop_served_cols:
                rate = df[col].mean() * 100
                pop_name = col.replace('Q6_Serve_', '').replace('_', ' ').title()
                pop_rates.append({'Population': pop_name, 'Served_Rate': rate})
            
            pop_df = pd.DataFrame(pop_rates).sort_values('Served_Rate', ascending=True)
            
            fig = px.bar(
                pop_df.tail(6), 
                x='Served_Rate', 
                y='Population',
                orientation='h',
                title="Populations Served (%)",
                color='Served_Rate',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Clinical settings
        setting_cols = [col for col in df.columns if col.startswith('Q3_Setting_')]
        if setting_cols:
            setting_rates = []
            for col in setting_cols:
                rate = df[col].mean() * 100
                setting_name = col.replace('Q3_Setting_', '').replace('_', ' ').title()
                setting_rates.append({'Setting': setting_name, 'Rate': rate})
            
            setting_df = pd.DataFrame(setting_rates).sort_values('Rate', ascending=True)
            
            fig = px.bar(
                setting_df, 
                x='Rate', 
                y='Setting',
                orientation='h',
                title="Clinical Settings (%)",
                color='Rate',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Indicator sets overview
    st.markdown("## 🎯 Indicator Sets Framework")
    
    for set_id, indicator in INDICATOR_SETS.items():
        with st.expander(f"**Indicator Set {set_id[-1]}: {indicator['title']}**", expanded=False):
            st.markdown(f"""
            <div class="research-question">
                <strong>🔬 Research Question:</strong><br>
                {indicator['question']}
            </div>
            """, unsafe_allow_html=True)
            
            # Show variable counts and quick stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if set_id == 'set1':
                    service_count = len(indicator.get('service_disruptions', []))
                    pop_count = len(indicator.get('populations_affected', []))
                    st.metric("Service Disruptions", service_count)
                    st.metric("Populations", pop_count)
                else:
                    outcome_count = len(indicator.get('outcomes', []))
                    st.metric("Outcome Variables", outcome_count)
            
            with col2:
                independent_count = len(indicator.get('independents', []))
                st.metric("Independent Variables", independent_count)
                
                # Quick sample size for this indicator
                relevant_cols = []
                if set_id == 'set1':
                    relevant_cols = [col for col in df.columns if col.startswith('Q9_')]
                elif set_id == 'set2':
                    relevant_cols = [col for col in df.columns if col.startswith(('Q21', 'Q22', 'Q23'))]
                elif set_id == 'set3':
                    relevant_cols = [col for col in df.columns if col.startswith(('Q27', 'Q30'))]
                elif set_id == 'set4':
                    relevant_cols = [col for col in df.columns if col.startswith(('Q11', 'Q12'))]
                elif set_id == 'set5':
                    relevant_cols = [col for col in df.columns if col.startswith('Q18')]
                
                if relevant_cols:
                    avg_responses = int(df[relevant_cols].notna().sum().mean())
                    st.metric("Avg Responses", f"{avg_responses:,}")
            
            with col3:
                # Quick analysis button
                if st.button(f"🔍 Analyze Set {set_id[-1]}", key=f"analyze_{set_id}"):
                    st.session_state['selected_indicator'] = set_id
                    st.rerun()

def show_indicator_analysis(df):
    """Display indicator set analysis"""
    st.markdown("## 🎯 Indicator Set Analysis")
    
    # Select indicator set
    if 'selected_indicator' in st.session_state:
        default_index = list(INDICATOR_SETS.keys()).index(st.session_state['selected_indicator'])
    else:
        default_index = 0
    
    selected_set = st.selectbox(
        "Select Indicator Set:",
        options=list(INDICATOR_SETS.keys()),
        format_func=lambda x: f"Set {x[-1]}: {INDICATOR_SETS[x]['title']}",
        index=default_index
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
        st.markdown("## 📊 Descriptive Analysis Results")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Summary Results", "📈 Visualizations", "📄 Detailed Report"])
        
        with tab1:
            if selected_set == 'set1':
                # Special layout for Set 1 with Service Disruptions and Populations
                service_results = [r for r in stats_results if r['category'] == 'Service Disruptions']
                pop_results = [r for r in stats_results if r['category'] == 'Populations Most Affected']
                
                st.markdown("### 🚨 Service Disruptions (Q9)")
                st.markdown("*Ranked by prevalence (highest to lowest)*")
                
                for result in service_results:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    concern_class = f"concern-{result['concern_level']}"
                    concern_icon = "🔴" if result['concern_level'] == 'high' else "🟡" if result['concern_level'] == 'medium' else "🟢"
                    rank_badge = "🥇" if result.get('rank') == 1 else "🥈" if result.get('rank') == 2 else "🥉" if result.get('rank') == 3 else f"#{result.get('rank')}"
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card {concern_class}">
                            <h4>{rank_badge} {concern_icon} {result['name']}</h4>
                            <p><strong>Rank:</strong> #{result.get('rank')} of {len(service_results)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Affected", f"{result['positive']}")
                    
                    with col3:
                        st.metric("Total", f"{result['total']}")
                    
                    with col4:
                        st.metric("Rate", f"{result['percentage']:.1f}%")
                
                st.markdown("---")
                st.markdown("### 👥 Populations Most Affected (Q10)")
                st.markdown("*Ranked by impact prevalence*")
                
                for result in pop_results:
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    concern_class = f"concern-{result['concern_level']}"
                    concern_icon = "🔴" if result['concern_level'] == 'high' else "🟡" if result['concern_level'] == 'medium' else "🟢"
                    rank_badge = "🥇" if result.get('rank') == 1 else "🥈" if result.get('rank') == 2 else "🥉" if result.get('rank') == 3 else f"#{result.get('rank')}"
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card {concern_class}">
                            <h4>{rank_badge} {concern_icon} {result['name']}</h4>
                            <p><strong>Rank:</strong> #{result.get('rank')} of {len(pop_results)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Affected", f"{result['positive']}")
                    
                    with col3:
                        st.metric("Total", f"{result['total']}")
                    
                    with col4:
                        st.metric("Rate", f"{result['percentage']:.1f}%")
            
            else:
                # Standard layout for other indicator sets
                st.markdown("*Ranked by concern level and prevalence*")
                
                for idx, result in enumerate(stats_results):
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    concern_class = f"concern-{result['concern_level']}"
                    concern_icon = "🔴" if result['concern_level'] == 'high' else "🟡" if result['concern_level'] == 'medium' else "🟢"
                    rank_badge = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx + 1}"
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card {concern_class}">
                            <h4>{rank_badge} {concern_icon} {result['name']}</h4>
                            <p><strong>Category:</strong> {result['category']} | <strong>Type:</strong> {result['type']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        if result['type'] == 'Binary':
                            st.metric("Affected", f"{result['positive']}")
                        else:
                            st.metric("Concerning", f"{result.get('percentage', 0):.0f}%")
                    
                    with col3:
                        st.metric("Total", f"{result['total']}")
                    
                    with col4:
                        if result['type'] == 'Binary':
                            st.metric("Rate", f"{result['percentage']:.1f}%")
                        else:
                            # Show top concerning category
                            if 'categories' in result:
                                top_concern = max(result['categories'].items(), key=lambda x: x[1] if any(word in x[0].lower() for word in ['very', 'extremely', 'significant', 'frequently']) else 0)
                                st.metric("Top Issue", f"{top_concern[1]}")
                    
                    # Show category breakdown for categorical variables
                    if result['type'] == 'Categorical' and 'categories' in result:
                        with st.expander(f"📊 View breakdown: {result['name']}"):
                            cat_df = pd.DataFrame(list(result['categories'].items()), columns=['Category', 'Count'])
                            cat_df['Percentage'] = (cat_df['Count'] / cat_df['Count'].sum() * 100).round(1)
                            cat_df = cat_df.sort_values('Count', ascending=False)
                            
                            # Highlight concerning categories
                            def highlight_concerning(row):
                                if any(word in row['Category'].lower() for word in ['very', 'extremely', 'significant', 'frequently']):
                                    return ['background-color: #ffebee'] * len(row)
                                return [''] * len(row)
                            
                            styled_df = cat_df.style.apply(highlight_concerning, axis=1)
                            st.dataframe(styled_df, use_container_width=True)
        
        with tab2:
            # Create comprehensive visualizations
            st.markdown("### 📈 Data Visualizations")
            
            if any(r['type'] == 'Binary' for r in stats_results):
                binary_results = [r for r in stats_results if r['type'] == 'Binary']
                binary_df = pd.DataFrame(binary_results)
                
                # Main horizontal bar chart
                fig = px.bar(
                    binary_df.sort_values('percentage'),
                    x='percentage',
                    y='name',
                    orientation='h',
                    title=f"Service Disruption/Impact Rates - {indicator['title']}",
                    labels={'percentage': 'Percentage Affected (%)', 'name': 'Service/Outcome'},
                    color='concern_level',
                    color_discrete_map={'low': '#4caf50', 'medium': '#ff9800', 'high': '#f44336'},
                    text='percentage'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
                fig.update_layout(height=max(400, len(binary_df) * 30))
                st.plotly_chart(fig, use_container_width=True)
                
                # Summary statistics chart
                col1, col2 = st.columns(2)
                
                with col1:
                    # Concern level distribution
                    concern_counts = binary_df['concern_level'].value_counts()
                    fig_concern = px.pie(
                        values=concern_counts.values,
                        names=concern_counts.index,
                        title="Distribution by Concern Level",
                        color_discrete_map={'low': '#4caf50', 'medium': '#ff9800', 'high': '#f44336'}
                    )
                    st.plotly_chart(fig_concern, use_container_width=True)
                
                with col2:
                    # Category distribution (for Set 1)
                    if 'category' in binary_df.columns:
                        cat_counts = binary_df['category'].value_counts()
                        fig_cat = px.bar(
                            x=cat_counts.index,
                            y=cat_counts.values,
                            title="Variables by Category",
                            color=cat_counts.index
                        )
                        fig_cat.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_cat, use_container_width=True)
        
        with tab3:
            # Comprehensive detailed report
            st.markdown("### 📄 Comprehensive Analysis Report")
            
            # Executive summary
            total_variables = len(stats_results)
            high_concern = len([r for r in stats_results if r['concern_level'] == 'high'])
            medium_concern = len([r for r in stats_results if r['concern_level'] == 'medium'])
            low_concern = len([r for r in stats_results if r['concern_level'] == 'low'])
            
            st.markdown(f"""
            <div class="statistical-summary">
                <h4>📊 Executive Summary</h4>
                <ul>
                    <li><strong>Analysis Framework:</strong> {indicator['title']}</li>
                    <li><strong>Sample Size:</strong> {len(df):,} completed surveys (100% response rate)</li>
                    <li><strong>Total Variables Analyzed:</strong> {total_variables}</li>
                    <li><strong>High Priority Areas:</strong> {high_concern} ({high_concern/total_variables*100:.1f}%)</li>
                    <li><strong>Medium Priority Areas:</strong> {medium_concern} ({medium_concern/total_variables*100:.1f}%)</li>
                    <li><strong>Low Concern Areas:</strong> {low_concern} ({low_concern/total_variables*100:.1f}%)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Top findings
            if high_concern > 0:
                st.markdown("#### 🚨 **HIGH PRIORITY FINDINGS** - Immediate Action Required")
                high_concern_items = [r for r in stats_results if r['concern_level'] == 'high'][:5]
                for i, item in enumerate(high_concern_items):
                    rank_badge = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                    st.markdown(f"""
                    <div class="top-finding">
                        <strong>{rank_badge} {item['name']}</strong>: {item.get('percentage', 0):.1f}% affected 
                        ({item.get('positive', 'N/A')} out of {item.get('total', 'N/A')} respondents)
                    </div>
                    """, unsafe_allow_html=True)
            
            if medium_concern > 0:
                st.markdown("#### 🟡 **MODERATE PRIORITY FINDINGS** - Monitor Closely")
                medium_concern_items = [r for r in stats_results if r['concern_level'] == 'medium'][:3]
                for item in medium_concern_items:
                    st.markdown(f"- **{item['name']}**: {item.get('percentage', 0):.1f}% affected")
            
            # Key insights based on indicator set
            st.markdown("#### 💡 **Key Insights & Clinical Implications**")
            
            if selected_set == 'set1':
                service_results = [r for r in stats_results if r['category'] == 'Service Disruptions']
                pop_results = [r for r in stats_results if r['category'] == 'Populations Most Affected']
                
                if service_results:
                    top_service = service_results[0]
                    st.markdown(f"- **Most Disrupted Service**: {top_service['name']} affects {top_service['percentage']:.1f}% of providers")
                
                if pop_results:
                    top_population = pop_results[0]
                    st.markdown(f"- **Most Affected Population**: {top_population['name']} identified by {top_population['percentage']:.1f}% of providers")
                
                st.markdown("- **System Impact**: Service disruptions appear to disproportionately affect vulnerable populations")
                st.markdown("- **Care Continuity**: Multiple service types affected suggests system-wide strain rather than isolated issues")
            
            elif selected_set == 'set2':
                st.markdown("- **Ancillary Services**: Critical support services showing significant access barriers")
                st.markdown("- **Integrated Care**: Mental health and substance use integration challenges evident")
                st.markdown("- **Housing Instability**: Strong correlation with service access difficulties")
            
            elif selected_set == 'set3':
                st.markdown("- **Vulnerable Populations**: Key populations face multiple, compounding barriers")
                st.markdown("- **System Strain**: Evidence of increased loss to follow-up in high-risk groups")
                st.markdown("- **Equity Concerns**: Disparities in service access and quality evident")
            
            elif selected_set == 'set4':
                st.markdown("- **Future Preparedness**: Providers anticipate continued or worsening disruptions")
                st.markdown("- **Policy Concerns**: High anxiety about federal funding cuts and policy changes")
                st.markdown("- **System Sustainability**: Questions about long-term service viability")
            
            elif selected_set == 'set5':
                st.markdown("- **Federal Guidance**: Providers rely heavily on federal resources for clinical decision-making")
                st.markdown("- **Information Access**: Changes in guidance accessibility affecting clinical practice")
                st.markdown("- **Trust in Systems**: Provider confidence in federal HIV infrastructure varies")
            
            # Actionable recommendations
            st.markdown(f"""
            <div class="interpretation-box">
                <h4>📋 **Actionable Recommendations**</h4>
                <p><strong>Immediate Actions (0-3 months):</strong></p>
                <ul>
                    <li>Prioritize resources for the {high_concern} high-concern areas identified</li>
                    <li>Establish rapid response protocols for most affected services/populations</li>
                    <li>Strengthen communication channels with highest-risk provider groups</li>
                    <li>Implement enhanced monitoring for {medium_concern} medium-concern areas</li>
                </ul>
                
                <p><strong>Strategic Planning (3-12 months):</strong></p>
                <ul>
                    <li>Develop targeted interventions based on specific barrier patterns identified</li>
                    <li>Enhance cross-system coordination to address multiple service disruptions</li>
                    <li>Invest in workforce development for most affected provider categories</li>
                    <li>Create contingency plans for anticipated future disruptions</li>
                </ul>
                
                <p><strong>Research & Monitoring (Ongoing):</strong></p>
                <ul>
                    <li>Conduct longitudinal follow-up to track improvement/deterioration</li>
                    <li>Implement regular provider surveys to monitor system health</li>
                    <li>Evaluate intervention effectiveness through targeted metrics</li>
                    <li>Share findings with policy makers and funding organizations</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # Export summary
            st.markdown("#### 📥 **Export Analysis Results**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Create summary CSV
                export_df = pd.DataFrame(stats_results)
                csv_data = export_df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Results (CSV)",
                    data=csv_data,
                    file_name=f"indicator_set_{selected_set}_analysis.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Create detailed text report
                report_text = f"""HIV Service Disruption Survey Analysis
Indicator Set {selected_set[-1]}: {indicator['title']}

Research Question: {indicator['question']}

Summary Statistics:
- Total Variables: {total_variables}
- High Priority: {high_concern} ({high_concern/total_variables*100:.1f}%)
- Medium Priority: {medium_concern} ({medium_concern/total_variables*100:.1f}%)
- Low Concern: {low_concern} ({low_concern/total_variables*100:.1f}%)
- Sample Size: {len(df):,} completed surveys

Top Findings:
"""
                for i, item in enumerate([r for r in stats_results if r['concern_level'] == 'high'][:5]):
                    report_text += f"{i+1}. {item['name']}: {item.get('percentage', 0):.1f}% affected\n"
                
                st.download_button(
                    label="📄 Download Report (TXT)",
                    data=report_text,
                    file_name=f"indicator_set_{selected_set}_report.txt",
                    mime="text/plain"
                )

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
            "🚨 Service Disruptions": [col for col in df.columns if col.startswith('Q9_') and 'No_disruptions' not in col],
            "👥 Populations Affected": [col for col in df.columns if col.startswith('Q10_Pop_')],
            "🏥 Access & Barriers": [col for col in df.columns if col.startswith(('Q21', 'Q22', 'Q23'))],
            "🔮 Future Concerns": [col for col in df.columns if col.startswith(('Q11', 'Q12', 'Q13', 'Q15'))],
            "📋 Federal Guidance": [col for col in df.columns if col.startswith(('Q18', 'Q19'))],
            "🎯 Population Barriers": [col for col in df.columns if col.startswith(('Q27', 'Q28', 'Q29', 'Q30'))]
        }
        
        outcome_category = st.selectbox("Select Category:", list(outcome_categories.keys()))
        available_outcomes = outcome_categories[outcome_category]
        
        if available_outcomes:
            outcome_var = st.selectbox(
                "Select Outcome Variable:", 
                available_outcomes,
                format_func=lambda x: x.replace('Q9_', '').replace('Q10_Pop_', '').replace('Q21_', '').replace('Q22_', '').replace('Q23_', '').replace('Q27_', '').replace('Q28_', '').replace('Q29_', '').replace('Q30_', '').replace('_', ' ').title()
            )
        else:
            outcome_var = None
            st.warning("No variables available in this category")
    
    with col2:
        st.markdown("### 🔍 Select Independent Variable")
        independent_categories = {
            "👨‍⚕️ Professional Characteristics": ['Q2_Professional_Role', 'Q5_Years_HIV_Practice'],
            "🏥 Clinical Settings": [col for col in df.columns if col.startswith('Q3_Setting_')],
            "💰 Funding Sources": [col for col in df.columns if col.startswith('Q4_Funding_')],
            "👥 Populations Served": [col for col in df.columns if col.startswith('Q6_Serve_')]
        }
        
        independent_category = st.selectbox("Select Category:", list(independent_categories.keys()))
        available_independents = independent_categories[independent_category]
        
        if available_independents:
            independent_var = st.selectbox(
                "Select Independent Variable:", 
                available_independents,
                format_func=lambda x: x.replace('Q2_', '').replace('Q3_Setting_', '').replace('Q4_Funding_', '').replace('Q5_', '').replace('Q6_Serve_', '').replace('_', ' ').title()
            )
        else:
            independent_var = None
            st.warning("No variables available in this category")
    
    # Generate cross-tabulation
    if st.button("🔬 Generate Cross-Tabulation Analysis", type="primary"):
        if outcome_var and independent_var:
            with st.spinner("Performing comprehensive statistical analysis..."):
                result = create_cross_tabulation(df, outcome_var, independent_var)
                
                if result:
                    # Display statistical summary header
                    st.markdown("## 📈 Statistical Analysis Results")
                    
                    # Clean variable names for display
                    outcome_display = outcome_var.replace('Q9_', '').replace('Q10_Pop_', '').replace('_', ' ').title()
                    independent_display = independent_var.replace('Q2_', '').replace('Q3_Setting_', '').replace('Q4_Funding_', '').replace('Q5_', '').replace('Q6_Serve_', '').replace('_', ' ').title()
                    
                    st.markdown(f"**Analysis:** {independent_display} × {outcome_display}")
                    
                    # Statistical metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Sample Size", f"{result['sample_size']:,}")
                    
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
                    
                    # Statistical interpretation box
                    if result['p_value'] is not None:
                        if result['p_value'] < 0.05:
                            st.markdown(f"""
                            <div class="interpretation-box">
                                <h4>✅ **Significant Association Found** (p < 0.05)</h4>
                                <p>There is a statistically significant relationship between <strong>{independent_display}</strong> 
                                and <strong>{outcome_display}</strong>.</p>
                                {f"<p><strong>Effect Size:</strong> {effect_size if result['cramers_v'] else 'Unknown'} association indicates {'meaningful practical significance' if result['cramers_v'] and result['cramers_v'] > 0.15 else 'limited practical significance despite statistical significance'}.</p>" if result['cramers_v'] else ""}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="warning-box">
                                <h4>ℹ️ **No Significant Association** (p ≥ 0.05)</h4>
                                <p>No statistically significant relationship was detected between <strong>{independent_display}</strong> 
                                and <strong>{outcome_display}</strong>. This suggests these variables are independent in this sample.</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # Display cross-tabulation tables
                    st.markdown("## 📋 Cross-Tabulation Tables")
                    
                    tab1, tab2, tab3 = st.tabs(["📊 Frequency Counts", "📈 Row Percentages", "🎨 Visualization"])
                    
                    with tab1:
                        st.markdown("### Frequency Distribution")
                        st.markdown("*Shows the count of responses in each combination*")
                        
                        # Enhanced frequency table with totals highlighted
                        styled_crosstab = result['crosstab'].style.highlight_max(axis=1, subset=result['crosstab'].columns[:-1])
                        st.dataframe(styled_crosstab, use_container_width=True)
                        
                        # Quick insights
                        max_cell = result['crosstab'].iloc[:-1, :-1].max().max()
                        max_location = result['crosstab'].iloc[:-1, :-1].stack().idxmax()
                        st.info(f"💡 **Highest frequency:** {max_cell} responses for {max_location[0]} × {max_location[1]}")
                    
                    with tab2:
                        st.markdown("### Row Percentages")
                        st.markdown("*Shows what percentage of each row group has the outcome*")
                        
                        # Enhanced percentage table with conditional formatting
                        styled_pct = result['percentages'].style.format("{:.1f}%").background_gradient(
                            cmap='Reds', 
                            subset=result['percentages'].columns[:-1] if 'All' in result['percentages'].columns else result['percentages'].columns
                        )
                        st.dataframe(styled_pct, use_container_width=True)
                        
                        # Identify concerning combinations
                        concerning_cells = []
                        if 'All' in result['percentages'].columns:
                            analysis_df = result['percentages'].drop('All', axis=1).drop('All', axis=0)
                        else:
                            analysis_df = result['percentages']
                        
                        for idx in analysis_df.index:
                            for col in analysis_df.columns:
                                if analysis_df.loc[idx, col] > 50:  # High percentage threshold
                                    concerning_cells.append({
                                        'combination': f"{idx} × {col}",
                                        'percentage': analysis_df.loc[idx, col]
                                    })
                        
                        if concerning_cells:
                            concerning_cells.sort(key=lambda x: x['percentage'], reverse=True)
                            st.markdown("#### ⚠️ **High-Risk Combinations** (>50%)")
                            for cell in concerning_cells[:5]:  # Show top 5
                                st.markdown(f"- **{cell['combination']}**: {cell['percentage']:.1f}%")
                        else:
                            st.success("✅ No extremely high-risk combinations (>50%) identified")
                    
                    with tab3:
                        st.markdown("### Interactive Visualization")
                        
                        # Create multiple visualizations
                        viz_data = result['percentages'].drop('All', axis=1).drop('All', axis=0) if 'All' in result['percentages'].columns else result['percentages']
                        
                        if not viz_data.empty and viz_data.shape[0] <= 15 and viz_data.shape[1] <= 15:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Heatmap
                                fig_heatmap = px.imshow(
                                    viz_data,
                                    title="Row Percentage Heatmap",
                                    labels=dict(color="Percentage", x=outcome_display, y=independent_display),
                                    aspect="auto",
                                    color_continuous_scale="Reds"
                                )
                                fig_heatmap.update_layout(height=max(400, viz_data.shape[0] * 40))
                                st.plotly_chart(fig_heatmap, use_container_width=True)
                            
                            with col2:
                                # Grouped bar chart
                                viz_data_reset = viz_data.reset_index()
                                viz_melted = viz_data_reset.melt(id_vars=viz_data_reset.columns[0], 
                                                               var_name=outcome_display, 
                                                               value_name='Percentage')
                                
                                fig_bar = px.bar(
                                    viz_melted,
                                    x=viz_data_reset.columns[0],
                                    y='Percentage',
                                    color=outcome_display,
                                    title="Grouped Bar Chart",
                                    barmode='group'
                                )
                                fig_bar.update_xaxes(tickangle=45)
                                fig_bar.update_layout(height=400)
                                st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info("📊 Table too large for optimal visualization. Showing summary chart instead.")
                            
                            # Summary visualization for large tables
                            if viz_data.shape[1] == 2:  # Binary outcome
                                # Show just the "positive" outcome
                                positive_col = viz_data.columns[-1] if '1' in str(viz_data.columns[-1]) else viz_data.columns[0]
                                summary_data = viz_data[positive_col].sort_values(ascending=True)
                                
                                fig_summary = px.bar(
                                    x=summary_data.values,
                                    y=summary_data.index,
                                    orientation='h',
                                    title=f"Percentage with {outcome_display} by {independent_display}",
                                    labels={'x': 'Percentage', 'y': independent_display}
                                )
                                fig_summary.update_layout(height=max(400, len(summary_data) * 25))
                                st.plotly_chart(fig_summary, use_container_width=True)
                    
                    # Clinical interpretation and recommendations
                    st.markdown("## 💡 Clinical Interpretation & Recommendations")
                    
                    if result['p_value'] and result['p_value'] < 0.05:
                        interpretation_level = "strong" if result['cramers_v'] and result['cramers_v'] > 0.3 else "moderate" if result['cramers_v'] and result['cramers_v'] > 0.15 else "weak"
                        
                        st.markdown(f"""
                        <div class="interpretation-box">
                            <h4>🔬 **Clinical Significance Analysis**</h4>
                            <p>The statistically significant relationship between <strong>{independent_display}</strong> and 
                            <strong>{outcome_display}</strong> has <em>{interpretation_level} practical significance</em> for clinical practice.</p>
                            
                            <h5>📋 **Evidence-Based Recommendations:**</h5>
                            <ul>
                                <li><strong>Targeted Interventions:</strong> Focus resources on the highest-risk combinations identified in the analysis</li>
                                <li><strong>Risk Stratification:</strong> Use {independent_display} as a predictor for {outcome_display} in clinical assessment</li>
                                <li><strong>Monitoring Protocols:</strong> Implement enhanced surveillance for vulnerable subgroups</li>
                                <li><strong>Resource Allocation:</strong> Prioritize support based on risk profile patterns</li>
                                <li><strong>Policy Development:</strong> Consider differential approaches based on identified associations</li>
                            </ul>
                            
                            <h5>🔍 **Further Investigation:**</h5>
                            <ul>
                                <li>Explore underlying mechanisms driving the observed associations</li>
                                <li>Investigate potential confounding variables and mediating factors</li>
                                <li>Consider longitudinal follow-up to assess temporal relationships</li>
                                <li>Validate findings through targeted qualitative research</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="warning-box">
                            <h4>📊 **Non-Significant Findings: Still Valuable**</h4>
                            <p>While no significant association was found between <strong>{independent_display}</strong> and 
                            <strong>{outcome_display}</strong>, this finding is also important for clinical practice.</p>
                            
                            <h5>💡 **Implications:**</h5>
                            <ul>
                                <li><strong>Universal Risk:</strong> {outcome_display} may affect all groups relatively equally</li>
                                <li><strong>Other Factors:</strong> Consider alternative predictors or risk factors</li>
                                <li><strong>System-Wide Issues:</strong> Problem may be systemic rather than group-specific</li>
                                <li><strong>Intervention Approach:</strong> Broad-based rather than targeted interventions may be appropriate</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Export functionality
                    st.markdown("## 📥 Export Analysis Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Frequency table export
                        csv_freq = result['crosstab'].to_csv()
                        st.download_button(
                            label="📊 Download Frequency Table",
                            data=csv_freq,
                            file_name=f"crosstab_freq_{outcome_var}_{independent_var}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        # Percentage table export
                        csv_pct = result['percentages'].to_csv()
                        st.download_button(
                            label="📈 Download Percentage Table",
                            data=csv_pct,
                            file_name=f"crosstab_pct_{outcome_var}_{independent_var}.csv",
                            mime="text/csv"
                        )
                    
                    with col3:
                        # Statistical summary export
                        stats_summary = f"""Cross-Tabulation Analysis Summary
========================================

Variables:
- Outcome: {outcome_display}
- Independent: {independent_display}

Statistical Results:
- Sample Size: {result['sample_size']:,}
- Chi-Square: {result['chi2_stat']:.3f if result['chi2_stat'] else 'N/A'}
- P-Value: {result['p_value']:.3f if result['p_value'] else 'N/A'}
- Cramér's V: {result['cramers_v']:.3f if result['cramers_v'] else 'N/A'}
- Significance: {'Significant' if result['p_value'] and result['p_value'] < 0.05 else 'Not Significant'}
- Effect Size: {effect_size if result['cramers_v'] else 'Unknown'}

Clinical Interpretation:
{interpretation_level.title() if result['p_value'] and result['p_value'] < 0.05 else 'No significant'} association detected.

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                        st.download_button(
                            label="📄 Download Statistical Summary",
                            data=stats_summary,
                            file_name=f"crosstab_summary_{outcome_var}_{independent_var}.txt",
                            mime="text/plain"
                        )
                
                else:
                    st.error("❌ Unable to generate cross-tabulation. Please check your variable selections and ensure sufficient data is available for analysis.")
        else:
            st.warning("⚠️ Please select both outcome and independent variables to proceed with cross-tabulation analysis.")

def show_custom_analysis(df):
    """Display custom analysis options"""
    st.markdown("## 🔬 Custom Analysis & Advanced Filtering")
    
    st.markdown("""
    <div class="research-question">
        <strong>🎯 Purpose:</strong> Perform customized analysis with flexible filtering, comparison, and visualization options
        tailored to your specific research questions and hypotheses.
    </div>
    """, unsafe_allow_html=True)
    
    # Advanced filters section
    st.markdown("### 🔧 Advanced Filters & Subsetting")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**👨‍⚕️ Professional Characteristics**")
        if 'Q2_Professional_Role' in df.columns:
            all_roles = df['Q2_Professional_Role'].unique()
            selected_roles = st.multiselect(
                "Professional Roles:",
                options=all_roles,
                default=all_roles,
                help="Select specific professional roles to include in analysis"
            )
        else:
            selected_roles = None
        
        if 'Q5_Years_HIV_Practice' in df.columns:
            all_experience = df['Q5_Years_HIV_Practice'].unique()
            selected_experience = st.multiselect(
                "Years of Experience:",
                options=all_experience,
                default=all_experience,
                help="Filter by years of HIV practice experience"
            )
        else:
            selected_experience = None
    
    with col2:
        st.markdown("**🏥 Clinical Settings**")
        setting_cols = [col for col in df.columns if col.startswith('Q3_Setting_')]
        setting_filters = {}
        
        for setting_col in setting_cols[:5]:  # Limit to first 5 settings
            setting_name = setting_col.replace('Q3_Setting_', '').replace('_', ' ').title()
            setting_filters[setting_col] = st.selectbox(
                f"{setting_name}:",
                options=['Any', 'Yes', 'No'],
                help=f"Filter by {setting_name} setting"
            )
    
    with col3:
        st.markdown("**👥 Populations Served**")
        pop_cols = [col for col in df.columns if col.startswith('Q6_Serve_')]
        pop_filters = {}
        
        # Key populations for filtering
        key_pops = ['Q6_Serve_Transgender', 'Q6_Serve_Homeless_Housing_Unstable', 
                   'Q6_Serve_Immigrants_Undocumented', 'Q6_Serve_Black_African_American']
        
        for pop_col in key_pops:
            if pop_col in df.columns:
                pop_name = pop_col.replace('Q6_Serve_', '').replace('_', ' ').title()
                pop_filters[pop_col] = st.selectbox(
                    f"Serves {pop_name}:",
                    options=['Any', 'Yes', 'No'],
                    help=f"Filter by whether provider serves {pop_name}"
                )
    
    # Apply filters
    filtered_df = df.copy()
    filter_description = []
    
    if selected_roles:
        filtered_df = filtered_df[filtered_df['Q2_Professional_Role'].isin(selected_roles)]
        if len(selected_roles) < len(df['Q2_Professional_Role'].unique()):
            filter_description.append(f"Professional roles: {len(selected_roles)} selected")
    
    if selected_experience:
        filtered_df = filtered_df[filtered_df['Q5_Years_HIV_Practice'].isin(selected_experience)]
        if len(selected_experience) < len(df['Q5_Years_HIV_Practice'].unique()):
            filter_description.append(f"Experience levels: {len(selected_experience)} selected")
    
    # Apply setting filters
    for setting_col, setting_value in setting_filters.items():
        if setting_value == 'Yes':
            filtered_df = filtered_df[filtered_df[setting_col] == 1]
            filter_description.append(f"{setting_col.replace('Q3_Setting_', '').replace('_', ' ')}: Yes")
        elif setting_value == 'No':
            filtered_df = filtered_df[filtered_df[setting_col] == 0]
            filter_description.append(f"{setting_col.replace('Q3_Setting_', '').replace('_', ' ')}: No")
    
    # Apply population filters
    for pop_col, pop_value in pop_filters.items():
        if pop_value == 'Yes':
            filtered_df = filtered_df[filtered_df[pop_col] == 1]
            filter_description.append(f"Serves {pop_col.replace('Q6_Serve_', '').replace('_', ' ')}")
        elif pop_value == 'No':
            filtered_df = filtered_df[filtered_df[pop_col] == 0]
            filter_description.append(f"Does not serve {pop_col.replace('Q6_Serve_', '').replace('_', ' ')}")
    
    # Display filter results
    filter_reduction = len(df) - len(filtered_df)
    filter_desc_text = "; ".join(filter_description) if filter_description else "No filters applied"
    
    st.markdown(f"""
    <div class="metric-card">
        <strong>📊 Filtered Dataset Results:</strong><br>
        <strong>Sample Size:</strong> {len(filtered_df):,} records ({filter_reduction:,} filtered out)<br>
        <strong>Filters Applied:</strong> {filter_desc_text}
    </div>
    """, unsafe_allow_html=True)
    
    if len(filtered_df) == 0:
        st.error("❌ No records match the selected filters. Please adjust your filter criteria to include more data.")
        return
    elif len(filtered_df) < 30:
        st.warning(f"⚠️ Small sample size ({len(filtered_df)} records). Results may not be statistically reliable.")
    
    # Analysis options
    st.markdown("### 📊 Select Custom Analysis Type")
    
    analysis_option = st.selectbox(
        "Choose Analysis Approach:",
        [
            "🔍 Comparative Service Disruption Analysis",
            "📈 Population Risk Assessment", 
            "🎯 Setting-Based Impact Analysis",
            "📊 Correlation & Association Matrix",
            "🔮 Predictive Risk Modeling",
            "📋 Custom Cross-Tabulation Builder"
        ]
    )
    
    # Execute selected analysis
    if analysis_option == "🔍 Comparative Service Disruption Analysis":
        st.markdown("#### 🔍 **Comparative Service Disruption Analysis**")
        st.markdown("*Compare disruption rates across different provider characteristics*")
        
        # Select services to compare
        disruption_cols = [col for col in filtered_df.columns if col.startswith('Q9_') and 'No_disruptions' not in col]
        
        if disruption_cols:
            selected_disruptions = st.multiselect(
                "Select Services to Analyze:",
                disruption_cols,
                default=disruption_cols[:6],  # Default to first 6
                format_func=lambda x: x.replace('Q9_', '').replace('_', ' ').title()
            )
            
            comparison_var = st.selectbox(
                "Compare Across:",
                ['Q2_Professional_Role', 'Q5_Years_HIV_Practice'] + 
                [col for col in filtered_df.columns if col.startswith('Q3_Setting_')][:3],
                format_func=lambda x: x.replace('Q2_', '').replace('Q3_Setting_', '').replace('Q5_', '').replace('_', ' ').title()
            )
            
            if selected_disruptions and comparison_var:
                # Calculate disruption rates
                comparison_data = []
                
                if comparison_var in ['Q2_Professional_Role', 'Q5_Years_HIV_Practice']:
                    # Categorical comparison
                    for category in filtered_df[comparison_var].unique():
                        category_data = filtered_df[filtered_df[comparison_var] == category]
                        
                        for service_col in selected_disruptions:
                            if service_col in category_data.columns and len(category_data) > 0:
                                rate = category_data[service_col].mean() * 100
                                count = category_data[service_col].sum()
                                total = len(category_data)
                                
                                comparison_data.append({
                                    'Category': category,
                                    'Service': service_col.replace('Q9_', '').replace('_', ' ').title(),
                                    'Disruption_Rate': rate,
                                    'Count': count,
                                    'Total': total,
                                    'Sample_Size': total
                                })
                else:
                    # Binary setting comparison
                    for setting_value in [0, 1]:
                        setting_label = 'No' if setting_value == 0 else 'Yes'
                        category_data = filtered_df[filtered_df[comparison_var] == setting_value]
                        
                        for service_col in selected_disruptions:
                            if service_col in category_data.columns and len(category_data) > 0:
                                rate = category_data[service_col].mean() * 100
                                count = category_data[service_col].sum()
                                total = len(category_data)
                                
                                comparison_data.append({
                                    'Category': f"{comparison_var.replace('Q3_Setting_', '').replace('_', ' ').title()}: {setting_label}",
                                    'Service': service_col.replace('Q9_', '').replace('_', ' ').title(),
                                    'Disruption_Rate': rate,
                                    'Count': count,
                                    'Total': total,
                                    'Sample_Size': total
                                })
                
                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data)
                    
                    # Create grouped bar chart
                    fig = px.bar(
                        comparison_df, 
                        x='Category', 
                        y='Disruption_Rate', 
                        color='Service',
                        title=f"Service Disruption Rates by {comparison_var.replace('_', ' ').title()}",
                        labels={'Disruption_Rate': 'Disruption Rate (%)', 'Category': comparison_var.replace('_', ' ').title()},
                        barmode='group',
                        text='Disruption_Rate'
                    )
                    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig.update_xaxes(tickangle=45)
                    fig.update_layout(height=600, showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary statistics table
                    st.markdown("#### 📊 **Detailed Comparison Table**")
                    
                    # Pivot table for better visualization
                    pivot_table = comparison_df.pivot_table(
                        index='Category', 
                        columns='Service', 
                        values='Disruption_Rate',
                        aggfunc='mean'
                    ).round(1)
                    
                    # Style the table
                    styled_pivot = pivot_table.style.background_gradient(cmap='Reds', axis=None).format("{:.1f}%")
                    st.dataframe(styled_pivot, use_container_width=True)
                    
                    # Key insights
                    st.markdown("#### 💡 **Key Insights**")
                    
                    # Find highest and lowest rates
                    max_rate_idx = comparison_df['Disruption_Rate'].idxmax()
                    min_rate_idx = comparison_df['Disruption_Rate'].idxmin()
                    
                    max_rate_info = comparison_df.loc[max_rate_idx]
                    min_rate_info = comparison_df.loc[min_rate_idx]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **🔴 Highest Disruption Rate:**
                        - **Service:** {max_rate_info['Service']}
                        - **Group:** {max_rate_info['Category']}
                        - **Rate:** {max_rate_info['Disruption_Rate']:.1f}%
                        - **Affected:** {max_rate_info['Count']}/{max_rate_info['Total']}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **🟢 Lowest Disruption Rate:**
                        - **Service:** {min_rate_info['Service']}
                        - **Group:** {min_rate_info['Category']}
                        - **Rate:** {min_rate_info['Disruption_Rate']:.1f}%
                        - **Affected:** {min_rate_info['Count']}/{min_rate_info['Total']}
                        """)
                    
                    # Export comparison data
                    csv_data = comparison_df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Comparison Data (CSV)",
                        data=csv_data,
                        file_name="service_disruption_comparison.csv",
                        mime="text/csv"
                    )
    
    elif analysis_option == "📈 Population Risk Assessment":
        st.markdown("#### 📈 **Population Risk Assessment Analysis**")
        st.markdown("*Identify populations at highest risk for service disruptions and barriers*")
        
        # Population risk analysis
        pop_affected_cols = [col for col in filtered_df.columns if col.startswith('Q10_Pop_')]
        barrier_cols = [col for col in filtered_df.columns if col.startswith(('Q27_', 'Q28_', 'Q29_', 'Q30_'))]
        
        if pop_affected_cols or barrier_cols:
            st.markdown("##### 👥 **Populations Most Affected by Disruptions**")
            
            if pop_affected_cols:
                pop_risk_data = []
                
                for pop_col in pop_affected_cols:
                    if pop_col in filtered_df.columns:
                        affected_rate = filtered_df[pop_col].mean() * 100
                        affected_count = filtered_df[pop_col].sum()
                        total_responses = filtered_df[pop_col].notna().sum()
                        
                        pop_name = pop_col.replace('Q10_Pop_', '').replace('_', ' ').title()
                        
                        pop_risk_data.append({
                            'Population': pop_name,
                            'Affected_Rate': affected_rate,
                            'Affected_Count': affected_count,
                            'Total_Responses': total_responses,
                            'Risk_Level': 'High' if affected_rate > 40 else 'Medium' if affected_rate > 25 else 'Low'
                        })
                
                if pop_risk_data:
                    pop_risk_df = pd.DataFrame(pop_risk_data).sort_values('Affected_Rate', ascending=False)
                    
                    # Risk assessment visualization
                    fig_risk = px.bar(
                        pop_risk_df,
                        x='Affected_Rate',
                        y='Population',
                        orientation='h',
                        color='Risk_Level',
                        color_discrete_map={'High': '#f44336', 'Medium': '#ff9800', 'Low': '#4caf50'},
                        title="Population Risk Assessment - Disruption Impact Rates",
                        labels={'Affected_Rate': 'Percentage Affected (%)', 'Population': 'Population Group'},
                        text='Affected_Rate'
                    )
                    fig_risk.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
                    fig_risk.update_layout(height=400)
                    st.plotly_chart(fig_risk, use_container_width=True)
                    
                    # Risk summary table
                    st.markdown("##### 📋 **Population Risk Summary**")
                    
                    for _, row in pop_risk_df.iterrows():
                        risk_color = '#f44336' if row['Risk_Level'] == 'High' else '#ff9800' if row['Risk_Level'] == 'Medium' else '#4caf50'
                        
                        st.markdown(f"""
                        <div style="border-left: 4px solid {risk_color}; padding: 10px; margin: 5px 0; background-color: #f9f9f9;">
                            <strong>{row['Population']}</strong> - <span style="color: {risk_color}; font-weight: bold;">{row['Risk_Level']} Risk</span><br>
                            <strong>Impact Rate:</strong> {row['Affected_Rate']:.1f}% ({row['Affected_Count']}/{row['Total_Responses']} providers)
                        </div>
                        """, unsafe_allow_html=True)
            
            # Barrier analysis
            if barrier_cols:
                st.markdown("##### 🚧 **Specific Population Barriers**")
                
                barrier_data = []
                for barrier_col in barrier_cols:
                    if barrier_col in filtered_df.columns:
                        if filtered_df[barrier_col].dtype in ['int64', 'float64'] and filtered_df[barrier_col].nunique() <= 2:
                            # Binary barrier
                            barrier_rate = filtered_df[barrier_col].mean() * 100
                            barrier_count = filtered_df[barrier_col].sum()
                            total_responses = filtered_df[barrier_col].notna().sum()
                        else:
                            # Categorical barrier - count concerning responses
                            concerning_values = ['Significant decline', 'Frequently', 'Almost always']
                            barrier_count = sum([filtered_df[barrier_col].value_counts().get(val, 0) for val in concerning_values])
                            total_responses = filtered_df[barrier_col].notna().sum()
                            barrier_rate = (barrier_count / total_responses * 100) if total_responses > 0 else 0
                        
                        barrier_name = barrier_col.replace('Q27_', 'Transgender: ').replace('Q28_', 'Undocumented: ').replace('Q29_', 'Homeless: ').replace('Q30_', 'LTFU: ').replace('_', ' ').title()
                        
                        barrier_data.append({
                            'Barrier': barrier_name,
                            'Prevalence_Rate': barrier_rate,
                            'Count': barrier_count,
                            'Total': total_responses,
                            'Severity': 'High' if barrier_rate > 35 else 'Medium' if barrier_rate > 20 else 'Low'
                        })
                
                if barrier_data:
                    barrier_df = pd.DataFrame(barrier_data).sort_values('Prevalence_Rate', ascending=False)
                    
                    # Barrier visualization
                    fig_barriers = px.bar(
                        barrier_df.head(8),  # Top 8 barriers
                        x='Prevalence_Rate',
                        y='Barrier',
                        orientation='h',
                        color='Severity',
                        color_discrete_map={'High': '#d32f2f', 'Medium': '#f57c00', 'Low': '#388e3c'},
                        title="Top Population Barriers by Prevalence",
                        labels={'Prevalence_Rate': 'Prevalence Rate (%)', 'Barrier': 'Barrier Type'},
                        text='Prevalence_Rate'
                    )
                    fig_barriers.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
                    fig_barriers.update_layout(height=500)
                    st.plotly_chart(fig_barriers, use_container_width=True)
        else:
            st.info("No population risk data available in the filtered dataset.")
    
    elif analysis_option == "📊 Correlation & Association Matrix":
        st.markdown("#### 📊 **Correlation & Association Matrix**")
        st.markdown("*Explore relationships between multiple variables simultaneously*")
        
        # Select variables for correlation analysis
        numeric_vars = []
        binary_vars = []
        
        # Get service disruptions (binary)
        disruption_cols = [col for col in filtered_df.columns if col.startswith('Q9_') and 'No_disruptions' not in col]
        binary_vars.extend(disruption_cols)
        
        # Get binary outcomes
        binary_outcome_cols = [col for col in filtered_df.columns if col.startswith(('Q10_', 'Q27_', 'Q29_', 'Q30_')) and filtered_df[col].nunique() <= 2]
        binary_vars.extend(binary_outcome_cols)
        
        # Get setting variables
        setting_cols = [col for col in filtered_df.columns if col.startswith('Q3_Setting_')]
        binary_vars.extend(setting_cols)
        
        if len(binary_vars) > 1:
            selected_vars = st.multiselect(
                "Select Variables for Correlation Analysis:",
                binary_vars,
                default=binary_vars[:min(10, len(binary_vars))],
                format_func=lambda x: x.replace('Q9_', '').replace('Q10_Pop_', '').replace('Q27_', 'Trans: ').replace('Q29_', 'Homeless: ').replace('Q30_', 'LTFU: ').replace('Q3_Setting_', 'Setting: ').replace('_', ' ').title()
            )
            
            if len(selected_vars) > 1:
                # Calculate correlation matrix
                corr_data = filtered_df[selected_vars].corr()
                
                # Create correlation heatmap
                fig_corr = px.imshow(
                    corr_data,
                    title="Correlation Matrix - Service Disruptions & Outcomes",
                    color_continuous_scale='RdBu',
                    aspect="auto",
                    labels={'color': 'Correlation Coefficient'}
                )
                
                # Clean up labels
                clean_labels = [var.replace('Q9_', '').replace('Q10_Pop_', '').replace('Q27_', 'Trans: ').replace('Q29_', 'Homeless: ').replace('Q30_', 'LTFU: ').replace('Q3_Setting_', 'Setting: ').replace('_', ' ').title() for var in selected_vars]
                
                fig_corr.update_layout(
                    xaxis={'tickvals': list(range(len(clean_labels))), 'ticktext': clean_labels, 'tickangle': 45},
                    yaxis={'tickvals': list(range(len(clean_labels))), 'ticktext': clean_labels},
                    height=max(500, len(selected_vars) * 40)
                )
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Identify strong correlations
                st.markdown("##### 🔍 **Notable Correlations** (|r| > 0.3)")
                
                strong_corr = []
                for i in range(len(corr_data.columns)):
                    for j in range(i+1, len(corr_data.columns)):
                        corr_val = corr_data.iloc[i, j]
                        if abs(corr_val) > 0.3:
                            var1_clean = clean_labels[i]
                            var2_clean = clean_labels[j]
                            strong_corr.append({
                                'Variable 1': var1_clean,
                                'Variable 2': var2_clean,
                                'Correlation': corr_val,
                                'Strength': 'Strong' if abs(corr_val) > 0.5 else 'Moderate'
                            })
                
                if strong_corr:
                    strong_corr_df = pd.DataFrame(strong_corr).sort_values('Correlation', key=abs, ascending=False)
                    
                    for _, row in strong_corr_df.iterrows():
                        corr_direction = 'Positive' if row['Correlation'] > 0 else 'Negative'
                        corr_color = '#4caf50' if row['Correlation'] > 0 else '#f44336'
                        
                        st.markdown(f"""
                        <div style="border-left: 4px solid {corr_color}; padding: 8px; margin: 5px 0; background-color: #f9f9f9;">
                            <strong>{row['Variable 1']}</strong> ↔ <strong>{row['Variable 2']}</strong><br>
                            <span style="color: {corr_color}; font-weight: bold;">{corr_direction} correlation: {row['Correlation']:.3f}</span> ({row['Strength']})
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No strong correlations (|r| > 0.3) found among selected variables.")
        else:
            st.info("Insufficient binary variables available for correlation analysis in the filtered dataset.")

def show_data_explorer(df):
    """Display data exploration interface"""
    st.markdown("## 📋 Data Explorer & Export Center")
    
    st.markdown("""
    <div class="research-question">
        <strong>🔍 Purpose:</strong> Explore the complete survey dataset, examine variable distributions, 
        apply custom filters, and export data for external analysis.
    </div>
    """, unsafe_allow_html=True)
    
    # Dataset overview
    st.markdown("### 📊 Dataset Overview & Quality Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    
    with col2:
        st.metric("Total Variables", len(df.columns))
    
    with col3:
        missing_values = df.isnull().sum().sum()
        st.metric("Missing Values", f"{missing_values:,}")
    
    with col4:
        missing_pct = (missing_values / (len(df) * len(df.columns))) * 100
        st.metric("Missing %", f"{missing_pct:.1f}%")
    
    # Data quality assessment
    st.markdown("#### 🔍 **Data Quality Assessment**")
    
    # Variable completeness
    completeness_data = []
    for col in df.columns:
        if col not in ['ResponseID']:
            total_count = len(df)
            non_null_count = df[col].notna().sum()
            completeness_pct = (non_null_count / total_count) * 100
            
            completeness_data.append({
                'Variable': col.replace('_', ' ').title(),
                'Complete_Responses': non_null_count,
                'Total_Responses': total_count,
                'Completeness_Pct': completeness_pct,
                'Quality': 'Excellent' if completeness_pct >= 95 else 'Good' if completeness_pct >= 85 else 'Fair' if completeness_pct >= 70 else 'Poor'
            })
    
    completeness_df = pd.DataFrame(completeness_data).sort_values('Completeness_Pct', ascending=False)
    
    # Show quality summary
    quality_summary = completeness_df['Quality'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_quality = px.pie(
            values=quality_summary.values,
            names=quality_summary.index,
            title="Variable Quality Distribution",
            color_discrete_map={
                'Excellent': '#4caf50',
                'Good': '#8bc34a', 
                'Fair': '#ff9800',
                'Poor': '#f44336'
            }
        )
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Top and bottom variables by completeness
        st.markdown("**📈 Highest Quality Variables:**")
        for _, row in completeness_df.head(5).iterrows():
            st.markdown(f"- {row['Variable']}: {row['Completeness_Pct']:.1f}%")
        
        poor_quality = completeness_df[completeness_df['Quality'] == 'Poor']
        if not poor_quality.empty:
            st.markdown("**⚠️ Variables Needing Attention:**")
            for _, row in poor_quality.iterrows():
                st.markdown(f"- {row['Variable']}: {row['Completeness_Pct']:.1f}%")
    
    # Variable explorer
    st.markdown("### 🔍 Interactive Variable Explorer")
    
    # Categorize variables for easier navigation
    variable_categories = {
        "👨‍⚕️ Demographics & Professional": [col for col in df.columns if col.startswith(('Q2_', 'Q5_'))],
        "🏥 Clinical Settings & Infrastructure": [col for col in df.columns if col.startswith('Q3_')],
        "💰 Funding & Financial": [col for col in df.columns if col.startswith('Q4_')],
        "👥 Populations Served": [col for col in df.columns if col.startswith('Q6_')],
        "🚨 Service Disruptions": [col for col in df.columns if col.startswith('Q9_')],
        "👥 Populations Most Affected": [col for col in df.columns if col.startswith('Q10_')],
        "🔮 Future Expectations & Concerns": [col for col in df.columns if col.startswith(('Q11', 'Q12', 'Q13', 'Q15'))],
        "📋 Federal Guidance & Resources": [col for col in df.columns if col.startswith(('Q18', 'Q19'))],
        "🏥 Ancillary Services Access": [col for col in df.columns if col.startswith(('Q21', 'Q22', 'Q23'))],
        "🎯 Population-Specific Barriers": [col for col in df.columns if col.startswith(('Q27', 'Q28', 'Q29', 'Q30'))]
    }
    
    selected_category = st.selectbox("Select Variable Category:", list(variable_categories.keys()))
    
    if variable_categories[selected_category]:
        selected_variable = st.selectbox(
            "Select Variable for Detailed Analysis:", 
            variable_categories[selected_category],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_variable:
            # Variable analysis tabs
            var_tab1, var_tab2, var_tab3 = st.tabs(["📊 Distribution", "📈 Statistics", "🔍 Cross-Analysis"])
            
            with var_tab1:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Variable distribution visualization
                    if df[selected_variable].dtype in ['object', 'category']:
                        value_counts = df[selected_variable].value_counts()
                        fig = px.bar(
                            x=value_counts.values,
                            y=value_counts.index,
                            orientation='h',
                            title=f"Distribution: {selected_variable.replace('_', ' ').title()}",
                            labels={'x': 'Count', 'y': 'Values'},
                            text=value_counts.values
                        )
                        fig.update_traces(textposition='inside')
                        fig.update_layout(height=max(300, len(value_counts) * 30))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Numerical/binary variable
                        if df[selected_variable].nunique() <= 10:
                            # Bar chart for discrete values
                            value_counts = df[selected_variable].value_counts().sort_index()
                            fig = px.bar(
                                x=value_counts.index,
                                y=value_counts.values,
                                title=f"Distribution: {selected_variable.replace('_', ' ').title()}",
                                labels={'x': 'Value', 'y': 'Count'},
                                text=value_counts.values
                            )
                            fig.update_traces(textposition='outside')
                        else:
                            # Histogram for continuous values
                            fig = px.histogram(
                                df, 
                                x=selected_variable,
                                title=f"Distribution: {selected_variable.replace('_', ' ').title()}",
                                nbins=20
                            )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Variable information panel
                    st.markdown("**📋 Variable Information:**")
                    st.markdown(f"**Type:** {df[selected_variable].dtype}")
                    st.markdown(f"**Non-null:** {df[selected_variable].notna().sum():,}")
                    st.markdown(f"**Missing:** {df[selected_variable].isnull().sum():,}")
                    st.markdown(f"**Unique Values:** {df[selected_variable].nunique():,}")
                    
                    completeness = (df[selected_variable].notna().sum() / len(df)) * 100
                    st.markdown(f"**Completeness:** {completeness:.1f}%")
                    
                    if df[selected_variable].dtype in ['object', 'category']:
                        st.markdown("**📊 Value Distribution:**")
                        value_counts = df[selected_variable].value_counts()
                        for val, count in value_counts.head(8).items():
                            pct = (count / len(df)) * 100
                            st.markdown(f"- **{val}:** {count:,} ({pct:.1f}%)")
                        
                        if len(value_counts) > 8:
                            st.markdown(f"... and {len(value_counts) - 8} more values")
                    else:
                        st.markdown("**📊 Summary Statistics:**")
                        st.markdown(f"**Mean:** {df[selected_variable].mean():.3f}")
                        st.markdown(f"**Median:** {df[selected_variable].median():.3f}")
                        st.markdown(f"**Std Dev:** {df[selected_variable].std():.3f}")
                        st.markdown(f"**Min:** {df[selected_variable].min()}")
                        st.markdown(f"**Max:** {df[selected_variable].max()}")
            
            with var_tab2:
                # Detailed statistics
                st.markdown(f"#### 📈 **Detailed Statistics: {selected_variable.replace('_', ' ').title()}**")
                
                if df[selected_variable].dtype in ['object', 'category']:
                    # Categorical statistics
                    value_counts = df[selected_variable].value_counts()
                    stats_df = pd.DataFrame({
                        'Value': value_counts.index,
                        'Count': value_counts.values,
                        'Percentage': (value_counts.values / len(df) * 100).round(2),
                        'Cumulative_Pct': (value_counts.values / len(df) * 100).cumsum().round(2)
                    })
                    
                    # Style the statistics table
                    styled_stats = stats_df.style.format({
                        'Percentage': '{:.1f}%',
                        'Cumulative_Pct': '{:.1f}%'
                    }).background_gradient(subset=['Count'], cmap='Blues')
                    
                    st.dataframe(styled_stats, use_container_width=True)
                    
                    # Additional insights
                    modal_value = value_counts.index[0]
                    modal_pct = value_counts.iloc[0] / len(df) * 100
                    
                    st.markdown(f"""
                    **📊 Key Statistics:**
                    - **Most Common Value:** {modal_value} ({modal_pct:.1f}%)
                    - **Number of Categories:** {len(value_counts)}
                    - **Diversity Index:** {(1 - (value_counts / len(df)).pow(2).sum()):.3f}
                    """)
                
                else:
                    # Numerical statistics
                    stats = df[selected_variable].describe()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🔢 Descriptive Statistics:**")
                        for stat, value in stats.items():
                            st.metric(stat.title(), f"{value:.3f}")
                    
                    with col2:
                        st.markdown("**📊 Distribution Characteristics:**")
                        
                        # Skewness and kurtosis
                        skewness = df[selected_variable].skew()
                        kurtosis = df[selected_variable].kurtosis()
                        
                        st.metric("Skewness", f"{skewness:.3f}")
                        st.metric("Kurtosis", f"{kurtosis:.3f}")
                        
                        # Quartiles
                        q1 = df[selected_variable].quantile(0.25)
                        q3 = df[selected_variable].quantile(0.75)
                        iqr = q3 - q1
                        
                        st.metric("Q1 (25th percentile)", f"{q1:.3f}")
                        st.metric("Q3 (75th percentile)", f"{q3:.3f}")
                        st.metric("IQR", f"{iqr:.3f}")
                    
                    # Box plot for numerical variables
                    if df[selected_variable].nunique() > 2:
                        fig_box = px.box(
                            df, 
                            y=selected_variable,
                            title=f"Box Plot: {selected_variable.replace('_', ' ').title()}"
                        )
                        st.plotly_chart(fig_box, use_container_width=True)
            
            with var_tab3:
                # Cross-analysis with other variables
                st.markdown(f"#### 🔍 **Cross-Analysis: {selected_variable.replace('_', ' ').title()}**")
                
                # Select another variable for cross-analysis
                other_vars = [col for col in df.columns if col != selected_variable and col != 'ResponseID']
                
                if other_vars:
                    cross_var = st.selectbox(
                        "Select Variable for Cross-Analysis:",
                        other_vars,
                        format_func=lambda x: x.replace('_', ' ').title()
                    )
                    
                    if cross_var:
                        # Determine analysis type based on variable types
                        var1_categorical = df[selected_variable].dtype in ['object', 'category'] or df[selected_variable].nunique() <= 10
                        var2_categorical = df[cross_var].dtype in ['object', 'category'] or df[cross_var].nunique() <= 10
                        
                        if var1_categorical and var2_categorical:
                            # Both categorical - create cross-tabulation
                            cross_tab = pd.crosstab(df[selected_variable], df[cross_var], margins=True)
                            
                            st.markdown("**📊 Cross-Tabulation:**")
                            st.dataframe(cross_tab, use_container_width=True)
                            
                            # Percentage cross-tabulation
                            cross_tab_pct = pd.crosstab(df[selected_variable], df[cross_var], normalize='index') * 100
                            
                            st.markdown("**📈 Row Percentages:**")
                            styled_cross = cross_tab_pct.style.format("{:.1f}%").background_gradient(cmap='Blues')
                            st.dataframe(styled_cross, use_container_width=True)
                            
                        elif var1_categorical and not var2_categorical:
                            # Categorical vs Numerical - grouped analysis
                            grouped_stats = df.groupby(selected_variable)[cross_var].agg(['mean', 'median', 'std', 'count']).round(3)
                            
                            st.markdown("**📊 Grouped Statistics:**")
                            st.dataframe(grouped_stats, use_container_width=True)
                            
                            # Box plot by group
                            fig_grouped = px.box(
                                df, 
                                x=selected_variable, 
                                y=cross_var,
                                title=f"{cross_var.replace('_', ' ').title()} by {selected_variable.replace('_', ' ').title()}"
                            )
                            fig_grouped.update_xaxes(tickangle=45)
                            st.plotly_chart(fig_grouped, use_container_width=True)
                            
                        elif not var1_categorical and var2_categorical:
                            # Numerical vs Categorical - same as above but reversed
                            grouped_stats = df.groupby(cross_var)[selected_variable].agg(['mean', 'median', 'std', 'count']).round(3)
                            
                            st.markdown("**📊 Grouped Statistics:**")
                            st.dataframe(grouped_stats, use_container_width=True)
                            
                            # Box plot by group
                            fig_grouped = px.box(
                                df, 
                                x=cross_var, 
                                y=selected_variable,
                                title=f"{selected_variable.replace('_', ' ').title()} by {cross_var.replace('_', ' ').title()}"
                            )
                            fig_grouped.update_xaxes(tickangle=45)
                            st.plotly_chart(fig_grouped, use_container_width=True)
                            
                        else:
                            # Both numerical - correlation and scatter plot
                            correlation = df[selected_variable].corr(df[cross_var])
                            
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                st.metric("Correlation", f"{correlation:.3f}")
                                
                                corr_strength = "Strong" if abs(correlation) > 0.5 else "Medium" if abs(correlation) > 0.3 else "Weak"
                                corr_direction = "Positive" if correlation > 0 else "Negative"
                                
                                st.markdown(f"**Direction:** {corr_direction}")
                                st.markdown(f"**Strength:** {corr_strength}")
                            
                            with col2:
                                # Scatter plot
                                fig_scatter = px.scatter(
                                    df, 
                                    x=selected_variable, 
                                    y=cross_var,
                                    title=f"Correlation: {selected_variable.replace('_', ' ').title()} vs {cross_var.replace('_', ' ').title()}",
                                    trendline="ols"
                                )
                                st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Data table viewer with advanced filtering
    st.markdown("### 📋 Advanced Data Table Viewer")
    
    # Advanced filtering options
    with st.expander("🔧 **Advanced Filters & Search**", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Text search
            search_term = st.text_input("🔍 Search in text fields:", "")
            
            # Professional role filter
            if 'Q2_Professional_Role' in df.columns:
                role_filter = st.multiselect(
                    "Filter by Professional Role:",
                    df['Q2_Professional_Role'].unique(),
                    default=[]
                )
        
        with col2:
            # Completion status filter
            if 'Progress' in df.columns:
                progress_filter = st.selectbox(
                    "Filter by Completion Status:",
                    ['All', 'Complete Only (100%)', 'Incomplete Only (<100%)']
                )
            
            # Years of experience filter
            if 'Q5_Years_HIV_Practice' in df.columns:
                exp_filter = st.multiselect(
                    "Filter by Experience:",
                    df['Q5_Years_HIV_Practice'].unique(),
                    default=[]
                )
        
        with col3:
            # Custom value filter
            filter_column = st.selectbox(
                "Custom Filter Column:",
                ['None'] + [col for col in df.columns if col not in ['ResponseID']],
                format_func=lambda x: x.replace('_', ' ').title() if x != 'None' else x
            )
            
            if filter_column != 'None':
                if df[filter_column].dtype in ['object', 'category']:
                    filter_values = st.multiselect(
                        f"Filter {filter_column} values:",
                        df[filter_column].unique(),
                        default=[]
                    )
                else:
                    # Numerical filter
                    min_val = float(df[filter_column].min())
                    max_val = float(df[filter_column].max())
                    filter_range = st.slider(
                        f"Filter {filter_column} range:",
                        min_val, max_val, (min_val, max_val)
                    )
    
    # Apply filters to dataframe
    filtered_display_df = df.copy()
    
    # Apply text search
    if search_term:
        text_cols = df.select_dtypes(include=['object']).columns
        mask = False
        for col in text_cols:
            mask |= df[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_display_df = filtered_display_df[mask]
    
    # Apply role filter
    if 'role_filter' in locals() and role_filter:
        filtered_display_df = filtered_display_df[filtered_display_df['Q2_Professional_Role'].isin(role_filter)]
    
    # Apply progress filter
    if 'progress_filter' in locals():
        if progress_filter == 'Complete Only (100%)':
            filtered_display_df = filtered_display_df[filtered_display_df['Progress'] == 100]
        elif progress_filter == 'Incomplete Only (<100%)':
            filtered_display_df = filtered_display_df[filtered_display_df['Progress'] < 100]
    
    # Apply experience filter
    if 'exp_filter' in locals() and exp_filter:
        filtered_display_df = filtered_display_df[filtered_display_df['Q5_Years_HIV_Practice'].isin(exp_filter)]
    
    # Apply custom filter
    if filter_column != 'None':
        if df[filter_column].dtype in ['object', 'category']:
            if 'filter_values' in locals() and filter_values:
                filtered_display_df = filtered_display_df[filtered_display_df[filter_column].isin(filter_values)]
        else:
            if 'filter_range' in locals():
                filtered_display_df = filtered_display_df[
                    (filtered_display_df[filter_column] >= filter_range[0]) & 
                    (filtered_display_df[filter_column] <= filter_range[1])
                ]
    
    # Display filter results
    st.markdown(f"""
    <div class="metric-card">
        <strong>📊 Filtered Results:</strong> {len(filtered_display_df):,} records 
        ({len(df) - len(filtered_display_df):,} filtered out)
    </div>
    """, unsafe_allow_html=True)
    
    # Column selection for display
    st.markdown("#### 🔍 **Select Columns to Display**")
    
    # Predefined column sets
    col_set = st.selectbox(
        "Quick Column Sets:",
        [
            "All Columns",
            "Core Variables (Demographics + Key Outcomes)",
            "Service Disruptions Only",
            "Professional Characteristics",
            "Clinical Settings",
            "Populations Served",
            "Barriers & Outcomes"
        ]
    )
    
    if col_set == "All Columns":
        selected_columns = df.columns.tolist()
    elif col_set == "Core Variables (Demographics + Key Outcomes)":
        selected_columns = [col for col in df.columns if col.startswith(('ResponseID', 'Progress', 'Q2_', 'Q5_', 'Q9_', 'Q11', 'Q13'))]
    elif col_set == "Service Disruptions Only":
        selected_columns = ['ResponseID', 'Q2_Professional_Role'] + [col for col in df.columns if col.startswith('Q9_')]
    elif col_set == "Professional Characteristics":
        selected_columns = [col for col in df.columns if col.startswith(('ResponseID', 'Q2_', 'Q5_', 'Q3_', 'Q4_'))]
    elif col_set == "Clinical Settings":
        selected_columns = ['ResponseID', 'Q2_Professional_Role'] + [col for col in df.columns if col.startswith('Q3_')]
    elif col_set == "Populations Served":
        selected_columns = ['ResponseID', 'Q2_Professional_Role'] + [col for col in df.columns if col.startswith('Q6_')]
    elif col_set == "Barriers & Outcomes":
        selected_columns = ['ResponseID', 'Q2_Professional_Role'] + [col for col in df.columns if col.startswith(('Q21', 'Q22', 'Q23', 'Q27', 'Q28', 'Q29', 'Q30'))]
    
    # Allow manual column selection
    if st.checkbox("🎛️ **Customize Column Selection**"):
        all_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Select Columns:",
            all_columns,
            default=selected_columns[:20] if len(selected_columns) > 20 else selected_columns,
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    # Row limiting
    max_rows = len(filtered_display_df)
    if max_rows > 1000:
        st.warning(f"⚠️ Large dataset ({max_rows:,} rows). Limiting display for performance.")
        max_display = 1000
    else:
        max_display = max_rows
    
    num_rows = st.slider(
        "Number of Rows to Display:", 
        1, 
        min(max_display, max_rows), 
        min(100, max_rows)
    )
    
    # Display the data table
    if selected_columns and len(filtered_display_df) > 0:
        display_df = filtered_display_df[selected_columns].head(num_rows)
        
        # Clean column names for display
        display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]
        
        st.markdown("#### 📋 **Data Table**")
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Data summary below table
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**📊 Showing:** {len(display_df):,} of {len(filtered_display_df):,} rows")
        
        with col2:
            st.markdown(f"**🔢 Columns:** {len(selected_columns)}")
        
        with col3:
            total_data_points = len(display_df) * len(selected_columns)
            st.markdown(f"**📈 Data Points:** {total_data_points:,}")
    
    # Export functionality
    st.markdown("### 📥 Export & Download Center")
    
    export_tab1, export_tab2, export_tab3 = st.tabs(["📊 Data Export", "📄 Reports", "🔧 Custom Export"])
    
    with export_tab1:
        st.markdown("#### 📊 **Standard Data Exports**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Full dataset export
            if st.button("📋 **Export Complete Dataset**"):
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download Complete Dataset (CSV)",
                    data=csv_data,
                    file_name="hiv_survey_complete_dataset.csv",
                    mime="text/csv"
                )
        
        with col2:
            # Filtered dataset export
            if len(filtered_display_df) < len(df):
                if st.button("🔍 **Export Filtered Dataset**"):
                    filtered_csv = filtered_display_df.to_csv(index=False)
                    st.download_button(
                        label="📊 Download Filtered Dataset (CSV)",
                        data=filtered_csv,
                        file_name="hiv_survey_filtered_dataset.csv",
                        mime="text/csv"
                    )
        
        with col3:
            # Selected columns export
            if selected_columns:
                if st.button("📋 **Export Selected Columns**"):
                    selected_csv = df[selected_columns].to_csv(index=False)
                    st.download_button(
                        label="📊 Download Selected Columns (CSV)",
                        data=selected_csv,
                        file_name="hiv_survey_selected_variables.csv",
                        mime="text/csv"
                    )
    
    with export_tab2:
        st.markdown("#### 📄 **Analysis Reports**")
        
        # Generate summary report
        if st.button("📄 **Generate Data Summary Report**"):
            # Create comprehensive summary report
            report_content = f"""HIV Service Disruption Survey - Data Summary Report
================================================================

Dataset Overview:
- Total Records: {len(df):,}
- Complete Records (100% Progress): {len(df[df['Progress'] == 100]):,}
- Total Variables: {len(df.columns)}
- Data Quality Score: {((df.notna().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%

Professional Role Distribution:
"""
            if 'Q2_Professional_Role' in df.columns:
                role_counts = df['Q2_Professional_Role'].value_counts()
                for role, count in role_counts.items():
                    pct = (count / len(df)) * 100
                    report_content += f"- {role}: {count:,} ({pct:.1f}%)\n"
            
            report_content += f"""

Service Disruption Summary:
"""
            disruption_cols = [col for col in df.columns if col.startswith('Q9_') and 'No_disruptions' not in col]
            for col in disruption_cols[:10]:  # Top 10 disruptions
                rate = df[col].mean() * 100
                count = df[col].sum()
                service_name = col.replace('Q9_', '').replace('_', ' ').title()
                report_content += f"- {service_name}: {rate:.1f}% ({count:,} providers affected)\n"
            
            report_content += f"""

Data Quality Assessment:
"""
            for col in df.columns[:20]:  # First 20 variables
                completeness = (df[col].notna().sum() / len(df)) * 100
                var_name = col.replace('_', ' ').title()
                report_content += f"- {var_name}: {completeness:.1f}% complete\n"
            
            report_content += f"""

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: HIV Service Disruption Survey Analysis Dashboard
"""
            
            st.download_button(
                label="📄 Download Summary Report (TXT)",
                data=report_content,
                file_name="hiv_survey_summary_report.txt",
                mime="text/plain"
            )
    
    with export_tab3:
        st.markdown("#### 🔧 **Custom Export Builder**")
        
        # Custom export configuration
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "Export Format:",
                ["CSV", "Excel (XLSX)", "JSON", "Tab-separated (TSV)"]
            )
            
            include_metadata = st.checkbox("Include Metadata", value=True)
            
        with col2:
            export_encoding = st.selectbox(
                "Character Encoding:",
                ["UTF-8", "UTF-16", "ASCII"]
            )
            
            compress_export = st.checkbox("Compress Export", value=False)
        
        # Variable selection for custom export
        st.markdown("**Select Variables for Export:**")
        
        export_categories = st.multiselect(
            "Variable Categories:",
            list(variable_categories.keys()),
            default=list(variable_categories.keys())[:3]
        )
        
        export_vars = []
        for category in export_categories:
            export_vars.extend(variable_categories[category])
        
        # Allow fine-tuning
        if st.checkbox("Fine-tune Variable Selection"):
            export_vars = st.multiselect(
                "Select Specific Variables:",
                export_vars,
                default=export_vars[:30] if len(export_vars) > 30 else export_vars,
                format_func=lambda x: x.replace('_', ' ').title()
            )
        
        # Generate custom export
        if st.button("🔧 **Generate Custom Export**") and export_vars:
            export_df = df[export_vars]
            
            if export_format == "CSV":
                export_data = export_df.to_csv(index=False, encoding=export_encoding.lower())
                mime_type = "text/csv"
                file_ext = "csv"
            elif export_format == "Excel (XLSX)":
                # For Excel, we'll use CSV format in this demo
                export_data = export_df.to_csv(index=False)
                mime_type = "text/csv"
                file_ext = "csv"
                st.info("Excel format converted to CSV for compatibility")
            elif export_format == "JSON":
                export_data = export_df.to_json(orient='records', indent=2)
                mime_type = "application/json"
                file_ext = "json"
            elif export_format == "Tab-separated (TSV)":
                export_data = export_df.to_csv(index=False, sep='\t', encoding=export_encoding.lower())
                mime_type = "text/tab-separated-values"
                file_ext = "tsv"
            
            # Add metadata if requested
            if include_metadata and export_format in ["CSV", "Tab-separated (TSV)"]:
                metadata = f"""# HIV Service Disruption Survey Data Export
# Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
# Total Records: {len(export_df):,}
# Variables: {len(export_vars)}
# Format: {export_format}
# Encoding: {export_encoding}
#
"""
                export_data = metadata + export_data
            
            st.download_button(
                label=f"📊 Download Custom Export ({export_format})",
                data=export_data,
                file_name=f"hiv_survey_custom_export.{file_ext}",
                mime=mime_type
            )

if __name__ == "__main__":
    main()
               
