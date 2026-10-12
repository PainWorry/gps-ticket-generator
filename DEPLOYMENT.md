# Deployment Guide: Streamlit Community Cloud (Free POC)

This guide details the procedure to deploy the GPS Ticket Generator on Streamlit Community Cloud.

## Prerequisites
1. A GitHub account.
2. A free account on [share.streamlit.io](https://share.streamlit.io) connected to your GitHub account.

---

## Step 1: Push Code to GitHub

1. Initialize Git in the project folder:
   ```bash
   cd "C:\Users\Onelink\OneDrive - Onelink Technology Co., Ltd\New_DT_GP\20261012_Streamlit_deploy"
   git init
   git add app.py requirements.txt .gitignore cs_ticket_generator.html DEPLOYMENT.md
   git commit -m "feat: initial commit for GPS ticket generator Streamlit POC"
   ```

2. Create a new repository on GitHub (e.g., `gps-ticket-generator`).

3. Link the remote and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<your-username>/gps-ticket-generator.git
   git push -u origin main
   ```

---

## Step 2: Deploy to Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**.
3. Fill in the deployment details:
   - **Repository**: `<your-username>/gps-ticket-generator`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Advanced settings**: Select **Python 3.9** under Python version.
   - **App URL** (Optional): Choose a custom subdomain (e.g., `gps-ticket-generator.streamlit.app`).
4. Click **Deploy**.

Streamlit Cloud will provision the container, install packages from `requirements.txt`, and launch the app at the provided public URL.

---

## Step 3: Local Testing (Optional)

To run the application locally before deploying:
```bash
pip install -r requirements.txt
streamlit run app.py
```
