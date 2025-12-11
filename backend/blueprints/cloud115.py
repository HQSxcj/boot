from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from middleware.auth import require_auth
from p115_bridge import get_p115_service
from services.secret_store import SecretStore
import json

cloud115_bp = Blueprint('cloud115', __name__, url_prefix='/api/115')

# These will be set by init_cloud115_blueprint
_secret_store = None
_p115_service = None


def init_cloud115_blueprint(secret_store: SecretStore):
    """Initialize cloud115 blueprint with secret store."""
    global _secret_store, _p115_service
    _secret_store = secret_store
    _p115_service = get_p115_service()
    return cloud115_bp


@cloud115_bp.route('/login/qrcode', methods=['POST'])
@require_auth
def start_qr_login():
    """Start a QR code login session for 115 cloud."""
    try:
        data = request.get_json() or {}
        
        login_app = data.get('loginApp', 'web')
        login_method = data.get('loginMethod', 'cookie')
        
        if login_method not in ['cookie', 'open_app']:
            return jsonify({
                'success': False,
                'error': 'Invalid login method'
            }), 400
        
        # Start QR login
        result = _p115_service.start_qr_login(
            login_app=login_app,
            login_method=login_method
        )
        
        if 'error' in result and result.get('success') == False:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to start QR login')
            }), 400
        
        return jsonify({
            'success': True,
            'data': {
                'sessionId': result['sessionId'],
                'qrcode': result['qrcode'],
                'loginMethod': result['login_method'],
                'loginApp': result['login_app']
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start QR login: {str(e)}'
        }), 500


@cloud115_bp.route('/login/status/<session_id>', methods=['GET'])
@require_auth
def poll_login_status(session_id: str):
    """Poll QR code login status and persist cookies on success."""
    try:
        result = _p115_service.poll_login_status(session_id)
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Login failed'),
                'status': result.get('status', 'error')
            }), 400
        
        if result.get('status') == 'success':
            # Persist cookies to secret store
            cookies = result.get('cookies', {})
            
            if not cookies:
                return jsonify({
                    'success': False,
                    'error': 'No cookies received from login'
                }), 400
            
            # Store cookies encrypted
            cookies_json = json.dumps(cookies)
            _secret_store.set_secret('cloud115_cookies', cookies_json)
            
            # Also store session metadata
            metadata = {
                'login_method': _p115_service._session_cache.get(session_id, {}).get('login_method'),
                'login_app': _p115_service._session_cache.get(session_id, {}).get('login_app'),
                'logged_in_at': __import__('datetime').datetime.now().isoformat()
            }
            _secret_store.set_secret('cloud115_session_metadata', json.dumps(metadata))
            
            # Clear session
            _p115_service.clear_session(session_id)
            
            return jsonify({
                'success': True,
                'data': {
                    'status': 'success',
                    'message': 'Login successful and cookies stored'
                }
            }), 200
        
        # Still waiting
        return jsonify({
            'success': True,
            'data': {
                'status': result.get('status', 'waiting'),
                'message': 'Waiting for user to scan QR code'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to poll status: {str(e)}'
        }), 500


@cloud115_bp.route('/login/cookie', methods=['POST'])
@require_auth
def ingest_cookies():
    """Manually ingest and validate 115 cookies."""
    try:
        data = request.get_json()
        
        if not data or 'cookies' not in data:
            return jsonify({
                'success': False,
                'error': 'Cookies are required'
            }), 400
        
        cookies = data.get('cookies')
        
        if not isinstance(cookies, dict):
            try:
                if isinstance(cookies, str):
                    cookies = json.loads(cookies)
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid cookies format'
                }), 400
        
        # Validate cookies
        is_valid = _p115_service.validate_cookies(cookies)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired cookies'
            }), 401
        
        # Store cookies encrypted
        cookies_json = json.dumps(cookies)
        _secret_store.set_secret('cloud115_cookies', cookies_json)
        
        # Store metadata
        metadata = {
            'login_method': 'manual_import',
            'login_app': data.get('loginApp', 'web'),
            'logged_in_at': __import__('datetime').datetime.now().isoformat()
        }
        _secret_store.set_secret('cloud115_session_metadata', json.dumps(metadata))
        
        return jsonify({
            'success': True,
            'data': {
                'message': 'Cookies validated and stored successfully'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to ingest cookies: {str(e)}'
        }), 500


@cloud115_bp.route('/session', methods=['GET'])
@require_auth
def get_session_health():
    """Report 115 session health status."""
    try:
        # Try to get stored cookies
        cookies_json = _secret_store.get_secret('cloud115_cookies')
        
        if not cookies_json:
            return jsonify({
                'success': True,
                'data': {
                    'hasValidSession': False,
                    'message': 'No 115 session configured'
                }
            }), 200
        
        try:
            cookies = json.loads(cookies_json)
        except json.JSONDecodeError:
            return jsonify({
                'success': True,
                'data': {
                    'hasValidSession': False,
                    'message': 'Invalid session data'
                }
            }), 200
        
        # Check session health
        health = _p115_service.get_session_health(cookies)
        
        return jsonify({
            'success': True,
            'data': {
                'hasValidSession': health.get('hasValidSession', False),
                'lastCheck': health.get('lastCheck'),
                'message': 'Session check complete'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to check session: {str(e)}'
        }), 500
