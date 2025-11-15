#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test proxy format parsing"""

import sys
import os

# Set UTF-8 encoding for console output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.tiles.tile_profile_management import parse_proxy_string

def test_proxy_format(proxy_string, expected_protocol=None):
    """Test parsing a proxy string"""
    print(f"\n{'='*60}")
    print(f"Testing: {proxy_string}")
    print(f"{'='*60}")
    
    try:
        result = parse_proxy_string(proxy_string)
        print(f"✅ Success!")
        print(f"  Protocol: {result['protocol']}")
        print(f"  Server:   {result['server']}")
        print(f"  Port:     {result['port']}")
        print(f"  Username: {result['username']}")
        print(f"  Password: {result['password']}")
        
        if expected_protocol and result['protocol'] != expected_protocol:
            print(f"⚠️  Warning: Expected protocol '{expected_protocol}' but got '{result['protocol']}'")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("Testing Proxy Format Parsing")
    print("="*60)
    
    test_cases = [
        # Format: (proxy_string, expected_protocol)
        ("http://27.79.170.112:10009:user1:pass1", "http"),
        ("socks4://27.79.170.112:10009:user1:pass1", "socks4"),
        ("socks5://27.79.170.112:10009:user1:pass1", "socks5"),
        ("27.79.170.112:10009:user1:pass1", "http"),  # Default to http
        ("http://27.79.170.112:10009", "http"),  # No auth
        ("27.79.170.112:10009", "http"),  # No auth, default to http
        ("socks5://proxy.example.com:1080:admin:p@ssw0rd:123", "socks5"),  # Password with ':'
        ("192.168.1.1:8080:user:pass", "http"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for proxy_string, expected_protocol in test_cases:
        if test_proxy_format(proxy_string, expected_protocol):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {success_count}/{total_count} tests passed")
    print(f"{'='*60}")
    
    if success_count == total_count:
        print("✅ All tests passed!")
    else:
        print(f"❌ {total_count - success_count} tests failed")

if __name__ == "__main__":
    main()
