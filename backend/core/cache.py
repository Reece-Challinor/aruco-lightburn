"""
Caching configuration and utilities
"""
from flask_caching import Cache
from functools import wraps
import hashlib
import json

cache = Cache()

def init_cache(app):
    """Initialize cache with Flask app"""
    cache.init_app(app)
    return cache

def make_cache_key(*args, **kwargs):
    """Create a cache key from arguments"""
    key_parts = []
    
    # Add args to key
    for arg in args:
        if isinstance(arg, (dict, list)):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(arg))
    
    # Add kwargs to key
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (dict, list)):
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        else:
            key_parts.append(f"{k}:{v}")
    
    # Create hash of key parts
    key_string = "-".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached_result(timeout=300, key_prefix=''):
    """Decorator for caching function results"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}{f.__name__}:{make_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        return decorated_function
    return decorator

def invalidate_cache(pattern=None):
    """Invalidate cache entries"""
    # Simple cache doesn't support patterns, just clear all
    cache.clear()

class CacheManager:
    """Cache management utilities"""
    
    @staticmethod
    def get_cache_stats():
        """Get cache statistics for simple cache"""
        # Always use simple cache
        return {
            'type': 'simple',
            'total_keys': len(cache.cache._cache) if hasattr(cache.cache, '_cache') else 0
        }