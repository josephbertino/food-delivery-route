import os
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
def _init_firebase():
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        # Try to use service account file first
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
        
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            # For Cloud Run/Firebase Functions, use default credentials
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                # Fallback: use project ID from environment
                project_id = os.getenv('FIREBASE_PROJECT_ID')
                if project_id:
                    firebase_admin.initialize_app(options={'projectId': project_id})
                else:
                    raise ValueError(
                        "Firebase not initialized. Set FIREBASE_SERVICE_ACCOUNT_PATH or FIREBASE_PROJECT_ID, "
                        "or ensure default credentials are available."
                    )
    
    return firestore.client()

# Initialize Firestore client
try:
    db = _init_firebase()
except Exception as e:
    print(f"Warning: Firebase initialization failed: {e}")
    print("Routes will be stored in-memory (not persistent)")
    db = None

class FirestoreStorage:
    """Storage interface for routes using Firestore."""
    
    def __init__(self):
        self.collection = 'routes'
        self.expiration_hours = 24
    
    def _get_expires_at(self):
        """Get expiration timestamp (24 hours from now)."""
        return datetime.utcnow() + timedelta(hours=self.expiration_hours)
    
    def store_route(self, route_code, route_data):
        """Store a route in Firestore with expiration."""
        if not db:
            # Fallback to in-memory storage
            if not hasattr(self, '_in_memory_storage'):
                self._in_memory_storage = {}
            self._in_memory_storage[route_code] = {
                **route_data,
                'expires_at': self._get_expires_at()
            }
            return True
        
        try:
            doc_ref = db.collection(self.collection).document(route_code)
            doc_ref.set({
                **route_data,
                'created_at': firestore.SERVER_TIMESTAMP,
                'expires_at': self._get_expires_at()
            })
            return True
        except Exception as e:
            print(f"Error storing route: {e}")
            return False
    
    def get_route(self, route_code):
        """Retrieve a route from Firestore, checking expiration."""
        if not db:
            # Fallback to in-memory storage
            if not hasattr(self, '_in_memory_storage'):
                return None
            data = self._in_memory_storage.get(route_code)
            if not data:
                return None
            
            # Check expiration
            expires_at = data.get('expires_at')
            if expires_at and expires_at < datetime.utcnow():
                del self._in_memory_storage[route_code]
                return None
            
            # Return route data without metadata
            return {
                'route': data.get('route'),
                'total_distance': data.get('total_distance'),
                'total_duration': data.get('total_duration'),
                'google_maps_url': data.get('google_maps_url')
            }
        
        try:
            doc_ref = db.collection(self.collection).document(route_code)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            
            # Check if expired
            expires_at = data.get('expires_at')
            if expires_at:
                if isinstance(expires_at, datetime):
                    if expires_at < datetime.utcnow():
                        # Delete expired route
                        doc_ref.delete()
                        return None
                elif hasattr(expires_at, 'timestamp'):
                    # Firestore Timestamp object
                    if expires_at.to_datetime() < datetime.utcnow():
                        doc_ref.delete()
                        return None
            
            # Return route data without metadata
            return {
                'route': data.get('route'),
                'total_distance': data.get('total_distance'),
                'total_duration': data.get('total_duration'),
                'google_maps_url': data.get('google_maps_url')
            }
        except Exception as e:
            print(f"Error retrieving route: {e}")
            return None
    
    def delete_route(self, route_code):
        """Delete a route from Firestore."""
        if not db:
            # Fallback to in-memory storage
            if hasattr(self, '_in_memory_storage'):
                self._in_memory_storage.pop(route_code, None)
            return
        
        try:
            db.collection(self.collection).document(route_code).delete()
        except Exception as e:
            print(f"Error deleting route: {e}")

# Global storage instance
storage = FirestoreStorage()

