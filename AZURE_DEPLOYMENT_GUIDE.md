# Azure Deployment Guide - GoData Dashboard

## Step-by-Step Instructions

### 1. Access Azure Portal
- Go to https://portal.azure.com
- Sign in with your Azure account

### 2. Create a Web App

**2.1. Search for App Services**
- In the search bar at the top, type "App Services"
- Click on "App Services"

**2.2. Create New App Service**
- Click the "+ Create" button
- Select "Web App"

**2.3. Configure Basic Settings**

**Project Details:**
- **Subscription**: Select your Azure subscription
- **Resource Group**: Click "Create new" → Name it `godata-rg` → OK

**Instance Details:**
- **Name**: `godata-dashboard` (must be globally unique - try `godata-dashboard-yourname` if taken)
- **Publish**: Select `Code`
- **Runtime stack**: Select `Python 3.11`
- **Operating System**: Select `Linux`
- **Region**: Select `East US` (or closest to you)

**Pricing Plan:**
- Click "Change size"
- Select `Dev/Test` tab
- Choose `F1` (Free) or `B1` (Basic - recommended for better performance)
- Click "Apply"

**2.4. Click "Next: Deployment >"**

### 3. Configure GitHub Deployment

**3.1. Enable GitHub Actions**
- **Continuous deployment**: Enable
- **GitHub account**: Click "Authorize" and sign in with GitHub account `godataec`
- **Organization**: Select `godataec`
- **Repository**: Select `apprentabilidad`
- **Branch**: Select `main`

**3.2. Click "Review + create"**
- Review all settings
- Click "Create"
- Wait 2-3 minutes for deployment to complete

### 4. Configure Application Settings

**4.1. Go to your new App Service**
- Click "Go to resource" when deployment completes

**4.2. Configure Startup Command**
- In the left menu, scroll to "Settings"
- Click "Configuration"
- Click "General settings" tab
- **Startup Command**: Enter `gunicorn dashboard:server`
- Click "Save" at the top
- Click "Continue" when prompted

**4.3. Add Environment Variables (Optional)**
- Still in "Configuration", click "Application settings" tab
- Click "+ New application setting"
- **Name**: `DASH_DEBUG`
- **Value**: `False`
- Click "OK"
- Click "Save" at the top
- Click "Continue"

### 5. Deploy from GitHub

**5.1. Go to Deployment Center**
- In the left menu, click "Deployment Center"
- You should see your GitHub repo connected
- Azure will automatically deploy when you push to `main` branch

**5.2. Monitor Deployment**
- Click "Logs" tab to see deployment progress
- Wait for "Deployment successful" message (~3-5 minutes)

### 6. Access Your Dashboard

**6.1. Get Your URL**
- In the App Service overview page (left menu → "Overview")
- Find the "URL" (looks like: `https://godata-dashboard.azurewebsites.net`)
- Click on it or copy to browser

**6.2. First Load**
- First access takes 10-20 seconds (app is generating data)
- Subsequent loads are instant

---

## Troubleshooting

**If deployment fails:**
1. Go to "Deployment Center" → "Logs"
2. Check the error messages
3. Common issues:
   - Wrong startup command → Check "Configuration" → "General settings"
   - Missing dependencies → Check `requirements.txt`
   - Runtime errors → Check "Log stream" in left menu

**If app shows errors:**
1. Go to "Log stream" in left menu
2. Look for Python errors
3. Check that all files are in GitHub repo

**Need to redeploy?**
1. Make changes locally
2. `git add .`
3. `git commit -m "Your message"`
4. `git push`
5. Azure auto-deploys in 2-3 minutes

---

## Your App Info

- **GitHub Repo**: https://github.com/godataec/apprentabilidad
- **Azure URL**: `https://godata-dashboard.azurewebsites.net` (or your custom name)
- **Startup Command**: `gunicorn dashboard:server`
- **Runtime**: Python 3.11 on Linux

---

## Next Steps After Deployment

1. Test all features:
   - Year/Month filters
   - Bubble chart hover
   - Scatter plot updates
   - Customer table search

2. Share the URL with your team

3. Monitor in Azure:
   - Go to "Monitoring" → "Metrics" to see usage
   - Check "Log stream" for any errors

**Estimated deployment time: 10-15 minutes**
