# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### 1. Prerequisites
- GitHub repository with your code
- Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))

### 2. Required Files for Deployment
Make sure these files are in your repository:

```
├── streamlit_dashboard.py          # Main app file
├── requirements.txt                # Dependencies
├── runtime.txt                     # Python version
├── .streamlit/config.toml          # Streamlit config
└── README.md                       # Documentation
```

### 3. Deploy Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```

2. **Connect to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select your repository and branch (usually `main`)
   - Set main file path: `streamlit_dashboard.py`
   - Click "Deploy!"

### 4. Configuration Files

**requirements.txt** (already created):
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
openpyxl>=3.1.0
xlsxwriter>=3.1.0
matplotlib>=3.7.0
seaborn>=0.12.0
reportlab>=4.0.0
chardet>=5.0.0
```

**runtime.txt** (already created):
```
python-3.11
```

**.streamlit/config.toml** (already created):
```toml
[global]
developmentMode = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### 5. Demo Mode

The dashboard now includes **Demo Mode** with sample data, so it will work even without the actual data files. This is perfect for deployment demonstrations.

When deployed, the dashboard will:
- ✅ Show sample data if real data files are missing
- ✅ Display a warning that it's in demo mode
- ✅ Provide instructions for uploading real data
- ✅ Work with all interactive features

### 6. Troubleshooting

**Common Issues:**

1. **App won't start**
   - Check that `streamlit_dashboard.py` is in the root directory
   - Verify all dependencies are in `requirements.txt`
   - Check the logs in Streamlit Cloud dashboard

2. **Import errors**
   - Make sure all required packages are listed in `requirements.txt`
   - Check Python version compatibility in `runtime.txt`

3. **Data not loading**
   - The app will automatically use sample data if real data is missing
   - This is expected behavior for demo deployments

### 7. Using Real Data

To use your actual data in the deployed app:

1. **Option A: Include data files in repository**
   ```bash
   git add *.xlsx *.csv
   git commit -m "Add data files"
   git push
   ```

2. **Option B: File upload feature** (future enhancement)
   - Add file upload widget to dashboard
   - Process uploaded files dynamically

### 8. Custom Domain (Optional)

Once deployed, you can:
- Use the provided Streamlit URL: `https://your-app-name.streamlit.app`
- Set up a custom domain through Streamlit Cloud settings

### 9. Updates

To update your deployed app:
```bash
git add .
git commit -m "Update dashboard"
git push origin main
```

The app will automatically redeploy when you push to GitHub.

---

**Need Help?**
- Check Streamlit Cloud logs for error messages
- Verify all files are committed to GitHub
- Test locally first: `streamlit run streamlit_dashboard.py` 