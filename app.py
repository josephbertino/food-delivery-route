import os
import csv
import io
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import googlemaps
from route_optimizer import RouteOptimizer
from firestore_storage import storage

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize Google Maps client
api_key = os.getenv('GOOGLE_MAPS_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required. Please set it in your .env file.")
gmaps = googlemaps.Client(key=api_key)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

def _is_likely_address(text):
    """Check if text looks like an address (contains numbers or common address words)."""
    text_lower = text.lower().strip()
    # Check for numbers (addresses usually have numbers)
    has_number = any(char.isdigit() for char in text)
    # Check for common address indicators
    address_indicators = ['street', 'st', 'avenue', 'ave', 'road', 'rd', 'drive', 'dr', 'lane', 'ln', 'blvd', 'boulevard', 'way', 'court', 'ct']
    has_indicator = any(indicator in text_lower for indicator in address_indicators)
    return has_number or has_indicator

def _parse_csv(stream):
    """Parse CSV with flexible format - first column is address, optional header detection."""
    csv_reader = csv.reader(stream)
    rows = list(csv_reader)
    
    if not rows:
        return [], True  # Empty file, has_header = True by default
    
    # Check if first row looks like a header (doesn't look like an address)
    first_row = rows[0]
    first_cell = first_row[0].strip() if first_row else ""
    has_header = not _is_likely_address(first_cell)
    
    # Skip header if detected
    data_rows = rows[1:] if has_header else rows
    
    addresses = []
    for row in data_rows:
        if not row or not row[0].strip():
            continue
        
        # First column is always the address
        address = row[0].strip()
        
        # Additional columns are treated as notes/metadata
        notes = ', '.join([col.strip() for col in row[1:] if col.strip()])
        
        addresses.append({
            'address': address,
            'notes': notes
        })
    
    return addresses, has_header

@app.route('/api/optimize-route', methods=['POST'])
def optimize_route():
    try:
        # Get home address from form data
        home_address = request.form.get('home_address', '').strip()
        if not home_address:
            return jsonify({'error': 'Home address is required'}), 400
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read CSV content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        addresses, has_header = _parse_csv(stream)
        
        if not addresses:
            return jsonify({'error': 'No valid addresses found in CSV'}), 400
        
        # Add home address to the list for optimization
        # Home will be at index 0
        all_addresses = [{'address': home_address, 'notes': 'Home'}] + addresses
        home_index = 0
        
        # Optimize route
        optimizer = RouteOptimizer(gmaps)
        result = optimizer.optimize_route(all_addresses, home_index)
        
        if result['error']:
            return jsonify({'error': result['error']}), 500
        
        # Generate unique code
        route_code = str(uuid.uuid4())[:8].upper()
        
        # Store route in Firestore (with 24-hour expiration)
        route_data = {
            'route': result['route'],
            'total_distance': result['total_distance'],
            'total_duration': result['total_duration'],
            'google_maps_url': result['google_maps_url']
        }
        storage.store_route(route_code, route_data)
        
        return jsonify({
            'route_code': route_code,
            'route': result['route'],
            'total_distance': result['total_distance'],
            'total_duration': result['total_duration'],
            'google_maps_url': result['google_maps_url']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/route/<route_code>', methods=['GET'])
def get_route(route_code):
    route_code = route_code.upper()
    route_data = storage.get_route(route_code)
    
    if not route_data:
        return jsonify({'error': 'Route not found or expired'}), 404
    
    return jsonify(route_data)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True', port=port)

