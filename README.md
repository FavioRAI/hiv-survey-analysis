# hiv-survey-analysis
Survey Analysis 
# HIV Service Disruption Survey Analysis Dashboard

A comprehensive Streamlit application for analyzing HIV service disruption survey data, providing statistical analysis, cross-tabulations, and interactive visualizations for healthcare researchers and policy makers.

![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

## 🏥 Live Demo

**[View Live Application](https://your-app-name.streamlit.app)** *(Update this URL after deployment)*

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Data Structure](#data-structure)
- [Analysis Framework](#analysis-framework)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This application provides comprehensive analysis capabilities for HIV service disruption surveys, implementing a structured 5-indicator framework to examine:

1. **Service Disruptions & Affected Populations**
2. **Ancillary Services Access**
3. **Key Population Barriers**
4. **Anticipated Disruptions & Concerns**
5. **Federal Guidance Reliance & Trust**

The dashboard enables researchers to identify patterns, vulnerable populations, and system-wide impacts through statistical analysis and interactive visualizations.

## ✨ Features

### 📊 **Comprehensive Analysis Dashboard**
- **Overview Dashboard**: Survey metrics, completion rates, and quick insights
- **Indicator Set Analysis**: Deep-dive into each of the 5 research frameworks
- **Cross-Tabulation**: Statistical relationships with chi-square tests and effect sizes
- **Custom Analysis**: Flexible filtering and comparative analysis
- **Data Explorer**: Raw data exploration and export capabilities

### 📈 **Statistical Capabilities**
- Chi-square tests of independence
- Cramér's V effect size calculations
- Automated concern level classification (High/Medium/Low)
- Row and column percentage calculations
- Missing data handling and quality checks

### 🎨 **Interactive Visualizations**
- Plotly-powered interactive charts
- Heat maps for cross-tabulation analysis
- Distribution plots and comparative bar charts
- Color-coded concern level indicators
- Responsive design for all screen sizes

### 📁 **Data Management**
- Excel file upload support
- Sample data for demonstration
- CSV export functionality
- Data quality validation
- Automatic filtering of incomplete surveys

## 🚀 Installation

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/hiv-survey-analysis.git
cd hiv-survey-analysis
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
streamlit run app.py
```

5. **Open your browser to:** `http://localhost:8501`

## 🖥️ Usage

### 1. **Overview Dashboard**
- View survey completion metrics and data quality indicators
- Get quick insights into professional role distribution
- Explore top service disruptions across all respondents
- Navigate to specific indicator set analyses

### 2. **Indicator Set Analysis**
Select from 5 predefined research frameworks:
- **Set 1**: Service disruptions and affected populations
- **Set 2**: Ancillary services access and barriers
- **Set 3**: Key population system strain
- **Set 4**: Anticipated disruptions and concerns
- **Set 5**: Federal guidance reliance and trust

### 3. **Cross-Tabulation Analysis**
- Select outcome and independent variables
- Generate statistical cross-tabulations
- View frequency counts and row percentages
- Interpret chi-square test results and effect sizes
- Export results for further analysis

### 4. **Custom Analysis**
- Apply custom filters by professional role, experience, and settings
- Compare disruption rates across different groups
- Perform risk assessments to identify high-priority combinations
- Generate correlation matrices for numerical variables

### 5. **Data Upload**
- Upload your own Excel files (.xlsx, .xls)
- Application automatically detects and processes survey structure
- Maintains data quality by filtering incomplete responses

## 📊 Data Structure

### Required Columns

The application expects the following column structure:

#### **Core Survey Data**
- `Progress`: Completion percentage (filters for 100% complete)
- `ResponseID`: Unique response identifier

#### **Demographics & Characteristics**
- `Q2_Professional_Role`: Professional role categories
- `Q5_Years_HIV_Practice`: Years of HIV practice experience

#### **Clinical Settings (Q3)**
- `Q3_Setting_Ryan_White`: Ryan White clinic setting
- `Q3_Setting_Community_Health`: Community health center
- `Q3_Setting_Hospital_Based`: Hospital-based clinic

#### **Service Disruptions (Q9)**
- `Q9_Gender-Affirming Care`: Gender-affirming care disruptions
- `Q9_HIV Testing`: HIV testing service disruptions
- `Q9_HIV Treatment`: HIV treatment disruptions
- `Q9_[Service Name]`: Additional service categories

#### **Outcome Variables**
- `Q21`: Mental health services access
- `Q22`: Substance use services access
- `Q23`: Housing instability observations
- `Q11-Q15`: Future concerns and anticipated disruptions
- `Q18`: Federal guidelines usage frequency

### Sample Data

The application includes comprehensive sample data based on actual survey cross-tabulations, ensuring realistic analysis examples when no data file is uploaded.

## 🔬 Analysis Framework

### Indicator Set 1: Service Disruptions & Populations
**Research Question**: What types of HIV services have been disrupted, and which populations are most affected?

**Key Variables**:
- Service disruption types (Q9)
- Most affected populations (Q10)
- Professional role associations (Q2)

### Indicator Set 2: Ancillary Services Access
**Research Question**: How accessible are mental health, substance use, and housing support services?

**Key Variables**:
- Mental health access (Q21)
- Substance use services (Q22)
- Housing instability (Q23)

### Indicator Set 3: Key Population Barriers
**Research Question**: What barriers do vulnerable populations face in HIV service access?

**Key Variables**:
- Transgender-specific barriers
- Housing instability impacts
- Loss to follow-up patterns

### Indicator Set 4: Anticipated Disruptions
**Research Question**: What service disruptions do providers anticipate, and what are their concern levels?

**Key Variables**:
- 6-12 month disruption expectations (Q11)
- 12-18 month disruption expectations (Q12)
- Medicaid cut concerns (Q13)

### Indicator Set 5: Federal Guidance Trust
**Research Question**: How do providers use federal guidelines, and have they observed access changes?

**Key Variables**:
- Federal guideline usage frequency (Q18)
- Guidance access changes (Q19)
- Federal resource concerns (Q17)

## 🌐 Deployment

### Deploy to Streamlit Cloud

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
- Visit [share.streamlit.io](https://share.streamlit.io)
- Connect your GitHub account
- Select your repository
- Choose `app.py` as the main file
- Click "Deploy!"

3. **Your app will be available at:**
`https://[your-repo-name].streamlit.app`

### Environment Variables
No environment variables required for basic functionality.

### Resource Requirements
- **Memory**: 512MB recommended
- **CPU**: 1 vCPU sufficient
- **Storage**: Minimal (application uses uploaded data)

## 📁 File Structure

```
hiv-survey-analysis/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore file
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── data/                 # Sample data directory (optional)
    └── sample_data.xlsx  # Sample survey data
```

## 🤝 Contributing

We welcome contributions to improve the HIV Service Disruption Survey Analysis Dashboard!

### How to Contribute:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/new-analysis`
3. **Make your changes and commit:** `git commit -m "Add new analysis feature"`
4. **Push to your fork:** `git push origin feature/new-analysis`
5. **Submit a Pull Request**

### Contribution Areas:
- Additional statistical tests
- New visualization types
- Enhanced data export formats
- Mobile responsiveness improvements
- Documentation updates

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Plotly Documentation**: [plotly.com/python](https://plotly.com/python/)
- **Pandas Documentation**: [pandas.pydata.org](https://pandas.pydata.org)

### Issues and Questions
- **GitHub Issues**: [Report bugs or request features](https://github.com/yourusername/hiv-survey-analysis/issues)
- **Discussions**: [Join community discussions](https://github.com/yourusername/hiv-survey-analysis/discussions)

### Contact
- **Email**: your.email@institution.edu
- **Institution**: Your Research Institution
- **Project Lead**: Your Name

## 📊 Citation

If you use this application in your research, please cite:

```bibtex
@software{hiv_survey_analysis_2024,
  title={HIV Service Disruption Survey Analysis Dashboard},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/hiv-survey-analysis},
  note={Streamlit application for HIV service disruption analysis}
}
```

## 🏆 Acknowledgments

- **Survey Data**: Based on comprehensive HIV service provider surveys
- **Statistical Framework**: Implements established epidemiological analysis methods
- **Visualization**: Built with Plotly for interactive data exploration
- **Platform**: Powered by Streamlit for accessible web deployment

## 🔄 Version History

- **v1.0.0** (2024): Initial release with 5-indicator framework
- **v1.1.0** (Future): Enhanced statistical tests and export options
- **v1.2.0** (Future): Advanced machine learning predictions

---

**Built with ❤️ for HIV researchers and public health professionals**

*Empowering data-driven decisions in HIV care and services*
