"""
Auth API Routes
Handles authentication status and user info
"""

from flask import Blueprint, jsonify
from splitwise_api.client import SplitwiseClient
from config import Config

auth_bp = Blueprint('auth', __name__)


def get_splitwise_client() -> SplitwiseClient:
    """Get Splitwise client instance"""
    return SplitwiseClient(
        consumer_key=Config.SPLITWISE_CONSUMER_KEY,
        consumer_secret=Config.SPLITWISE_CONSUMER_SECRET,
        api_key=Config.SPLITWISE_API_KEY
    )


@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    try:
        sw_client = get_splitwise_client()
        
        is_authenticated = sw_client.is_authenticated()
        user_info = sw_client.get_current_user_info() if is_authenticated else None
        
        return jsonify({
            'success': True,
            'authenticated': is_authenticated,
            'user': user_info,
            'has_api_key': bool(Config.SPLITWISE_API_KEY),
            'has_gemini_key': bool(Config.GEMINI_API_KEY)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'authenticated': False,
            'error': str(e)
        }), 500


@auth_bp.route('/groups', methods=['GET'])
def get_groups():
    """Get user's Splitwise groups"""
    try:
        sw_client = get_splitwise_client()
        
        if not sw_client.is_authenticated():
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        groups = sw_client.get_groups()
        
        return jsonify({
            'success': True,
            'groups': groups
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/friends', methods=['GET'])
def get_friends():
    """Get user's Splitwise friends"""
    try:
        sw_client = get_splitwise_client()
        
        if not sw_client.is_authenticated():
            return jsonify({
                'success': False,
                'error': 'Not authenticated'
            }), 401
        
        friends = sw_client.get_friends()
        
        return jsonify({
            'success': True,
            'friends': friends
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
