# 🚀 Deployment Guide: GitHub + Streamlit Cloud

Complete step-by-step guide to deploy your HIV Service Disruption Survey Analysis Dashboard from GitHub to Streamlit Cloud.

## 📋 Prerequisites

Before starting, ensure you have:
- A GitHub account ([Sign up here](https://github.com/join))
- A Streamlit Cloud account ([Sign up here](https://share.streamlit.io/signup))
- Git installed on your computer ([Download here](https://git-scm.com/downloads))
- Python 3.8+ installed ([Download here](https://www.python.org/downloads/))

## 🗂️ Step 1: Prepare Your Project Files

Create a new folder for your project and add these files:

```
hiv-survey-analysis/
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies  
├── README.md                 # Project documentation
├── .gitignore               # Files to ignore in Git
├── DEPLOYMENT_GUIDE.md      # This guide
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

### File Contents Summary:
- **app.py**: Your main Streamlit application (provided above)
- **requirements.txt**: Python package dependencies
- **README.md**: Comprehensive project documentation
- **.gitignore**: Excludes temporary files and sensitive data
- **config.toml**: Streamlit app configuration and theming

## 🐙 Step 2: Create GitHub Repository

### Option A: Using GitHub Website

1. **Go to GitHub.com** and sign in to your account
2. **Click the "+" icon** in the top right corner
3. **Select "New repository"**
4. **Fill in repository details:**
   - Repository name: `hiv-survey-analysis`
   - Description: `Interactive dashboard for HIV service disruption survey analysis`
   - Set to **Public** (required for free Streamlit deployment)
   - ✅ Check "Add a README file"
   - Choose **Python** for .gitignore template
   - Select **MIT License** (recommended)
5. **Click "Create repository"**

### Option B: Using Command Line

```bash
# Navigate to your project folder
cd path/to/your/hiv-survey-analysis

# Initialize Git repository
git init

# Add all files
git add .

# Make initial commit
git commit -m "Initial commit: HIV Survey Analysis Dashboard"

# Add GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/hiv-survey-analysis.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 📁 Step 3: Upload Your Files to GitHub

### Method 1: Upload via GitHub Website

1. **Go to your repository** on GitHub.com
2. **Click "uploading an existing file"** or drag and drop files
3. **Upload all project files:**
   - Drag `app.py`, `requirements.txt`, `README.md`, `.gitignore`
   - Create `.streamlit` folder and upload `config.toml`
4. **Add commit message:** "Add HIV survey analysis application"
5. **Click "Commit changes"**

### Method 2: Push via Command Line (if files are ready locally)

```bash
# Make sure you're in your project directory
cd hiv-survey-analysis

# Add all files
git add .

# Commit changes
git commit -m "Add complete HIV survey analysis application"

# Push to GitHub
git push origin main
```

## ☁️ Step 4: Deploy to Streamlit Cloud

### 4.1 Access Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub** (click "Continue with GitHub")
3. **Authorize Streamlit** to access your GitHub repositories

### 4.2 Deploy Your App

1. **Click "New app"** on the Streamlit Cloud dashboard
2. **Select deployment source:**
   - Repository: `YOUR_USERNAME/hiv-survey-analysis`
   - Branch: `main` (default)
   - Main file path: `app.py`
3. **Advanced settings** (optional):
   - App URL: `hiv-survey-analysis` (or custom name)
   - Python version: `3.9` (or latest stable)
4. **Click "Deploy!"**

### 4.3 Monitor Deployment

- **Deployment typically takes 2-5 minutes**
- **Watch the deployment logs** for any errors
- **Your app will be available at:** `https://your-app-name.streamlit.app`

## ✅ Step 5: Verify Deployment

### 5.1 Test Core Functionality

1. **Open your deployed app** in a browser
2. **Check all tabs work:**
   - 🏠 Overview
   - 🎯 Indicator Set Analysis  
   - 📊 Cross-Tabulation
   - 🔬 Custom Analysis
   - 📋 Data Explorer

3. **Test key features:**
   - Sample data loads correctly
   - Visualizations render properly
   - File upload functionality works
   - Export buttons function

### 5.2 Performance Check

- **Loading time** should be under 30 seconds
- **Interactive elements** should be responsive
- **Charts should render** without errors
- **Mobile compatibility** check (optional)

## 🔧 Step 6: Post-Deployment Configuration

### 6.1 Update Repository Settings

1. **Go to your GitHub repository**
2. **Click "Settings" tab**
3. **Scroll to "Pages" section**
4. **Add deployment link:**
   - Add your Streamlit app URL to the repository description
   - Pin the repository for easy access

### 6.2 Update README with Live Link

Edit your README.md to include the live app link:

```markdown
## 🏥 Live Demo

**[🚀 View Live Application](https://your-actual-app-name.streamlit.app)**
```

### 6.3 Set Up Automatic Redeployment

**Good news!** Streamlit Cloud automatically redeploys when you push changes to your GitHub repository.

```bash
# Make changes to your code
# Then push updates:
git add .
git commit -m "Update: Added new analysis feature"
git push origin main

# Streamlit will automatically redeploy within 2-3 minutes
```

## 🎯 Step 7: Customize Your Deployment

### 7.1 Custom Domain (Optional)

For custom domains:
1. **Upgrade to Streamlit Cloud Pro** (if needed)
2. **Configure CNAME records** in your DNS settings
3. **Add custom domain** in Streamlit Cloud settings

### 7.2 Environment Variables

If you need environment variables:
1. **Go to your app dashboard** on Streamlit Cloud
2. **Click "Settings"**
3. **Add secrets** in the "Secrets" section:

```toml
# Example secrets.toml format
API_KEY = "your-api-key"
DATABASE_URL = "your-database-connection"
```

### 7.3 Resource Optimization

For better performance:
- **Optimize data loading** with `@st.cache_data`
- **Reduce file sizes** for faster loading
- **Use efficient data formats** (Parquet vs CSV)

## 🐛 Step 8: Troubleshooting Common Issues

### Deployment Fails

**Issue**: App fails to deploy
**Solutions**:
1. Check `requirements.txt` for package version conflicts
2. Ensure `app.py` is in the root directory
3. Verify Python version compatibility
4. Check deployment logs for specific error messages

### Missing Dependencies

**Issue**: Import errors or missing packages
**Solutions**:
1. Update `requirements.txt` with all required packages
2. Specify exact versions if needed:
   ```
   streamlit==1.28.0
   pandas==1.5.3
   ```
3. Test locally first: `pip install -r requirements.txt`

### Data Upload Issues

**Issue**: File upload doesn't work
**Solutions**:
1. Check file size limits (200MB default)
2. Verify supported file formats (.xlsx, .xls)
3. Test with sample files first

### Slow Performance

**Issue**: App loads slowly
**Solutions**:
1. Add caching to data loading functions
2. Optimize visualization code
3. Reduce initial data processing
4. Consider data preprocessing

## 🔄 Step 9: Maintenance and Updates

### Regular Updates

```bash
# Pull latest changes (if collaborating)
git pull origin main

# Make your updates to code
# Test locally first:
streamlit run app.py

# Push updates
git add .
git commit -m "Enhancement: Improved data visualization"
git push origin main
```

### Monitoring

- **Check app health** regularly via Streamlit Cloud dashboard
- **Monitor usage statistics** (available in cloud dashboard)
- **Review error logs** if issues arise
- **Update dependencies** periodically for security

### Backup Strategy

1. **Keep local copies** of your code
2. **Use GitHub releases** for major versions
3. **Export important configurations**
4. **Document any custom modifications**

## 📞 Step 10: Getting Help

### Resources

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Documentation**: [docs.github.com](https://docs.github.com)

### Support Channels

- **Streamlit Cloud Support**: Via the dashboard help section
- **GitHub Issues**: For code-related problems
- **Community Forums**: For general questions

### Quick Fixes

| Problem | Quick Solution |
|---------|---------------|
| App won't start | Check requirements.txt |
| Import errors | Verify all packages in requirements |
| Data not loading | Check file paths and permissions |
| Charts not showing | Verify Plotly installation |
| Slow performance | Add @st.cache_data decorators |

## 🎉 Congratulations!

Your HIV Service Disruption Survey Analysis Dashboard is now live and accessible worldwide! 

### Your URLs:
- **GitHub Repository**: `https://github.com/YOUR_USERNAME/hiv-survey-analysis`
- **Live Application**: `https://your-app-name.streamlit.app`

### Next Steps:
1. **Share your app** with colleagues and stakeholders
2. **Gather feedback** for improvements
3. **Add new features** based on user needs
4. **Consider scaling** for larger datasets

---

**🚀 Happy analyzing!** Your dashboard is now ready to help researchers and policymakers make data-driven decisions in HIV care and services.
