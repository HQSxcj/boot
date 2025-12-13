from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from services.emby_service import EmbyService
from persistence.store import DataStore

emby_bp = Blueprint('emby', __name__, url_prefix='/api/emby')

# Global instances (set during initialization)
_emby_service = None
_store = None


def init_emby_blueprint(store: DataStore):
    """Initialize emby blueprint with required services."""
    global _emby_service, _store
    _store = store
    _emby_service = EmbyService(store)
    emby_bp.store = store
    return emby_bp


@emby_bp.route('/test-connection', methods=['POST'])
@require_auth
def test_emby_connection():
    """Test connection to Emby server."""
    try:
        if not _emby_service:
            return jsonify({
                'success': False,
                'error': 'Emby service not initialized'
            }), 500
        
        result = _emby_service.test_connection()
        
        return jsonify({
            'success': result['success'],
            'data': {
                'success': result['success'],
                'latency': result.get('latency', 0),
                'msg': result.get('msg', '')
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to test connection: {str(e)}'
        }), 500


@emby_bp.route('/scan-missing', methods=['POST'])
@require_auth
def scan_missing_episodes():
    """Scan for missing episodes in Emby."""
    try:
        if not _emby_service:
            return jsonify({
                'success': False,
                'error': 'Emby service not initialized'
            }), 500
        
        result = _emby_service.scan_missing_episodes()
        
        return jsonify({
            'success': result['success'],
            'data': result.get('data', [])
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to scan missing episodes: {str(e)}'
        }), 500


@emby_bp.route('/refresh-library', methods=['POST'])
@require_auth
def refresh_library():
    """刷新 Emby 媒体库"""
    try:
        if not _emby_service:
            return jsonify({
                'success': False,
                'error': 'Emby 服务未初始化'
            }), 500
        
        data = request.get_json() or {}
        library_id = data.get('libraryId')
        
        result = _emby_service.refresh_library(library_id)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'刷新失败: {str(e)}'
        }), 500


@emby_bp.route('/media-info/<item_id>', methods=['GET'])
@require_auth
def get_media_info(item_id: str):
    """获取媒体文件的技术信息（分辨率、编码、字幕等）"""
    try:
        if not _emby_service:
            return jsonify({
                'success': False,
                'error': 'Emby 服务未初始化'
            }), 500
        
        result = _emby_service.get_media_info(item_id)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取媒体信息失败: {str(e)}'
        }), 500


@emby_bp.route('/scan-and-notify', methods=['POST'])
@require_auth
def scan_and_notify():
    """扫描媒体库并获取新增项目（含媒体信息），用于 Bot 通知"""
    try:
        if not _emby_service:
            return jsonify({
                'success': False,
                'error': 'Emby 服务未初始化'
            }), 500
        
        data = request.get_json() or {}
        library_id = data.get('libraryId')
        
        result = _emby_service.scan_and_notify(library_id)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'扫描失败: {str(e)}'
        }), 500


@emby_bp.route('/latest-items', methods=['GET'])
@require_auth
def get_latest_items():
    """获取最新入库的项目"""
    try:
        if not _emby_service:
            return jsonify({
                'success': False,
                'error': 'Emby 服务未初始化'
            }), 500
        
        limit = request.args.get('limit', 10, type=int)
        item_type = request.args.get('type')
        
        result = _emby_service.get_latest_items(limit=limit, item_type=item_type)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取失败: {str(e)}'
        }), 500
