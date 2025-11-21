# Google Maps API Setup Guide

## Required APIs

This project requires the following Google Maps APIs:

1. **Distance Matrix API** - For calculating walking distances between addresses
2. **Directions API** - For generating route directions (optional, currently using URL generation)

## Step-by-Step Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `food-delivery-route-optimizer` (or your preferred name)
4. Click "Create"

### 2. Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for and enable:
   - **Distance Matrix API**
   - **Directions API** (optional but recommended)
   - **Maps JavaScript API** (if you plan to add map visualization)

### 3. Create API Key

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **API Key**
3. Copy the generated API key

### 4. Restrict API Key (Recommended for Security)

1. Click on the API key you just created
2. Under **API restrictions**, select **Restrict key**
3. Check only:
   - Distance Matrix API
   - Directions API
   - Maps JavaScript API (if enabled)
4. Under **Application restrictions**, you can:
   - For development: Select **None** (or **HTTP referrers** with your localhost)
   - For production: Add your Firebase Hosting domain
5. Click **Save**

### 5. Set Up Billing

⚠️ **Important**: Google Maps APIs require billing to be enabled, but they offer a free tier:

- **Distance Matrix API**: 
  - Free: $200 credit/month (covers ~40,000 requests)
  - After free tier: $5.00 per 1,000 requests
  
- **Directions API**:
  - Free: $200 credit/month
  - After free tier: $5.00 per 1,000 requests

1. Go to **Billing** in Google Cloud Console
2. Link a billing account (credit card required)
3. The free $200 credit should cover most usage for this app

### 6. Add API Key to Project

#### For Local Development:
Create a `.env` file in the project root:
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

#### For Firebase:
We'll set this as an environment variable in Firebase Functions (see Firebase setup guide)

## Testing Your API Key

You can test your API key with this curl command:

```bash
curl "https://maps.googleapis.com/maps/api/distancematrix/json?origins=Washington,DC&destinations=New+York+City,NY&mode=walking&key=YOUR_API_KEY"
```

If successful, you'll get a JSON response with distance and duration data.

## Monitoring Usage

1. Go to **APIs & Services** → **Dashboard**
2. View usage metrics for each API
3. Set up alerts in **Billing** → **Budgets & alerts** to monitor costs

## Security Best Practices

1. ✅ Restrict API key to specific APIs
2. ✅ Use application restrictions (HTTP referrers for web, IP for server)
3. ✅ Rotate keys periodically
4. ✅ Monitor usage regularly
5. ✅ Set up billing alerts
6. ❌ Never commit API keys to version control
7. ❌ Never expose API keys in client-side code (use Firebase Functions)

