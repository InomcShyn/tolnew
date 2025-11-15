"""
Simple script to run MinProxy HTTP Server
"""

import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("MinProxy HTTP Server - Launcher")
    print("=" * 60)
    print()
    
    # Get server directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_dir = os.path.join(current_dir, 'server')
    
    if not os.path.exists(server_dir):
        print("❌ ERROR: Server directory not found")
        print(f"Expected: {server_dir}")
        input("Press Enter to exit...")
        return
    
    server_file = os.path.join(server_dir, 'minproxy_server.py')
    if not os.path.exists(server_file):
        print("❌ ERROR: minproxy_server.py not found")
        print(f"Expected: {server_file}")
        input("Press Enter to exit...")
        return
    
    requirements_file = os.path.join(server_dir, 'requirements.txt')
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print()
    
    # Install dependencies
    if os.path.exists(requirements_file):
        print("📦 Installing dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', '-r', requirements_file], 
                         check=True, cwd=server_dir)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("⚠️ Warning: Failed to install some dependencies")
        print()
    
    # Run server
    print("🚀 Starting server...")
    print("📍 URL: http://localhost:5000")
    print("📍 Host: 0.0.0.0")
    print("📍 Port: 5000")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    try:
        subprocess.run([sys.executable, server_file, '--host', '0.0.0.0', '--port', '5000'],
                      cwd=server_dir)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
