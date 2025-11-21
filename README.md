# Food Delivery Route Optimizer

A tool to optimize walking routes for food delivery, starting and ending from a 'home' location.

## Features

- Upload CSV with addresses to visit and optional additional data per address
- Specify starting and ending point
- Optimize route using Google Maps APIs (shortest walking distance)
- Display optimal route with notes/metadata
- Generate Google Maps navigation link
- Mobile-friendly interface with unique code sharing

## Setup

### Prerequisites

- Python 3.8+
- Node.js 14+
- Google Maps API key with Distance Matrix API and Directions API enabled

### Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. Set up Google Maps API:
   - See [GOOGLE_MAPS_SETUP.md](GOOGLE_MAPS_SETUP.md) for detailed instructions
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the following APIs:
     - Distance Matrix API
     - Directions API
   - Create credentials (API Key)
   - (Optional) Restrict the API key to the enabled APIs for security

# HERE
4. Set up Firebase (for route storage):
   - See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed instructions
   - Install Firebase CLI: `npm install -g firebase-tools`
   - Run `firebase login` and `firebase init`
   - Enable Firestore Database
   - Download service account key and save as `firebase-service-account.json`

5. Create `.env` file in the root directory:
   ```bash
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
   FIREBASE_PROJECT_ID=your-firebase-project-id
   FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
   FLASK_ENV=development
   FLASK_DEBUG=True
   PORT=5000
   ```
   
   **Note:** For local development without Firebase, the app will use in-memory storage (routes won't persist).

### Running the Application

1. Start the backend server:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

2. Start the frontend (in a new terminal):
   ```bash
   cd frontend
   npm start
   ```
   The frontend will run on `http://localhost:3000`

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. **Create a Route:**
   - Click on "Create Route" tab
   - Enter your home address in the form
   - Upload a CSV file with delivery addresses
   - Wait for the route to be optimized
   - Copy the generated route code

2. **View Route on Mobile:**
   - Click on "Enter Code" tab
   - Enter the 8-character route code
   - View the optimized route
   - Click "Open in Google Maps" to start navigation

## CSV Format

The CSV can have a flexible format. Examples:

**Without header (recommended):**
```csv
123 Main St, Customer 1
456 Oak Ave, Customer 2, Special instructions
789 Pine Rd
321 Elm Street
```

**With header (optional):**
```csv
address,notes,instructions
123 Main St, Customer 1, Ring doorbell
456 Oak Ave, Customer 2, Leave at door
789 Pine Rd, Customer 3
```

**Key points:**
- First column must contain the address
- Additional columns are optional (notes, metadata, etc.)
- Header row is optional - the app auto-detects it
- Empty rows are ignored
- You must manually enter your HOME address in the form (it's not read from the CSV)
- The route will start and end at the Home address you provide
- All other addresses from the CSV will be optimized for shortest walking distance

## How It Works

1. **CSV Parsing:** The app reads addresses from the CSV (first column = address, additional columns = notes). The user manually enters the HOME address separately.
2. **Distance Matrix:** Uses Google Distance Matrix API to get walking distances between all points
3. **Route Optimization:** Solves the Traveling Salesman Problem (TSP) to find the optimal order
   - For ≤8 waypoints: Uses brute force (guaranteed optimal)
   - For >8 waypoints: Uses nearest neighbor heuristic (fast approximation)
4. **Route Generation:** Creates a step-by-step route with distances and durations
5. **Google Maps Integration:** Generates a Google Maps URL for real-time navigation

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/optimize-route` - Upload CSV and optimize route
- `GET /api/route/<route_code>` - Retrieve route by code

## Notes

- Routes are stored in Firebase Firestore and persist across server restarts
- Routes automatically expire 24 hours after creation 
- For production, consider using a database (e.g., SQLite, PostgreSQL)
- Google Maps API has usage limits and costs - check your quota
- The app is optimized for walking routes, but can be modified for other modes

## Troubleshooting

**"GOOGLE_MAPS_API_KEY environment variable is required"**
- Make sure you created a `.env` file with your API key

**"Distance Matrix API error"**
- Check that Distance Matrix API is enabled in Google Cloud Console
- Verify your API key is correct
- Check your API quota/billing

**"Route not found"**
- Route codes expire 24 hours after generation
- Make sure you're using the correct 8-character code
- Check that the route hasn't expired