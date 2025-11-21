import itertools
from typing import List, Dict, Tuple
from urllib.parse import quote_plus

class RouteOptimizer:
    def __init__(self, gmaps_client):
        self.gmaps = gmaps_client
    
    def optimize_route(self, addresses: List[Dict], home_index: int) -> Dict:
        """
        Optimize route starting and ending at home address.
        
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
            
            # Get distance matrix for all points (home + waypoints)
            all_addresses = [home_address] + waypoints
            address_strings = [addr['address'] for addr in all_addresses]
            
            # Get distance matrix using walking mode
            distance_matrix = self.gmaps.distance_matrix(
                address_strings,
                address_strings,
                mode='walking',
                units='metric'
            )
            
            if distance_matrix['status'] != 'OK':
                return {
                    'error': f"Distance Matrix API error: {distance_matrix.get('status', 'Unknown error')}",
                    'route': [],
                    'total_distance': 0,
                    'total_duration': 0,
                    'google_maps_url': ''
                }
            
            # Extract distances and durations
            n = len(all_addresses)
            distances = [[0] * n for _ in range(n)]
            durations = [[0] * n for _ in range(n)]
            
            for i in range(n):
                for j in range(n):
                    element = distance_matrix['rows'][i]['elements'][j]
                    if element['status'] == 'OK':
                        distances[i][j] = element['distance']['value']  # meters
                        durations[i][j] = element['duration']['value']  # seconds
                    else:
                        # If route not found, use a large penalty
                        distances[i][j] = float('inf')
                        durations[i][j] = float('inf')
            
            # Solve TSP: find optimal order of waypoints
            # Home is at index 0, waypoints are at indices 1 to n-1
            waypoint_indices = list(range(1, n))
            
            if len(waypoint_indices) <= 1:
                # Only one waypoint, order is fixed
                optimal_order = [0] + waypoint_indices + [0]
            else:
                # Try all permutations (for small number of waypoints)
                # For larger sets, we'd use a more efficient algorithm
                if len(waypoint_indices) > 8:
                    # Use nearest neighbor heuristic for large sets
                    optimal_order = self._nearest_neighbor_tsp(distances, 0, waypoint_indices)
                else:
                    # Brute force for small sets
                    optimal_order = self._brute_force_tsp(distances, 0, waypoint_indices)
            
            # Build route with addresses and metadata
            route = []
            total_distance = 0
            total_duration = 0
            
            for i, idx in enumerate(optimal_order):
                addr_data = all_addresses[idx]
                route.append({
                    'step': i + 1,
                    'address': addr_data['address'],
                    'notes': addr_data['notes'],
                    'is_home': idx == 0
                })
                
                # Add distance and duration to next step
                if i < len(optimal_order) - 1:
                    next_idx = optimal_order[i + 1]
                    total_distance += distances[idx][next_idx]
                    total_duration += durations[idx][next_idx]
            
            # Generate Google Maps URL
            google_maps_url = self._generate_google_maps_url(all_addresses, optimal_order)
            
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
    
    def _brute_force_tsp(self, distances: List[List[float]], start: int, waypoints: List[int]) -> List[int]:
        """Solve TSP using brute force (only for small sets)."""
        if not waypoints:
            return [start, start]
        
        min_distance = float('inf')
        best_order = None
        
        for perm in itertools.permutations(waypoints):
            order = [start] + list(perm) + [start]
            distance = sum(distances[order[i]][order[i+1]] for i in range(len(order)-1))
            
            if distance < min_distance:
                min_distance = distance
                best_order = order
        
        return best_order
    
    def _nearest_neighbor_tsp(self, distances: List[List[float]], start: int, waypoints: List[int]) -> List[int]:
        """Solve TSP using nearest neighbor heuristic."""
        if not waypoints:
            return [start, start]
        
        unvisited = set(waypoints)
        current = start
        order = [start]
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distances[current][x])
            order.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        order.append(start)  # Return to home
        return order
    
    def _generate_google_maps_url(self, addresses: List[Dict], order: List[int]) -> str:
        """Generate Google Maps URL for navigation."""
        base_url = "https://www.google.com/maps/dir/"
        
        # Build waypoints string with proper URL encoding
        waypoints = []
        for idx in order:
            address = addresses[idx]['address']
            # Properly URL encode the address
            waypoints.append(quote_plus(address))
        
        url = base_url + '/'.join(waypoints)
        return url

