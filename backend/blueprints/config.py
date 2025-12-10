from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from persistence.store import DataStore

config_bp = Blueprint('config', __name__, url_prefix='/api')


def init_config_blueprint(store: DataStore):
    """Initialize config blueprint with data store."""
    config_bp.store = store
    return config_bp


@config_bp.route('/config', methods=['GET'])
@require_auth
def get_config():
    """Get full application configuration."""
    try:
        config = config_bp.store.get_config()
        
        return jsonify({
            'success': True,
            'data': config
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve config: {str(e)}'
        }), 500


@config_bp.route('/config', methods=['PUT'])
@require_auth
def update_config():
    """Update application configuration."""
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Config data is required'
        }), 400
    
    try:
        # Update config in store
        config_bp.store.update_config(data)
        
        # Return updated config
        updated_config = config_bp.store.get_config()
        
        return jsonify({
            'success': True,
            'data': updated_config
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update config: {str(e)}'
        }), 500


@config_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    """Get current user information (alternative endpoint)."""
    from flask_jwt_extended import get_jwt_identity
    
    username = get_jwt_identity()
    two_factor_enabled = config_bp.store.is_two_factor_enabled()
    
    return jsonify({
        'success': True,
        'data': {
            'username': username,
            'twoFactorEnabled': two_factor_enabled
        }
    }), 200
