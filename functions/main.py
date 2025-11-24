"""
Firebase Cloud Functions for Food Delivery Route Optimizer.

This module contains scheduled functions for maintenance tasks.
"""

from firebase_functions import scheduler_fn
from firebase_functions.options import set_global_options
from firebase_admin import initialize_app, firestore
from datetime import datetime, timezone

# For cost control, you can set the maximum number of containers that can be
# running at the same time. This helps mitigate the impact of unexpected
# traffic spikes by instead downgrading performance. This limit is a per-function
# limit. You can override the limit for each function using the max_instances
# parameter in the decorator, e.g. @https_fn.on_request(max_instances=5).
set_global_options(max_instances=10)

# Initialize Firebase Admin SDK
initialize_app()


@scheduler_fn.on_schedule(
    schedule="0 2 * * *",  # Run daily at 2:00 AM UTC
    timezone="UTC",
    memory=256,
    timeout_sec=540,  # 9 minutes (max for 2nd gen functions)
)
def cleanup_expired_routes(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled function to delete expired routes from Firestore.
    
    Runs daily at 2:00 AM UTC to clean up routes that have expired
    (older than 24 hours).
    
    Args:
        event: The scheduled event trigger
    """
    db = firestore.client()
    collection = 'routes'
    now = datetime.now(timezone.utc)
    
    deleted_count = 0
    error_count = 0
    
    try:
        # Query for all routes with expires_at < now
        routes_ref = db.collection(collection)
        expired_routes = routes_ref.where('expires_at', '<', now).stream()
        
        # Delete expired routes in batches
        batch = db.batch()
        batch_count = 0
        max_batch_size = 500  # Firestore batch limit
        
        for doc in expired_routes:
            batch.delete(doc.reference)
            batch_count += 1
            
            # Commit batch when it reaches the limit
            if batch_count >= max_batch_size:
                try:
                    batch.commit()
                    deleted_count += batch_count
                    batch = db.batch()
                    batch_count = 0
                except Exception as e:
                    print(f"Error committing batch: {e}")
                    error_count += batch_count
                    batch = db.batch()
                    batch_count = 0
        
        # Commit remaining deletions
        if batch_count > 0:
            try:
                batch.commit()
                deleted_count += batch_count
            except Exception as e:
                print(f"Error committing final batch: {e}")
                error_count += batch_count
        
        print(f"Cleanup completed: {deleted_count} routes deleted, {error_count} errors")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        raise