"""
Marker repository for database operations using SQLAlchemy
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import db
from models import CalibrationPattern
import json

logger = logging.getLogger(__name__)

class MarkerRepository:
    """Repository for marker database operations using PostgreSQL"""
    
    def save_marker(self, marker_data: Dict) -> int:
        """Save marker to database"""
        try:
            # Create new calibration pattern record
            pattern = CalibrationPattern(
                pattern_type='aruco_marker',
                pattern_name=f"ArUCO_{marker_data.get('dict', 'unknown')}_{marker_data.get('id', 0)}",
                physical_width_mm=marker_data.get('size', 20),
                physical_height_mm=marker_data.get('size', 20),
                marker_size_mm=marker_data.get('size', 20),
                dictionary_type=marker_data.get('dict', 'unknown'),
                total_markers=1,
                first_marker_id=marker_data.get('id', 0),
                calibration_data=marker_data,
                grid_size_x=1,
                grid_size_y=1
            )
            
            db.session.add(pattern)
            db.session.commit()
            
            logger.info(f"Saved marker {pattern.id} to database")
            return pattern.id
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error saving marker: {e}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving marker: {e}")
            raise
    
    def get_marker(self, marker_id: int) -> Optional[Dict]:
        """Get marker by ID"""
        try:
            pattern = CalibrationPattern.query.get(marker_id)
            if pattern:
                return pattern.to_dict()
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving marker: {e}")
            return None
    
    def list_markers(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List markers with optional filters"""
        try:
            query = CalibrationPattern.query.filter_by(pattern_type='aruco_marker')
            
            if filters:
                if 'dictionary' in filters:
                    query = query.filter_by(dictionary_type=filters['dictionary'])
                
                if 'start_date' in filters:
                    query = query.filter(CalibrationPattern.created_at >= filters['start_date'])
                
                if 'end_date' in filters:
                    query = query.filter(CalibrationPattern.created_at <= filters['end_date'])
            
            patterns = query.all()
            return [p.to_dict() for p in patterns]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing markers: {e}")
            return []
    
    def update_marker(self, marker_id: int, update_data: Dict) -> bool:
        """Update marker data"""
        try:
            pattern = CalibrationPattern.query.get(marker_id)
            if pattern:
                # Update calibration data
                current_data = pattern.calibration_data or {}
                current_data.update(update_data)
                pattern.calibration_data = current_data
                
                db.session.commit()
                logger.info(f"Updated marker {marker_id}")
                return True
            return False
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error updating marker: {e}")
            return False
    
    def delete_marker(self, marker_id: int) -> bool:
        """Delete marker"""
        try:
            pattern = CalibrationPattern.query.get(marker_id)
            if pattern:
                db.session.delete(pattern)
                db.session.commit()
                logger.info(f"Deleted marker {marker_id}")
                return True
            return False
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error deleting marker: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get marker statistics from database"""
        try:
            total = CalibrationPattern.query.filter_by(pattern_type='aruco_marker').count()
            
            if total == 0:
                return {
                    'total_markers': 0,
                    'dictionaries': {},
                    'latest_marker': None
                }
            
            # Get dictionary counts
            from sqlalchemy import func
            dict_counts = db.session.query(
                CalibrationPattern.dictionary_type, 
                func.count(CalibrationPattern.id)
            ).filter_by(
                pattern_type='aruco_marker'
            ).group_by(
                CalibrationPattern.dictionary_type
            ).all()
            
            dictionaries = {dict_type: count for dict_type, count in dict_counts}
            
            # Get latest marker
            latest = CalibrationPattern.query.filter_by(
                pattern_type='aruco_marker'
            ).order_by(
                CalibrationPattern.created_at.desc()
            ).first()
            
            return {
                'total_markers': total,
                'dictionaries': dictionaries,
                'latest_marker': latest.to_dict() if latest else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting statistics: {e}")
            return {
                'total_markers': 0,
                'dictionaries': {},
                'latest_marker': None
            }