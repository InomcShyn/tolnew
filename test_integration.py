#!/usr/bin/env python3
"""
Integrated Auto TikTok 2FA Test - Test tích hợp hoàn chỉnh
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_integrated_auto_2fa():
    """Test tích hợp auto 2FA với chrome_manager"""
    print("🚀 Testing Integrated Auto TikTok 2FA")
    print("=" * 60)
    
    try:
        # Import chrome_manager
        from chrome_manager import ChromeProfileManager
        
        # Initialize manager
        manager = ChromeProfileManager()
        
        # Test account line
        test_account = "kristinaclawsonvbk25116@hotmail.com|kristinaaaigh1744|kristinaclawsonvbk25116@hotmail.com|kristinaaaigh1744|M.C546_BAY.0.U.-CnNF3jpiGu4bAqcuZdLn1CT6FYGcFc7E1kvAQS21M5jJBngLdNm9QJPojgbFObwNdqtkwDnwYgNoHXv1XLJLqf9AgMcOTtbW1TspGLj*6B9ISF3spx92j*p31YhGiYH5eC8UpigXx*W8rJprZ0AlqbgoDpSRPzZ*K9JEzysUWBVHicHvV0XfV5DD52JcoQAl4Yt0ypJUjK*yR6B0dbkxmNVBbQPCKd1k5NHBa4EqBD8dDdVa0xQsVBpCs1APT22945Sr*F*k*iEApEOTuhoHtLMn!oBKC5SQksNAHNysbgcP0327ijEhmYPLtPyYXjuDNS*7NoNkkuPzfxxd*2FDgru9EcUypotWuFUYmPZ7kspeUMc0WugtoZuoIDn!WDsu*tif8oF7LYXWyGb2F5oicJMNWPf1nn1KiIVfq6ACPtMY9i0XwApa6RKsoGSV7d6hVg$$|9e5f94bc-e8a4-4e73-b8be-63364c29d753"
        
        print(f"📧 Testing account: kristinaclawsonvbk25116@hotmail.com")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test Graph mail fetch
        print("🔍 Testing Graph mail fetch...")
        success, result = manager.test_graph_mail_fetch(test_account)
        
        if success:
            print(f"✅ SUCCESS: {result}")
            return True, result
        else:
            print(f"❌ FAILED: {result}")
            return False, result
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False, f"Integration test error: {e}"

def test_standalone_scripts():
    """Test các script standalone"""
    print("\n🧪 Testing Standalone Scripts")
    print("=" * 60)
    
    scripts_to_test = [
        "ultimate_handler.py",
        "simple_test_2fa.py", 
        "continuous_monitor.py",
        "auto_refresh_service.py"
    ]
    
    results = {}
    
    for script in scripts_to_test:
        if os.path.exists(script):
            print(f"✅ {script} - Found")
            results[script] = "Available"
        else:
            print(f"❌ {script} - Not found")
            results[script] = "Missing"
    
    return results

def test_gui_integration():
    """Test GUI integration"""
    print("\n🖥️ Testing GUI Integration")
    print("=" * 60)
    
    try:
        # Test if GUI can be imported
        from gui_manager_modern import ModernChromeProfileManager
        print("✅ GUI Manager imported successfully")
        
        # Test if auto 2FA methods exist
        manager = ModernChromeProfileManager()
        
        auto_2fa_methods = [
            'setup_device_login',
            'test_auto_2fa_connection', 
            'test_account_line_2fa',
            'save_auto_2fa_config',
            'load_auto_2fa_config',
            'clear_auto_2fa_config',
            'log_auto_2fa'
        ]
        
        for method in auto_2fa_methods:
            if hasattr(manager, method):
                print(f"✅ Method {method} - Available")
            else:
                print(f"❌ Method {method} - Missing")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI integration error: {e}")
        return False

def create_test_config():
    """Tạo file config test"""
    print("\n📝 Creating Test Configuration")
    print("=" * 60)
    
    test_config = {
        "email": "kristinaclawsonvbk25116@hotmail.com",
        "refresh_token": "M.C546_BAY.0.U.-CnNF3jpiGu4bAqcuZdLn1CT6FYGcFc7E1kvAQS21M5jJBngLdNm9QJPojgbFObwNdqtkwDnwYgNoHXv1XLJLqf9AgMcOTtbW1TspGLj*6B9ISF3spx92j*p31YhGiYH5eC8UpigXx*W8rJprZ0AlqbgoDpSRPzZ*K9JEzysUWBVHicHvV0XfV5DD52JcoQAl4Yt0ypJUjK*yR6B0dbkxmNVBbQPCKd1k5NHBa4EqBD8dDdVa0xQsVBpCs1APT22945Sr*F*k*iEApEOTuhoHtLMn!oBKC5SQksNAHNysbgcP0327ijEhmYPLtPyYXjuDNS*7NoNkkuPzfxxd*2FDgru9EcUypotWuFUYmPZ7kspeUMc0WugtoZuoIDn!WDsu*tif8oF7LYXWyGb2F5oicJMNWPf1nn1KiIVfq6ACPtMY9i0XwApa6RKsoGSV7d6hVg$$",
        "client_id": "9e5f94bc-e8a4-4e73-b8be-63364c29d753",
        "email_password": "kristinaaaigh1744"
    }
    
    try:
        with open('auto_2fa_config.json', 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2)
        
        print("✅ Test configuration created: auto_2fa_config.json")
        return True
        
    except Exception as e:
        print(f"❌ Config creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Integrated Auto TikTok 2FA Test Suite")
    print("=" * 80)
    print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Standalone scripts
    script_results = test_standalone_scripts()
    
    # Test 2: GUI integration
    gui_success = test_gui_integration()
    
    # Test 3: Create test config
    config_success = create_test_config()
    
    # Test 4: Integrated auto 2FA
    print("\n🔗 Testing Integrated Auto 2FA")
    print("=" * 60)
    auto_2fa_success, auto_2fa_result = test_integrated_auto_2fa()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 80)
    
    print(f"📁 Standalone Scripts: {sum(1 for v in script_results.values() if v == 'Available')}/{len(script_results)} available")
    print(f"🖥️ GUI Integration: {'✅ Success' if gui_success else '❌ Failed'}")
    print(f"📝 Test Config: {'✅ Created' if config_success else '❌ Failed'}")
    print(f"🔗 Auto 2FA Integration: {'✅ Success' if auto_2fa_success else '❌ Failed'}")
    
    if auto_2fa_success:
        print(f"🎉 Final Result: {auto_2fa_result}")
    else:
        print(f"❌ Final Result: {auto_2fa_result}")
    
    print(f"\n⏰ Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return auto_2fa_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
