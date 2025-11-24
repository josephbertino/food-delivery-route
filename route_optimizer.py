from typing import List, Dict
from urllib.parse import quote_plus

class RouteOptimizer:
    def __init__(self, gmaps_client):
        self.gmaps = gmaps_client
    
    def optimize_route(self, addresses: List[Dict], home_index: int) -> Dict:
        """
        Optimize route starting and ending at home address using Google Directions API.
        
        Uses Google's Directions API with waypoint optimization to automatically
        determine the optimal order of stops. This is more accurate and efficient
        than solving TSP locally, and handles larger numbers of waypoints better.
        
        Args:
            addresses: List of dicts with 'address' and 'notes' keys
            home_index: Index of the home address in the addresses list
        
        Returns:
            Dict with optimized route, distance, duration, and Google Maps URL
        """
        try:
            # Separate home from other addresses
            home_address = addresses[home_index]
            waypoints = [addr for idx, addr in enumerate(addresses) if idx != home_index]
            
            if not waypoints:
                return {
                    'error': 'No waypoints to visit (only home address found)',
                    'route': [],
                    'total_distance': 0,
                    'total_duration': 0,
                    'google_maps_url': ''
                }
            
            # Prepare waypoint addresses for Directions API
            waypoint_addresses = [addr['address'] for addr in waypoints]
            origin = home_address['address']
            destination = home_address['address']  # Return to home
            
            # Call Directions API with waypoint optimization
            # optimize_waypoints=True tells Google to optimize the order automatically
            directions_result = self.gmaps.directions(
                origin=origin,
                destination=destination,
                waypoints=waypoint_addresses,
                optimize_waypoints=True,  # This is the key parameter!
                mode='walking',
                units='metric'
            )
            
            if not directions_result:
                return {
                    'error': 'No route found. Please check your addresses.',
                    'route': [],
                    'total_distance': 0,
                    'total_duration': 0,
                    'google_maps_url': ''
                }
            
            # Extract route information
            route_data = directions_result[0]
            legs = route_data['legs']
            
            # Get optimized waypoint order from the response
            # The waypoint_order field contains the optimized indices
            waypoint_order = route_data.get('waypoint_order', list(range(len(waypoint_addresses))))
            
            # Build route with step-by-step information
            # The legs array contains: [home->wp1, wp1->wp2, ..., wpN->home]
            # The waypoint_order tells us the optimized order of waypoints
            route = []
            total_distance = 0  # meters
            total_duration = 0  # seconds
            
            # Add home as first step
            route.append({
                'step': 1,
                'address': home_address['address'],
                'notes': home_address.get('notes', 'Home'),
                'is_home': True
            })
            
            # Add waypoints in optimized order
            # The legs are already in the optimized order from the API
            step_num = 2
            for i, leg in enumerate(legs[:-1]):  # All legs except the last (return to home)
                # Get the waypoint index from the optimized order
                waypoint_idx = waypoint_order[i] if i < len(waypoint_order) else i
                waypoint = waypoints[waypoint_idx]
                
                route.append({
                    'step': step_num,
                    'address': waypoint['address'],
                    'notes': waypoint.get('notes', ''),
                    'is_home': False
                })
                
                total_distance += leg['distance']['value']
                total_duration += leg['duration']['value']
                step_num += 1
            
            # Add return to home as final step
            final_leg = legs[-1]  # Last leg is return to home
            route.append({
                'step': step_num,
                'address': home_address['address'],
                'notes': home_address.get('notes', 'Home'),
                'is_home': True
            })
            total_distance += final_leg['distance']['value']
            total_duration += final_leg['duration']['value']
            
            # Build optimized address list for Google Maps URL
            optimized_addresses = [home_address]
            for idx in waypoint_order:
                optimized_addresses.append(waypoints[idx])
            optimized_addresses.append(home_address)  # Return to home
            
            # Generate Google Maps URL with optimized waypoints
            google_maps_url = self._generate_google_maps_url(optimized_addresses)
            
            return {
                'error': None,
                'route': route,
                'total_distance': round(total_distance / 1000, 2),  # Convert to km
                'total_duration': round(total_duration / 60, 1),  # Convert to minutes
                'google_maps_url': google_maps_url
            }
        
        except Exception as e:
            return {
                'error': f"Route optimization failed: {str(e)}",
                'route': [],
                'total_distance': 0,
                'total_duration': 0,
                'google_maps_url': ''
            }
    
    def _generate_google_maps_url(self, addresses: List[Dict]) -> str:
        """Generate Google Maps URL for navigation with optimized route."""
        base_url = "https://www.google.com/maps/dir/"
        
        # Build waypoints string with proper URL encoding
        waypoints = []
        for addr in addresses:
            address = addr['address']
            # Properly URL encode the address
            waypoints.append(quote_plus(address))
        
        url = base_url + '/'.join(waypoints)
        return url

