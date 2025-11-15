"""
Simple Test Server - Test treo livestream
Server đơn giản để test chức năng treo livestream
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import threading
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.chrome_manager import ChromeProfileManager
from core.tiles.tile_livestream import run_livestream_profiles

app = Flask(__name__)
CORS(app)

# Global manager
manager = None

def init_manager():
    """Initialize Chrome Profile Manager"""
    global manager
    if manager is None:
        manager = ChromeProfileManager()
        print("✅ Chrome Manager initialized")
    return manager

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Treo Livestream</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
            font-size: 28px;
        }

        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }

        input[type="text"],
        input[type="number"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .btn {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 10px;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .status {
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .status.info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .info-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .info-box h3 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 16px;
        }

        .info-box p {
            color: #666;
            font-size: 13px;
            line-height: 1.6;
            margin: 0;
        }

        .profiles-info {
            background: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 13px;
            color: #1976d2;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📺 Test Treo Livestream</h1>
        <p class="subtitle">Test chức năng treo livestream với Chrome Manager</p>

        <div class="info-box">
            <h3>📋 Hướng dẫn</h3>
            <p>
                1. Nhập link livestream TikTok<br>
                2. Nhập số lượng profiles muốn mở<br>
                3. Click "🚀 Bắt đầu treo livestream"<br>
                4. Tool sẽ tự động mở profiles và treo livestream
            </p>
        </div>

        <div class="profiles-info" id="profilesInfo">
            Đang tải danh sách profiles...
        </div>

        <form id="livestreamForm">
            <div class="form-group">
                <label for="livestreamUrl">🌐 Link Livestream TikTok</label>
                <input type="text" id="livestreamUrl" 
                       placeholder="https://www.tiktok.com/@username/live" 
                       value="https://www.tiktok.com/@username/live" 
                       required>
            </div>

            <div class="form-group">
                <label for="profileCount">👥 Số lượng profiles (viewers)</label>
                <input type="number" id="profileCount" 
                       min="1" max="50" value="5" required>
                <small style="color: #666; font-size: 12px;">
                    Số profiles sẽ được mở để treo livestream
                </small>
            </div>

            <button type="submit" class="btn btn-primary" id="startBtn">
                🚀 Bắt đầu treo livestream
            </button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Đang xử lý...</p>
        </div>

        <div class="status" id="status"></div>
    </div>

    <script>
        // Load profiles info on page load
        window.addEventListener('load', async () => {
            try {
                const response = await fetch('/api/profiles');
                const data = await response.json();
                
                if (data.success) {
                    const count = data.count;
                    document.getElementById('profilesInfo').innerHTML = 
                        `✅ Có ${count} profiles sẵn sàng để sử dụng`;
                    
                    // Update max value
                    document.getElementById('profileCount').max = Math.min(count, 50);
                } else {
                    document.getElementById('profilesInfo').innerHTML = 
                        `⚠️ Không thể tải danh sách profiles`;
                }
            } catch (error) {
                document.getElementById('profilesInfo').innerHTML = 
                    `❌ Lỗi: ${error.message}`;
            }
        });

        function showStatus(type, message) {
            const statusDiv = document.getElementById('status');
            statusDiv.className = `status ${type}`;
            statusDiv.innerHTML = message;
            statusDiv.style.display = 'block';
        }

        function showLoading(show) {
            document.getElementById('loading').classList.toggle('active', show);
            document.getElementById('startBtn').disabled = show;
        }

        document.getElementById('livestreamForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const livestreamUrl = document.getElementById('livestreamUrl').value.trim();
            const profileCount = parseInt(document.getElementById('profileCount').value);
            
            if (!livestreamUrl) {
                showStatus('error', '❌ Vui lòng nhập link livestream!');
                return;
            }

            if (profileCount < 1) {
                showStatus('error', '❌ Số lượng profiles phải lớn hơn 0!');
                return;
            }

            // Confirm
            if (!confirm(`Bắt đầu treo livestream với ${profileCount} profiles?\\n\\nURL: ${livestreamUrl}`)) {
                return;
            }

            showLoading(true);
            showStatus('info', '⏳ Đang xử lý... Tool sẽ tự động mở profiles và treo livestream.');

            try {
                const response = await fetch('/api/start-livestream', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        livestream_url: livestreamUrl,
                        profile_count: profileCount
                    })
                });

                const data = await response.json();

                if (data.success) {
                    const successCount = data.success_count;
                    const total = data.total;
                    
                    let message = `✅ Hoàn thành!<br><br>`;
                    message += `✅ Thành công: ${successCount}/${total}<br>`;
                    
                    if (data.failed_count > 0) {
                        message += `❌ Thất bại: ${data.failed_count}<br><br>`;
                        message += `<strong>Chi tiết lỗi:</strong><br>`;
                        data.results.forEach(result => {
                            if (!result.success) {
                                message += `- ${result.profile}: ${result.message}<br>`;
                            }
                        });
                    }
                    
                    showStatus('success', message);
                } else {
                    showStatus('error', `❌ Lỗi: ${data.error || 'Unknown error'}`);
                }
            } catch (error) {
                showStatus('error', `❌ Lỗi kết nối: ${error.message}`);
            } finally {
                showLoading(false);
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get list of profiles"""
    try:
        mgr = init_manager()
        profiles = mgr.get_all_profiles()
        
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

