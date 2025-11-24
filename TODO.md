# TODO: Getting the App Fully Functional

This document lists all the actions you need to take to get the Food Delivery Route Optimizer app fully functional. Follow these steps in order.

## Prerequisites Check

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 14+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] Google account (for Google Cloud and Firebase)

---

## Phase 1: Local Development Setup

### Step 1: Install Dependencies

- [ ] Install Python dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Install frontend dependencies:
  ```bash
  cd frontend
  npm install
  cd ..
  ```

### Step 2: Set Up Google Maps API

**Reference:** See `GOOGLE_MAPS_SETUP.md` for detailed instructions

- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Create a new project (or select existing one)
- [ ] Enable the following APIs:
  - [ ] Distance Matrix API
  - [ ] Directions API
- [ ] Create an API Key:
  - [ ] Go to APIs & Services → Credentials
  - [ ] Click "Create Credentials" → "API Key"
  - [ ] Copy the API key
- [ ] (Recommended) Restrict the API key:
  - [ ] Click on the API key to edit
  - [ ] Under "API restrictions", select "Restrict key"
  - [ ] Check only: Distance Matrix API, Directions API
  - [ ] Save
- [ ] Set up billing (required for Google Maps APIs):
  - [ ] Go to Billing in Google Cloud Console
  - [ ] Link a billing account
  - [ ] Note: $200 free credit/month covers most usage

### Step 3: Set Up Firebase (For Route Storage)

**Reference:** See `FIREBASE_SETUP.md` for detailed instructions

- [ ] Install Firebase CLI:
  ```bash
  npm install -g firebase-tools
  ```

- [ ] Login to Firebase:
  ```bash
  firebase login
  ```

