"""
MinProxy HTTP Server
Server để điều khiển Chrome Manager từ xa qua HTTP API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import sys
import os
import json
import time

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print(f"[DEBUG] Parent directory: {parent_dir}")
print(f"[DEBUG] Python path: {sys.path[:3]}")

try:
    from core.chrome_manager import ChromeProfileManager
    from core.tiles.tile_minproxy import start_minproxy_livestream_batch, get_minproxy_active_sessions
    print("[DEBUG] Imports successful")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    print(f"[ERROR] Make sure you run the server from the project root or server directory")
    print(f"[ERROR] Current working directory: {os.getcwd()}")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global manager instance
manager = None
active_sessions = {}

def init_manager():
    """Initialize Chrome Profile Manager"""
    global manager
    if manager is None:
        manager = ChromeProfileManager()
        print("✅ Chrome Manager initialized")
    return manager

@app.route('/')
def index():
    """Home page"""
    return jsonify({
        'status': 'running',
        'message': 'MinProxy Server is running',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'Server info',
            'GET /health': 'Health check',
            'GET /profiles': 'List all profiles',
            'POST /minproxy/start': 'Start livestream viewing',
            'GET /minproxy/sessions': 'Get active sessions',
            'POST /minproxy/stop': 'Stop sessions',
            'GET /config': 'Get MinProxy config',
            'POST /config': 'Update MinProxy config'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'manager_initialized': manager is not None
    })

@app.route('/profiles', methods=['GET'])
def list_profiles():
    """List all Chrome profiles"""
    try:
        mgr = init_manager()
        profiles = mgr.list_profiles()
        
        return jsonify({
            'success': True,
            'profiles': profiles,
            'count': len(profiles)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/minproxy/start', methods=['POST'])
def start_minproxy():
    """
    Start MinProxy livestream viewing
    
    Request body:
    {
        "api_key": "your_api_key",
        "livestream_url": "https://www.tiktok.com/@username/live",
        "profile_names": ["Profile_1", "Profile_2"],
        "duration_minutes": 60,
        "auto_interact": false,
        "delay_between_requests": 1.0
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        api_key = data.get('api_key')
        livestream_url = data.get('livestream_url')
        profile_names = data.get('profile_names', [])
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'api_key is required'
            }), 400
        
        if not livestream_url:
            return jsonify({
                'success': False,
                'error': 'livestream_url is required'
            }), 400
        
        if not profile_names:
            return jsonify({
                'success': False,
                'error': 'profile_names is required'
            }), 400
        
        # Optional parameters
        duration_minutes = data.get('duration_minutes', 60)
        auto_interact = data.get('auto_interact', False)
        delay_between_requests = data.get('delay_between_requests', 1.0)
        
        # Start livestream viewing
        print(f"🚀 Starting MinProxy for {len(profile_names)} profiles...")
        
        results = start_minproxy_livestream_batch(
            api_key=api_key,
            livestream_url=livestream_url,
            profile_names=profile_names,
            duration_minutes=duration_minutes,
            auto_interact=auto_interact,
            delay_between_requests=delay_between_requests
        )
        
        # Process results
        success_count = sum(1 for _, s, _ in results if s)
        failed_count = len(results) - success_count
        
        response = {
            'success': True,
            'total': len(results),
            'success_count': success_count,
            'failed_count': failed_count,
            'results': [
                {
                    'profile': profile,
                    'success': success,
                    'message': message
                }
                for profile, success, message in results
            ]
        }
        
        print(f"✅ Completed: {success_count}/{len(results)} successful")
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/minproxy/sessions', methods=['GET'])
def get_sessions():
    """Get active MinProxy sessions"""
    try:
        api_key = request.args.get('api_key')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'api_key is required'
            }), 400
        
        success, sessions = get_minproxy_active_sessions(api_key)
        
        if success:
            return jsonify({
                'success': True,
                'sessions': sessions,
                'count': len(sessions)
            })
        else:
            return jsonify({
                'success': False,
                'error': sessions.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/minproxy/stop', methods=['POST'])
def stop_sessions():
    """
    Stop MinProxy sessions
    
    Request body:
    {
        "api_key": "your_api_key",
        "session_ids": ["session_1", "session_2"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        api_key = data.get('api_key')
        session_ids = data.get('session_ids', [])
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'api_key is required'
            }), 400
        
        if not session_ids:
            return jsonify({
                'success': False,
                'error': 'session_ids is required'
            }), 400
        
        from core.tiles.tile_minproxy import stop_minproxy_sessions
        
        results = stop_minproxy_sessions(api_key, session_ids)
        
        success_count = sum(1 for _, s, _ in results if s)
        
        return jsonify({
            'success': True,
            'total': len(results),
            'success_count': success_count,
            'results': [
                {
                    'session_id': session_id,
                    'success': success,
                    'message': message
                }
                for session_id, success, message in results
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Get MinProxy configuration"""
    try:
        config_path = os.path.join('config', 'minproxy_config.json')
        
        if not os.path.exists(config_path):
            return jsonify({
                'success': False,
                'error': 'Config file not found'
            }), 404
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Mask API key
        if 'api_key' in config:
            config['api_key_masked'] = config['api_key'][:10] + '...' + config['api_key'][-10:]
            del config['api_key']
        
        return jsonify({
            'success': True,
            'config': config
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/config', methods=['POST'])
def update_config():
    """
    Update MinProxy configuration
    
    Request body:
    {
        "api_key": "new_api_key",
        "default_duration_minutes": 60,
        "default_auto_interact": false,
        "delay_between_requests": 1.0
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        config_path = os.path.join('config', 'minproxy_config.json')
        
        # Load existing config
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # Update config
        if 'api_key' in data:
            config['api_key'] = data['api_key']
        if 'base_url' in data:
            config['base_url'] = data['base_url']
        if 'default_duration_minutes' in data:
            config['default_duration_minutes'] = data['default_duration_minutes']
        if 'default_auto_interact' in data:
            config['default_auto_interact'] = data['default_auto_interact']
        if 'delay_between_requests' in data:
            config['delay_between_requests'] = data['delay_between_requests']
        
        # Save config
        os.makedirs('config', exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Config updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask server"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           MinProxy HTTP Server                               ║
╚══════════════════════════════════════════════════════════════╝

🚀 Server starting...
📍 Host: {host}
🔌 Port: {port}
🌐 URL: http://{host}:{port}

📋 Available endpoints:
   GET  /                    - Server info
   GET  /health              - Health check
   GET  /profiles            - List profiles
   POST /minproxy/start      - Start livestream
   GET  /minproxy/sessions   - Get sessions
   POST /minproxy/stop       - Stop sessions
   GET  /config              - Get config
   POST /config              - Update config

Press Ctrl+C to stop the server
""")
    
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MinProxy HTTP Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, debug=args.debug)
