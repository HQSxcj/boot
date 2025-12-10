from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
from middleware.auth import require_auth
from persistence.store import DataStore

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def init_auth_blueprint(store: DataStore):
    """Initialize auth blueprint with data store."""
    auth_bp.store = store
    return auth_bp


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint - validates username/password and returns JWT."""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'error': 'Username and password are required'
        }), 400
    
    username = data['username']
    password = data['password']
    
    # Get admin credentials from store
    admin = auth_bp.store.get_admin_credentials()
    
    # If no password is set yet, set it on first login
    if not admin.get('password_hash'):
        password_hash = generate_password_hash(password)
        auth_bp.store.update_admin_password(password_hash)
        
        # Create access token
        access_token = create_access_token(identity=username)
        
        return jsonify({
            'success': True,
            'data': {
                'token': access_token,
                'username': username,
                'requires2FA': False
            }
        }), 200
    
    # Check username and password
    if username != admin.get('username') or not check_password_hash(admin.get('password_hash'), password):
        return jsonify({
            'success': False,
            'error': 'Invalid credentials'
        }), 401
    
    # Check if 2FA is enabled
    requires_2fa = auth_bp.store.is_two_factor_enabled()
    
    # Create access token
    access_token = create_access_token(identity=username)
    
    return jsonify({
        'success': True,
        'data': {
            'token': access_token,
            'username': username,
            'requires2FA': requires_2fa
        }
    }), 200


@auth_bp.route('/verify-otp', methods=['POST'])
@require_auth
def verify_otp():
    """Verify OTP code for 2FA."""
    data = request.get_json()
    
    if not data or 'code' not in data:
        return jsonify({
            'success': False,
            'error': 'OTP code is required'
        }), 400
    
    code = data['code']
    
    # Get 2FA secret
    secret = auth_bp.store.get_two_factor_secret()
    
    if not secret:
        return jsonify({
            'success': False,
            'error': '2FA is not enabled'
        }), 400
    
    # Verify OTP
    totp = pyotp.TOTP(secret)
    is_valid = totp.verify(code, valid_window=1)
    
    if not is_valid:
        return jsonify({
            'success': False,
            'error': 'Invalid OTP code'
        }), 401
    
    return jsonify({
        'success': True,
        'data': {
            'verified': True
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    """Get current user information."""
    username = get_jwt_identity()
    two_factor_enabled = auth_bp.store.is_two_factor_enabled()
    
    return jsonify({
        'success': True,
        'data': {
            'username': username,
            'twoFactorEnabled': two_factor_enabled
        }
    }), 200


@auth_bp.route('/setup-2fa', methods=['POST'])
@require_auth
def setup_2fa():
    """Setup 2FA by generating and storing a new secret."""
    # Generate new secret
    secret = pyotp.random_base32()
    
    # Store secret
    auth_bp.store.update_two_factor_secret(secret)
    
    # Generate provisioning URI for QR code
    username = get_jwt_identity()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=username,
        issuer_name='115 Telegram Bot'
    )
    
    return jsonify({
        'success': True,
        'data': {
            'secret': secret,
            'qrCodeUri': provisioning_uri
        }
    }), 200
