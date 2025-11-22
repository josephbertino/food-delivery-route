# Deployment Guide

This guide covers deploying the Food Delivery Route Optimizer to production.

## Overview

The application consists of:
- **Frontend**: React app (deploy to Firebase Hosting)
- **Backend**: Flask API (deploy to Google Cloud Run)
- **Database**: Firebase Firestore (already set up)

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

### Option A: Using Cloud Run (Recommended)

1. **Create a Dockerfile** (if not already created):

   **Step-by-step instructions:**
   
   a. **Open your terminal** and navigate to the project root directory:
   ```bash
   cd /path/to/food-delivery-route
   ```
   
   b. **Create a new file called `Dockerfile`** (with no extension) in the root directory.
   
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
  
#HERE
3. **Build and deploy to Cloud Run**:

```bash
# Set your project ID
export PROJECT_ID=your-google-cloud-project-id
export SERVICE_NAME=food-delivery-api
export REGION=us-central1

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_MAPS_API_KEY=your_api_key \
  --set-env-vars FIREBASE_PROJECT_ID=your-firebase-project-id \
  --set-secrets FIREBASE_SERVICE_ACCOUNT=/secrets/firebase-service-account:latest
```

4. **Get the Cloud Run URL**:

After deployment, you'll get a URL like: `https://food-delivery-api-xxxxx.run.app`

### Option B: Using Firebase Functions (Alternative)

If you prefer to use Firebase Functions, you'll need to convert the Flask app to a Cloud Function. This is more complex but keeps everything in Firebase.

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

The Flask app already has CORS enabled, but make sure your Cloud Run service allows requests from your Firebase Hosting domain.

## Step 5: Set Up Environment Variables

For Cloud Run, set environment variables:

```bash
gcloud run services update $SERVICE_NAME \
  --region $REGION \
  --update-env-vars GOOGLE_MAPS_API_KEY=your_api_key \
  --update-env-vars FIREBASE_PROJECT_ID=your-firebase-project-id
```

For sensitive data (like service account keys), use Google Secret Manager:

```bash
# Create secret
echo -n '{"type":"service_account",...}' | gcloud secrets create firebase-service-account --data-file=-

# Grant access
gcloud secrets add-iam-policy-binding firebase-service-account \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Step 6: Set Up Custom Domain (Optional)

### For Firebase Hosting:

1. Go to Firebase Console → Hosting
2. Click "Add custom domain"
3. Follow the instructions to verify domain ownership
4. Update DNS records as instructed

### For Cloud Run:

1. Go to Cloud Run → Your Service → Manage Custom Domains
2. Map your domain to the Cloud Run service
3. Update DNS records

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

