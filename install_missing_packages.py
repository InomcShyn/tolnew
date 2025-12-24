"""
Install Missing Packages
Cài đặt các packages còn thiếu
"""

import subprocess
import sys

def install_package(package):
    """Cài đặt một package"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_package(package_name):
    """Kiểm tra package đã cài chưa"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def main():
    print("=" * 70)
    print("📦 INSTALL MISSING PACKAGES")
    print("=" * 70)
    
    # Danh sách packages cần kiểm tra
    packages = {
        'nest_asyncio': 'nest-asyncio==1.6.0',
        'playwright': 'playwright==1.40.0',
        'pyperclip': 'pyperclip==1.8.2',
    }
    
    missing = []
    installed = []
    
    print("\n🔍 Checking packages...\n")
    
    for module_name, package_spec in packages.items():
        if check_package(module_name):
            print(f"✅ {module_name}: Already installed")
            installed.append(module_name)
        else:
            print(f"❌ {module_name}: Not found")
            missing.append((module_name, package_spec))
    
    if not missing:
        print("\n" + "=" * 70)
        print("✅ All packages are already installed!")
        print("=" * 70)
        return
    
    print("\n" + "=" * 70)
    print(f"📊 Summary: {len(installed)} installed, {len(missing)} missing")
    print("=" * 70)
    
    # Xác nhận cài đặt
    print(f"\nPackages to install:")
    for module_name, package_spec in missing:
        print(f"  - {package_spec}")
    
    response = input("\nInstall missing packages? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\n❌ Installation cancelled")
        return
    
    print("\n" + "=" * 70)
    print("🚀 INSTALLING PACKAGES")
    print("=" * 70 + "\n")
    
    success_count = 0
    failed_count = 0
    
    for module_name, package_spec in missing:
        if install_package(package_spec):
            success_count += 1
        else:
            failed_count += 1
        print()
    
    # Cài đặt Playwright browsers nếu cần
    if 'playwright' in [m for m, _ in missing]:
        print("=" * 70)
        print("🎭 Installing Playwright Browsers")
        print("=" * 70)
        print("\nThis may take a few minutes...")
        try:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            print("✅ Playwright browsers installed successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not install Playwright browsers: {e}")
            print("You can install manually later with: playwright install chromium")
    
    # Tổng kết
    print("\n" + "=" * 70)
    print("📊 INSTALLATION SUMMARY")
    print("=" * 70)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📦 Total: {len(missing)}")
    print("=" * 70)
    
    if failed_count > 0:
        print("\n⚠️  Some packages failed to install.")
        print("Try installing manually:")
        for module_name, package_spec in missing:
            print(f"  pip install {package_spec}")
    else:
        print("\n✅ All packages installed successfully!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
