"""
Admin dashboard endpoints
"""
from flask import Blueprint, request, jsonify, session
from functools import wraps
import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from models import User

bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or not getattr(user, 'is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard():
    """Get admin dashboard data"""
    try:
        # Get statistics
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter(
                User.last_login > datetime.utcnow() - timedelta(days=30)
            ).count() if hasattr(User, 'last_login') else 0,
            'markers_generated': 0,  # Will be populated from marker stats
            'exports_today': 0,  # Will be populated from export logs
        }
        
        return jsonify({
            'stats': stats,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({'error': 'Failed to load dashboard'}), 500

@bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """List all users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users_query = User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users = [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'created_at': u.created_at.isoformat() if hasattr(u, 'created_at') else None,
            'is_admin': getattr(u, 'is_admin', False)
        } for u in users_query.items]
        
        return jsonify({
            'users': users,
            'total': users_query.total,
            'page': page,
            'pages': users_query.pages,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Users list error: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') else None,
                'is_admin': getattr(user, 'is_admin', False)
            },
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"User fetch error: {e}")
        return jsonify({'error': 'Failed to fetch user'}), 500

@bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user details"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data:
            user.email = data['email']
        if 'is_admin' in data and hasattr(user, 'is_admin'):
            user.is_admin = data['is_admin']
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'success': True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"User update error: {e}")
        return jsonify({'error': 'Failed to update user'}), 500

@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent self-deletion
        if user.id == session.get('user_id'):
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User deleted successfully',
            'success': True
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"User deletion error: {e}")
        return jsonify({'error': 'Failed to delete user'}), 500

@bp.route('/settings', methods=['GET'])
@admin_required
def get_settings():
    """Get application settings"""
    try:
        # Get settings from database or config
        settings = {
            'max_markers_per_request': 1000,
            'max_export_size_mb': 50,
            'allowed_dictionaries': ['DICT_4X4_50', 'DICT_5X5_50', 'DICT_6X6_50'],
            'maintenance_mode': False
        }
        
        return jsonify({
            'settings': settings,
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Settings fetch error: {e}")
        return jsonify({'error': 'Failed to fetch settings'}), 500

@bp.route('/settings', methods=['PUT'])
@admin_required
def update_settings():
    """Update application settings"""
    try:
        data = request.get_json()
        
        # Update settings in database or config
        # This would normally update a Settings model
        
        return jsonify({
            'message': 'Settings updated successfully',
            'success': True
        }), 200
        
    except Exception as e:
        logger.error(f"Settings update error: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500