- [ ] Create Firebase project:
  - [ ] Go to [Firebase Console](https://console.firebase.google.com/)
  - [ ] Click "Add project"
  - [ ] Enter project name
  - [ ] (Optional) Enable Google Analytics
  - [ ] Click "Create project"

- [ ] **Upgrade to BLAZE plan (Required for Cloud Functions):**
  - [ ] Go to Firebase Console → Project Settings → Usage and billing
  - [ ] Click "Modify plan" or "Upgrade to Blaze"
  - [ ] Select the Blaze (pay-as-you-go) plan
  - [ ] Link a billing account (credit card required)
  - [ ] **Note:** Cloud Functions require the Blaze plan, but the free tier is generous:
    - 2 million function invocations/month (FREE)
    - 400,000 GB-seconds/month (FREE)
    - 200,000 CPU-seconds/month (FREE)
    - The scheduled cleanup job runs once daily (~30 invocations/month), so it's FREE
  - [ ] See [Firebase Pricing](https://firebase.google.com/pricing) for details

- [ ] Initialize Firebase in your project:
  ```bash
  firebase init
  ```
  - [ ] Select: Hosting, Firestore
  - [ ] Select your Firebase project
  - [ ] For hosting: Public directory = `frontend/build`, Single-page app = Yes
  - [ ] For Firestore: Use default security rules = Yes, choose location

- [ ] Update `.firebaserc`:
  - [ ] Replace `your-firebase-project-id` with your actual Firebase project ID

- [ ] Set up Firestore Security Rules:
  - [ ] Go to Firebase Console → Firestore Database → Rules
  - [ ] Update rules (see `FIREBASE_SETUP.md` for the rules)
  - [ ] Click "Publish"

- [ ] Get Firebase Service Account Key:
  - [ ] Go to Firebase Console → Project Settings → Service Accounts
  - [ ] Click "Generate new private key"
  - [ ] Save the JSON file as `firebase-service-account.json` in project root
  - [ ] Verify it's in `.gitignore` (should already be there)

### Step 4: Configure Environment Variables

- [ ] Create `.env` file in project root:
  ```bash
  GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
  FIREBASE_PROJECT_ID=your-firebase-project-id
  FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
  FLASK_ENV=development
  FLASK_DEBUG=True
  PORT=5000
  ```

- [ ] Replace placeholders with actual values:
  - [ ] `your_google_maps_api_key_here` → Your Google Maps API key
  - [ ] `your-firebase-project-id` → Your Firebase project ID

### Step 5: Test Locally

- [ ] Start backend server:
  ```bash
  python app.py
  ```
  - [ ] Verify it starts without errors
  - [ ] Check that it's running on `http://localhost:5000`

- [ ] Test backend health endpoint:
  ```bash
  curl http://localhost:5000/api/health
  ```
  - [ ] Should return `{"status":"ok"}`

- [ ] Start frontend (in a new terminal):
  ```bash
  cd frontend
  npm start
  ```
  - [ ] Verify it starts without errors
  - [ ] Check that it opens on `http://localhost:3000`

- [ ] Test the full flow:
  - [ ] Open `http://localhost:3000` in browser
  - [ ] Enter a home address
  - [ ] Upload `sample_addresses.csv` (or create your own test CSV)
  - [ ] Verify route optimization works
  - [ ] Copy the route code
  - [ ] Test retrieving route with the code

---

## Phase 2: Production Deployment

**Reference:** See `DEPLOYMENT.md` for detailed instructions

### Step 6: Deploy Frontend to Firebase Hosting

- [ ] Build the React app:
  ```bash
  cd frontend
  npm run build
  cd ..
  ```

- [ ] Deploy to Firebase Hosting:
  ```bash
  firebase deploy --only hosting
  ```

- [ ] Note your Firebase Hosting URL (e.g., `https://your-project-id.web.app`)

### Step 7: Deploy Backend to Google Cloud Run

- [ ] Install Google Cloud SDK (if not already installed)

- [ ] Authenticate with Google Cloud:
  ```bash
  gcloud auth login
  ```

- [ ] Set your project:
  ```bash
  gcloud config set project YOUR_GOOGLE_CLOUD_PROJECT_ID
  ```

- [ ] Create a Dockerfile (if not exists):
  - [ ] See `DEPLOYMENT.md` for Dockerfile content

- [ ] Build and deploy to Cloud Run:
  ```bash
  export PROJECT_ID=your-google-cloud-project-id
  export SERVICE_NAME=food-delivery-api
  export REGION=us-central1
  
  gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME
  
  gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_MAPS_API_KEY=your_api_key \
    --set-env-vars FIREBASE_PROJECT_ID=your-firebase-project-id
  ```

- [ ] Note your Cloud Run URL (e.g., `https://food-delivery-api-xxxxx.run.app`)

### Step 8: Deploy Scheduled Cleanup Cloud Function

- [ ] Install Python dependencies for Cloud Functions:
  ```bash
  cd functions
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  deactivate
  cd ..
  ```

- [ ] Deploy the Cloud Function:
  ```bash
  firebase deploy --only functions
  ```

- [ ] Verify the function is deployed:
  - [ ] Go to Firebase Console → Functions
  - [ ] You should see `cleanup_expired_routes` function
  - [ ] It should be scheduled to run daily at 2:00 AM UTC

- [ ] (Optional) Test the function manually:
  - [ ] Go to Firebase Console → Functions
  - [ ] Click on `cleanup_expired_routes`
  - [ ] Click "Test" or "Trigger" to run it manually
  - [ ] Check Firestore to verify expired routes are deleted

**Note:** The cleanup function runs automatically once per day. You can monitor its execution in Firebase Console → Functions → Logs.

### Step 9: Update Frontend to Use Production Backend

- [ ] Create `frontend/.env.production`:
  ```bash
  REACT_APP_API_URL=https://your-cloud-run-url.run.app/api
  ```

- [ ] Replace `your-cloud-run-url.run.app` with your actual Cloud Run URL

- [ ] Rebuild and redeploy frontend:
  ```bash
  cd frontend
  npm run build
  cd ..
  firebase deploy --only hosting
  ```

### Step 10: Test Production Deployment

- [ ] Visit your Firebase Hosting URL
- [ ] Test creating a route
- [ ] Test retrieving a route with code
- [ ] Verify routes persist (check Firestore in Firebase Console)
- [ ] Test on mobile device

---

## Phase 3: Optional Enhancements

### Step 11: Set Up Custom Domain (Optional)

- [ ] For Firebase Hosting:
  - [ ] Go to Firebase Console → Hosting
  - [ ] Click "Add custom domain"
  - [ ] Follow verification steps
  - [ ] Update DNS records

- [ ] For Cloud Run:
  - [ ] Go to Cloud Run → Your Service → Manage Custom Domains
  - [ ] Map your domain
  - [ ] Update DNS records

### Step 12: Set Up Monitoring (Recommended)

- [ ] Set up Google Cloud Monitoring alerts:
  - [ ] High error rates
  - [ ] High latency
  - [ ] API quota usage

- [ ] Set up billing alerts:
  - [ ] Google Maps API usage
  - [ ] Cloud Run costs
  - [ ] Firestore usage

### Step 13: Security Hardening (Recommended)

- [ ] Review and update Firestore security rules
- [ ] Set up API key restrictions for production
- [ ] Enable Cloud Run authentication (if needed)
- [ ] Review CORS settings

---

## Troubleshooting Checklist

If something doesn't work:

- [ ] Check that all environment variables are set correctly
- [ ] Verify Google Maps API is enabled and billing is set up
- [ ] Check Firebase service account key is in the correct location
- [ ] Verify Firestore is initialized and rules are published
- [ ] Check Cloud Run logs: `gcloud run services logs read SERVICE_NAME --region REGION`
- [ ] Check Firebase Hosting logs in Firebase Console
- [ ] Verify API URLs are correct in frontend `.env.production`

---

## Quick Reference

**Local Development:**
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`

**Production:**
- Frontend: `https://your-project-id.web.app`
- Backend: `https://your-service-name.run.app`

**Important Files:**
- `.env` - Local environment variables
- `firebase-service-account.json` - Firebase credentials (keep secret!)
- `frontend/.env.production` - Production API URL

**Useful Commands:**
```bash
# Local development
python app.py                    # Start backend
cd frontend && npm start         # Start frontend

# Deployment
firebase deploy --only hosting   # Deploy frontend
gcloud run deploy SERVICE_NAME   # Deploy backend

# Testing
curl http://localhost:5000/api/health  # Test backend
```

---

## Notes

- The app works locally without Firebase (uses in-memory storage), but Firebase is required for production
- Routes expire 24 hours after creation automatically
- Google Maps API has a $200/month free credit
- Monitor your API usage to avoid unexpected costs