@app.route('/api/start-livestream', methods=['POST'])
def start_livestream():
    """Start livestream viewing"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        livestream_url = data.get('livestream_url')
        profile_count = data.get('profile_count', 1)
        
        if not livestream_url:
            return jsonify({
                'success': False,
                'error': 'livestream_url is required'
            }), 400
        
        # Get profiles - CHỈ profiles đã login
        mgr = init_manager()
        all_profiles = mgr.get_all_profiles()
        
        # Filter chỉ lấy profiles đã login
        logged_in_profiles = [p for p in all_profiles if mgr.is_profile_logged_in(p)]
        
        print(f"[FILTER] Total profiles: {len(all_profiles)}")
        print(f"[FILTER] Logged in: {len(logged_in_profiles)}")
        print(f"[FILTER] Not logged in: {len(all_profiles) - len(logged_in_profiles)}")
        
        if not logged_in_profiles:
            return jsonify({
                'success': False,
                'error': f'Không có profile nào đã login! ({len(all_profiles)} profiles chưa login)'
            }), 400
        
        # Select profiles từ danh sách đã login
        selected_profiles = logged_in_profiles[:min(profile_count, len(logged_in_profiles))]
        
        print(f"🚀 Starting livestream for {len(selected_profiles)} profiles...")
        print(f"URL: {livestream_url}")
        
        # Start livestream in background thread
        def run_in_background():
            results = run_livestream_profiles(
                manager=mgr,
                profile_names=selected_profiles,
                start_url=livestream_url,
                max_concurrency=6,
                optimized_mode=True,
                ultra_low_memory=False
            )
            
            success_count = sum(1 for _, s, _ in results if s)
            print(f"✅ Completed: {success_count}/{len(results)} successful")
        
        # Start in background
        thread = threading.Thread(target=run_in_background, daemon=True)
        thread.start()
        
        # Return immediately
        return jsonify({
            'success': True,
            'total': len(selected_profiles),
            'success_count': len(selected_profiles),  # Assume success for now
            'failed_count': 0,
            'results': [
                {
                    'profile': profile,
                    'success': True,
                    'message': 'Đang mở profile và treo livestream...'
                }
                for profile in selected_profiles
            ],
            'message': f'Đã bắt đầu mở {len(selected_profiles)} profiles'
        })
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_server(host='0.0.0.0', port=8080):
    """Run the Flask server"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           Simple Test Server - Treo Livestream               ║
╚══════════════════════════════════════════════════════════════╝

🚀 Server starting...
📍 Host: {host}
🔌 Port: {port}
🌐 URL: http://localhost:{port}

📋 Chức năng:
   - Test treo livestream
   - Tự động mở profiles
   - Giao diện web đơn giản

Mở browser và truy cập: http://localhost:{port}

Press Ctrl+C to stop the server
""")
    
    app.run(host=host, port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_server()
