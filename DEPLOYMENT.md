# Deployment Guide

This guide covers deploying the Food Delivery Route Optimizer to production.

## Overview

The application consists of:
- **Frontend**: React app (deploy to Firebase Hosting)
- **Backend**: Flask API (needs to be deployed to a server - Cloud Run recommended)
- **Database**: Firebase Firestore (already set up)

### Why Do You Need to Deploy the Backend?

Your Flask backend (`app.py`) provides critical API endpoints that your React frontend calls:
- `/api/optimize-route` - Processes CSV files, calls Google Maps API, optimizes routes, stores in Firestore
- `/api/route/<code>` - Retrieves stored routes from Firestore

**The backend must be publicly accessible on the internet** so your deployed frontend can make HTTP requests to it. You cannot run the backend only on your local machine - it needs to be hosted on a server.

**Why Google Cloud Run?**
- Serverless (scales to zero when not in use, reducing costs)
- Pay-per-use pricing (very affordable for low traffic)
- Easy integration with Firebase/Google Cloud services
- Simple deployment with Docker
- Free tier: 2 million requests/month

**Alternative Options:**
- **Firebase Functions** (Option B below) - Keeps everything in Firebase ecosystem
- **Other Platforms**: Heroku, Railway, Render, AWS Lambda, Azure Functions
- **Self-hosted**: VPS, your own server (requires more maintenance)

## Prerequisites

1. Firebase project created (see [FIREBASE_SETUP.md](FIREBASE_SETUP.md))
2. Google Cloud project with billing enabled
3. Google Maps API key configured
4. Firebase CLI installed: `npm install -g firebase-tools`
5. Google Cloud SDK installed (for Cloud Run deployment)

## Step 1: Deploy Frontend to Firebase Hosting

### Build the React App

```bash
cd frontend
npm run build
cd ..
```

### Configure Firebase Hosting

Make sure `firebase.json` is configured correctly (already set up).

### Deploy

```bash
firebase deploy --only hosting
```

Your frontend will be available at: `https://your-project-id.web.app`

## Step 2: Deploy Backend to Google Cloud Run

### Using Cloud Run

1. **Create a Dockerfile** (if not already created):

   **Step-by-step instructions:**
   
   a. **Create a new file called `Dockerfile`** (with no extension) in the root directory.
   
   c. **Add the following content to the Dockerfile**:
   
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   ENV PORT=8080
   CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
   ```
   
   **What each line does:**
   - `FROM python:3.11-slim`: Starts with a lightweight Python 3.11 base image
   - `WORKDIR /app`: Sets `/app` as the working directory inside the container
   - `COPY requirements.txt .`: Copies your requirements file into the container
   - `RUN pip install ...`: Installs all Python dependencies
   - `COPY . .`: Copies all your application files into the container
   - `ENV PORT=8080`: Sets the port environment variable (Cloud Run uses port 8080)
   - `CMD exec gunicorn ...`: Runs your Flask app using Gunicorn (production WSGI server)
   
   d. **Save the file** - Make sure it's saved as `Dockerfile` in the root directory (same level as `app.py` and `requirements.txt`)
   
   e. **Verify the file was created correctly**:
   ```bash
   ls -la Dockerfile
   cat Dockerfile
   ```

2. **Create a `.dockerignore` file. Add the following content to `.dockerignore`**:
  
  ```
  __pycache__
  *.pyc
  *.pyo
  *.pyd
  .Python
  env/
  venv/
  .venv
  .env
  *.log
  node_modules/
  frontend/
  .git/
  .firebase/
  ```
  
  **What this file does:**
  - Tells Docker to ignore these files/folders when building the image
  - Reduces image size and prevents sensitive files (like `.env`) from being included
  - Excludes virtual environments, cache files, and the frontend (which is deployed separately)
  
3. **Build and deploy to Cloud Run**:

```bash
# Set your project ID and other variables
export PROJECT_ID=food-delivery-route-optimizer
export SERVICE_NAME=food-delivery-route
export REGION=us-central1

# IMPORTANT: Set the default gcloud project (gcloud doesn't use the PROJECT_ID env var automatically)
gcloud config set project $PROJECT_ID

