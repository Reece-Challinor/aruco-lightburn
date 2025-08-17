"""
Marker repository for database operations
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class MarkerRepository:
    """Repository for marker database operations"""
    
    def __init__(self):
        # In a full implementation, this would use SQLAlchemy models
        # For now, we'll use in-memory storage
        self.markers = {}
        self.marker_counter = 0
    
    def save_marker(self, marker_data: Dict) -> int:
        """Save marker to database"""
        try:
            self.marker_counter += 1
            marker_id = self.marker_counter
            
            self.markers[marker_id] = {
                **marker_data,
                'db_id': marker_id,
                'created_at': datetime.utcnow().isoformat()
            }
            
            return marker_id
            
        except Exception as e:
            logger.error(f"Error saving marker: {e}")
            raise
    
    def get_marker(self, marker_id: int) -> Optional[Dict]:
        """Get marker by ID"""
        return self.markers.get(marker_id)
    
    def list_markers(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List markers with optional filters"""
        markers = list(self.markers.values())
        
        if filters:
            # Apply filters
            if 'dictionary' in filters:
                markers = [m for m in markers if m.get('dict') == filters['dictionary']]
            
            if 'start_date' in filters:
                markers = [m for m in markers 
                          if m.get('created_at', '') >= filters['start_date']]
            
            if 'end_date' in filters:
                markers = [m for m in markers 
                          if m.get('created_at', '') <= filters['end_date']]
        
        return markers
    
    def update_marker(self, marker_id: int, update_data: Dict) -> bool:
        """Update marker data"""
        if marker_id in self.markers:
            self.markers[marker_id].update(update_data)
            self.markers[marker_id]['updated_at'] = datetime.utcnow().isoformat()
            return True
        return False
    
    def delete_marker(self, marker_id: int) -> bool:
        """Delete marker"""
        if marker_id in self.markers:
            del self.markers[marker_id]
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get marker statistics"""
        if not self.markers:
            return {
                'total_markers': 0,
                'dictionaries': [],
                'latest_marker': None
            }
        
        dictionaries = {}
        for marker in self.markers.values():
            dict_name = marker.get('dict', 'unknown')
            dictionaries[dict_name] = dictionaries.get(dict_name, 0) + 1
        
        latest_marker = max(self.markers.values(), 
                           key=lambda m: m.get('created_at', ''))
        
        return {
            'total_markers': len(self.markers),
            'dictionaries': dictionaries,
            'latest_marker': latest_marker
        }