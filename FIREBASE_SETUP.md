# Firebase Setup Guide

This guide will help you set up Firebase for hosting and storage.

## Prerequisites

1. Node.js installed (for Firebase CLI)
2. Google account
3. Firebase project created

## Step 1: Install Firebase CLI

```bash
npm install -g firebase-tools
```

## Step 2: Login to Firebase

```bash
firebase login
```

## Step 3: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name: `food-delivery-route-optimizer` (or your preferred name)
4. Enable Google Analytics (optional)
5. Click "Create project"

## Step 4: Initialize Firebase in Your Project

```bash
firebase init
```

Select the following:
- ✅ **Hosting**: Configure files for Firebase Hosting
- ✅ **Firestore**: Set up Firestore database
- ✅ **Functions**: Set up Cloud Functions (optional, if you want to migrate backend)

Follow the prompts:
- Select your Firebase project
- For hosting:
  - Public directory: `frontend/build`
  - Single-page app: Yes
  - Set up automatic builds: No (we'll build manually)
- For Firestore:
  - Use default security rules: Yes (we'll update them)
  - Choose locations: Select closest to your users

## Step 5: Update Firebase Project ID

Edit `.firebaserc` and replace `your-firebase-project-id` with your actual Firebase project ID.

# HERE
## Step 6: Set Up Firestore Security Rules

Go to Firebase Console → Firestore Database → Rules and update:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Routes collection - readable by anyone with code, writable by server only
    match /routes/{routeCode} {
      allow read: if true; // Anyone can read with code
      allow write: if false; // Only server can write (via Admin SDK)
    }
  }
}
```

## Step 7: Update Backend to Use Firestore

The backend has been updated to use Firestore. Make sure to:

1. Install Firebase Admin SDK:
   ```bash
   pip install firebase-admin
   ```

2. Set up Firebase Admin credentials:
   - Go to Firebase Console → Project Settings → Service Accounts
   - Click "Generate new private key"
   - Save the JSON file as `firebase-service-account.json` in the project root
   - Add `firebase-service-account.json` to `.gitignore`

## Step 8: Set Environment Variables

For local development, create `.env`:
```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
FIREBASE_PROJECT_ID=your-firebase-project-id
```

For Firebase Functions (if using), set secrets:
```bash
firebase functions:secrets:set GOOGLE_MAPS_API_KEY
```

## Step 9: Deploy

### Deploy Frontend to Firebase Hosting:

```bash
cd frontend
npm run build
cd ..
firebase deploy --only hosting
```

### Deploy Backend (Option 1: Keep Flask on Cloud Run)

See `DEPLOYMENT.md` for Cloud Run deployment instructions.

### Deploy Backend (Option 2: Migrate to Firebase Functions)

If you want to migrate the Flask backend to Firebase Functions, see the `functions/` directory setup.

## Step 10: Update Frontend API URL

After deployment, update the frontend to use the deployed backend URL:

1. Create `frontend/.env.production`:
   ```
   REACT_APP_API_URL=https://your-backend-url.com/api
   ```

2. Rebuild and redeploy:
   ```bash
   cd frontend
   npm run build
   cd ..
   firebase deploy --only hosting
   ```

## Firestore Structure

Routes are stored in the `routes` collection with this structure:

```
routes/
  {routeCode}/
    route: Array
    total_distance: Number
    total_duration: Number
    google_maps_url: String
    created_at: Timestamp
    expires_at: Timestamp
```

Routes automatically expire 24 hours after creation (handled by backend).

## Monitoring

- View logs: `firebase functions:log` (if using Functions)
- View Firestore usage: Firebase Console → Firestore → Usage
- View hosting analytics: Firebase Console → Hosting → Analytics