# Verify the project is set correctly
gcloud config get-value project

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
# First, grant Firestore permissions to Cloud Run service account (one-time setup):
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"

# Then deploy (uses default credentials - no secrets needed):
# Replace your-project-id with your actual Firebase project ID for CORS_ORIGINS
# Deploy without CORS_ORIGINS first (to avoid comma parsing issues)
# HERE
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_MAPS_API_KEY=your-api-key,FIREBASE_PROJECT_ID=food-delivery-route

# Set CORS_ORIGINS separately after deployment (handles comma-separated values better)
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --update-env-vars CORS_ORIGINS="https://food-delivery-route.web.app,https://food-delivery-route.firebaseapp.com"
```

**Note:** If you get an error about the project not being set, you can also add `--project $PROJECT_ID` to each gcloud command, or set it once with `gcloud config set project $PROJECT_ID` (recommended).

4. **Get the Cloud Run URL**:

After deployment, you'll get a URL like: `https://food-delivery-api-xxxxx.run.app`

### Option B: Using Firebase Functions (Alternative)

If you prefer to use Firebase Functions, you'll need to convert the Flask app to a Cloud Function. This is more complex but keeps everything in Firebase.

I will consider moving to Firebase functions if the project takes off

## Step 3: Update Frontend API URL

1. Create `frontend/.env.production`:

```bash
REACT_APP_API_URL=https://your-cloud-run-url.run.app/api
```

2. Rebuild and redeploy:

```bash
cd frontend
npm run build
cd ..
firebase deploy --only hosting
```

## Step 4: Configure CORS

The Flask app has CORS enabled, but you should restrict it to your Firebase Hosting domain for security.

1. **Get your Firebase Hosting URL:**
   - After deploying to Firebase Hosting, your URL will be: `https://your-project-id.web.app`
   - Or if you have a custom domain: `https://your-custom-domain.com`

2. **Set CORS origins in Cloud Run:**
   ```bash
   # Replace with your actual Firebase Hosting URL
   # Note: Comma-separated values must be quoted
   gcloud run services update $SERVICE_NAME \
     --region $REGION \
     --update-env-vars CORS_ORIGINS="https://your-project-id.web.app,https://your-project-id.firebaseapp.com"
   ```

   **Note:** 
   - You can specify multiple origins separated by commas (must be quoted)
   - If you don't set `CORS_ORIGINS`, the app will allow all origins (useful for development but not recommended for production)
   - Alternatively, you can set them one at a time or use a different approach (see troubleshooting below)

3. **Verify CORS is working:**
   - Open your Firebase Hosting site in a browser
   - Open Developer Tools → Network tab
   - Try using the app - API requests should succeed
   - Check the response headers - you should see `Access-Control-Allow-Origin` header

**Troubleshooting CORS/503 Errors:**

If you get a 503 error with CORS issues:

1. **Check if Cloud Run service is running and get the URL:**
   ```bash
   gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)"
   ```
   - This will show the service URL if it exists
   - If empty, the service might not be deployed

2. **Check Cloud Run logs for errors:**
   ```bash
   gcloud run services logs read $SERVICE_NAME --region $REGION --limit 50
   ```
   - Look for startup errors, missing environment variables, or crashes
   - Check for "GOOGLE_MAPS_API_KEY" errors or Firebase initialization failures

3. **Verify environment variables are set:**
   ```bash
   # List all environment variables
   gcloud run services describe $SERVICE_NAME --region $REGION \
     --format="table(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"
   ```
   Or to see them in a more readable format:
   ```bash
   gcloud run services describe $SERVICE_NAME --region $REGION \
     --format="yaml(spec.template.spec.containers[0].env)"
   ```
   - Make sure `GOOGLE_MAPS_API_KEY` and `FIREBASE_PROJECT_ID` are set
   - Check that `CORS_ORIGINS` matches your Firebase Hosting URL exactly (including `https://`)
   - If variables are missing, update them (see Step 5 below)

