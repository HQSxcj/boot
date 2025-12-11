from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from persistence.store import DataStore
from services.secret_store import SecretStore
import json

config_bp = Blueprint('config', __name__, url_prefix='/api')


def init_config_blueprint(store: DataStore, secret_store: SecretStore = None):
    """Initialize config blueprint with data store and secret store."""
    config_bp.store = store
    config_bp.secret_store = secret_store
    return config_bp


def _mask_sensitive_value(key: str, value: str) -> str:
    """Create a masked placeholder for sensitive values."""
    if not value:
        return ''
    if len(value) <= 4:
        return '****'
    return value[:2] + '*' * (len(value) - 4) + value[-2:]


def _is_sensitive_field(path: str) -> bool:
    """Check if a config field should be stored in secrets."""
    sensitive_paths = {
        'cloud115.cookies',
        'cloud123.clientSecret',
        'telegram.botToken',
        'emby.apiKey',
        'tmdb.apiKey',
        'openList.password',
        'proxy.password',
        'strm.webdav.password',
        'organize.ai.apiKey',
    }
    return path in sensitive_paths


def _extract_sensitive_fields(config: dict, prefix: str = '') -> dict:
    """Extract sensitive fields from config."""
    sensitive_fields = {}
    
    def traverse(obj, path_prefix):
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{path_prefix}.{key}" if path_prefix else key
                if isinstance(value, dict):
                    traverse(value, path)
                elif _is_sensitive_field(path):
                    sensitive_fields[path] = value
        
    traverse(config, prefix)
    return sensitive_fields


def _apply_masked_config(config: dict, prefix: str = '') -> dict:
    """Apply masked values to sensitive fields."""
    def traverse(obj, path_prefix):
        if isinstance(obj, dict):
            for key, value in obj.items():
                path = f"{path_prefix}.{key}" if path_prefix else key
                if isinstance(value, dict):
                    traverse(value, path)
                elif _is_sensitive_field(path) and value:
                    obj[key] = _mask_sensitive_value(key, str(value))
        
    traverse(config, prefix)
    return config


def _add_session_flags(config: dict, secret_store: SecretStore) -> dict:
    """Add session health flags to config."""
    if not secret_store:
        config['cloud115']['hasValidSession'] = False
        return config
    
    # Check if we have valid 115 cookies
    cookies_json = secret_store.get_secret('cloud115_cookies')
    config['cloud115']['hasValidSession'] = bool(cookies_json)
    
    return config


@config_bp.route('/config', methods=['GET'])
@require_auth
def get_config():
    """Get full application configuration with masked sensitive fields."""
    try:
        config = config_bp.store.get_config()
        
        # Mask sensitive fields
        config = _apply_masked_config(config)
        
        # Add session health flags
        config = _add_session_flags(config, config_bp.secret_store)
        
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
        # Extract sensitive fields
        sensitive_fields = _extract_sensitive_fields(data)
        
        # Store sensitive fields in secret store
        if config_bp.secret_store:
            for field_path, value in sensitive_fields.items():
                if value:
                    config_bp.secret_store.set_secret(f'config_{field_path}', str(value))
        
        # Create a copy for persistence - replace sensitive values with placeholders
        config_to_store = json.loads(json.dumps(data))
        for field_path in sensitive_fields:
            parts = field_path.split('.')
            obj = config_to_store
            for part in parts[:-1]:
                obj = obj.get(part, {})
            if isinstance(obj, dict):
                obj[parts[-1]] = _mask_sensitive_value(parts[-1], str(sensitive_fields[field_path]))
        
        # Update config in store (with masked placeholders)
        config_bp.store.update_config(config_to_store)
        
        # Return updated config with masked values and session flags
        updated_config = config_bp.store.get_config()
        updated_config = _apply_masked_config(updated_config)
        updated_config = _add_session_flags(updated_config, config_bp.secret_store)
        
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
