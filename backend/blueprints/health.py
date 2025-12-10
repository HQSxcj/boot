from flask import Blueprint, jsonify
import os

health_bp = Blueprint('health', __name__, url_prefix='/api')


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'service': '115-telegram-bot-admin',
            'version': '1.0.0'
        }
    }), 200