4. **Test the health endpoint directly:**
   ```bash
   curl https://your-cloud-run-url.run.app/api/health
   ```
   - Should return `{"status":"ok"}`
   - If this fails, the service isn't running properly

5. **Fixing CORS_ORIGINS with comma-separated values:**
   
   If `--update-env-vars` doesn't work with comma-separated values, use one of these approaches:
   
   **Option A: Use quotes (recommended):**
   ```bash
   gcloud run services update $SERVICE_NAME \
     --region $REGION \
     --update-env-vars CORS_ORIGINS="https://your-project-id.web.app,https://your-project-id.firebaseapp.com"
   ```
   
   **Option B: Set all env vars at once (use update-env-vars for each to avoid comma issues):**
   ```bash
   gcloud run services update $SERVICE_NAME \
     --region $REGION \
     --update-env-vars GOOGLE_MAPS_API_KEY=your_api_key \
     --update-env-vars FIREBASE_PROJECT_ID=your-project-id \
     --update-env-vars CORS_ORIGINS="https://your-project-id.web.app,https://your-project-id.firebaseapp.com"
   ```
   
   **Option C: Set only one origin (simplest):**
   ```bash
   gcloud run services update $SERVICE_NAME \
     --region $REGION \
     --update-env-vars CORS_ORIGINS=https://your-project-id.web.app
   ```

6. **Common issues:**
   - **Missing environment variables**: Service crashes on startup if `GOOGLE_MAPS_API_KEY` is missing
   - **Wrong CORS origin**: Must match exactly (including protocol `https://` and no trailing slash)
   - **Service not deployed**: Make sure deployment completed successfully
   - **Firestore permissions**: Service account needs `roles/datastore.user` role

## Step 5: Set Up Environment Variables

For Cloud Run, set or update environment variables:

```bash
# Option 1: Update individual variables (comma-separated values must be quoted)
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --update-env-vars GOOGLE_MAPS_API_KEY=your_api_key \
  --update-env-vars FIREBASE_PROJECT_ID=your-firebase-project-id \
  --update-env-vars CORS_ORIGINS="https://your-project-id.web.app,https://your-project-id.firebaseapp.com"

# Option 2: Set all at once using multiple update-env-vars flags (recommended for comma-separated values)
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --update-env-vars GOOGLE_MAPS_API_KEY=your_api_key \
  --update-env-vars FIREBASE_PROJECT_ID=your-project-id \
  --update-env-vars CORS_ORIGINS="https://your-project-id.web.app,https://your-project-id.firebaseapp.com"
```

**Note:** The app uses Cloud Run's default credentials to access Firestore. No service account JSON file or Secret Manager setup is needed - just make sure you've granted the `roles/datastore.user` permission to the Cloud Run service account (done in Step 2 above).

## Step 7: Monitor and Maintain

### View Logs

```bash
# Cloud Run logs
gcloud run services logs read $SERVICE_NAME --region $REGION

# Firebase Hosting analytics
# View in Firebase Console → Hosting → Analytics
```

### Set Up Alerts

1. Go to Google Cloud Console → Monitoring → Alerting
2. Create alerts for:
   - High error rates
   - High latency
   - API quota usage

### Cost Monitoring

- Monitor Google Maps API usage in Google Cloud Console
- Monitor Cloud Run costs in Billing
- Monitor Firestore usage in Firebase Console

## Troubleshooting

**Frontend can't connect to backend:**
- Check CORS settings
- Verify API URL in `.env.production`
- Check Cloud Run service is running

**Routes not persisting:**
- Verify Firestore is set up correctly
- Check service account permissions
- Verify environment variables are set

**API errors:**
- Check Google Maps API quota
- Verify API key is correct
- Check Cloud Run logs for errors

## Cost Estimation

Approximate monthly costs (for moderate usage):

- **Firebase Hosting**: Free tier (10 GB storage, 360 MB/day transfer)
- **Cloud Run**: ~$5-20/month (depending on traffic)
- **Firestore**: Free tier (1 GB storage, 50K reads/day)
- **Google Maps API**: $200 free credit/month, then ~$5 per 1,000 requests

Total: ~$5-25/month for moderate usage (within free tiers)

