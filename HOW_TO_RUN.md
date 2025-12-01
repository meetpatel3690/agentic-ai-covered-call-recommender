# 🚀 Quick Start Guide - Run the App in 30 Seconds

## ⚡ THE EASIEST WAY (Recommended)

### Option 1: Double-Click Method

## Step 1: Navigate to the Project Directory
 
#cd "C:\Users\meetp\OneDrive\Desktop\Complete_Options_Data_Agent\Agentic---AI---Stock---Recommendation"

## Step 2: Activate the Virtual Environment

.\.venv\Scripts\Activate.ps1

## Step 3: Install/Update Packages Using UV

uv add -r requirements.txt

## Step 4: Run the Streamlit App

streamlit run UI\app.py
---------------------------------------------------------
# Step 1: Go to project folder
cd "C:\Users\meetp\OneDrive\Desktop\Complete_Options_Data_Agent\Agentic---AI---Stock---Recommendation"

# Step 2: Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Step 3: Install packages (only needed first time or when packages change)
uv pip install streamlit requests pandas python-dotenv streamlit-searchbox

# Step 4: Run the app
streamlit run UI\app.py