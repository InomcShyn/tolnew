#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proxy utilities - Converted from core/utils/proxy_utils.py
"""

import re
from typing import Dict, Optional


def fix_duplicate_protocol(proxy_string: str) -> str:
    """
    Fix duplicate protocol in proxy string
    
    Examples:
        http://http://server:port -> http://server:port
        socks5://socks5://server:port -> socks5://server:port
    
    Args:
        proxy_string: Proxy string that may have duplicate protocol
        
    Returns:
        Cleaned proxy string
    """
    if proxy_string.startswith('http://http://'):
        return proxy_string.replace('http://http://', 'http://', 1)
    elif proxy_string.startswith('https://https://'):
        return proxy_string.replace('https://https://', 'https://', 1)
    elif proxy_string.startswith('socks5://socks5://'):
        return proxy_string.replace('socks5://socks5://', 'socks5://', 1)
    elif proxy_string.startswith('socks4://socks4://'):
        return proxy_string.replace('socks4://socks4://', 'socks4://', 1)
    return proxy_string


def parse_proxy_string(proxy_string: str) -> Dict:
    """
    Parse proxy string into components
    
    Supported formats:
    - http://server:port:username:password
    - socks5://server:port:username:password
    - server:port:username:password (defaults to http)
    
    Returns:
        Dict with keys: protocol, server, port, username, password
    """
    try:
        protocol = 'http'
        username = ''
        password = ''
        
        # Check if protocol is specified
        if '://' in proxy_string:
            parts = proxy_string.split('://', 1)
            protocol = parts[0].lower()
            rest = parts[1]
        else:
            rest = proxy_string
        
        # Parse rest: server:port:username:password or server:port
        parts = rest.split(':')
        
        if len(parts) >= 4:
            server = parts[0]
            port = parts[1]
            username = parts[2]
            password = ':'.join(parts[3:])
        elif len(parts) >= 2:
            server = parts[0]
            port = parts[1]
        else:
            raise ValueError(f"Invalid proxy format: {proxy_string}")
        
        return {
            'protocol': protocol,
            'server': server,
            'port': port,
            'username': username,
            'password': password
        }
    except Exception as e:
        raise ValueError(f"Failed to parse proxy '{proxy_string}': {e}")


def format_proxy_url(protocol: str, server: str, port: str, username: str = '', password: str = '') -> str:
    """
    Format proxy components into URL format
    
    Returns:
        Formatted proxy URL (scheme://user:pass@server:port)
    """
    if username and password:
        return f"{protocol}://{username}:{password}@{server}:{port}"
    else:
        return f"{protocol}://{server}:{port}"


def validate_proxy_format(proxy_string: str) -> tuple[bool, str]:
    """
    Validate proxy string format
    
    Returns:
        (is_valid, error_message)
    """
    try:
        parsed = parse_proxy_string(proxy_string)
        
        if not parsed['server']:
            return False, "Server address is required"
        
        try:
            port_num = int(parsed['port'])
            if port_num < 1 or port_num > 65535:
                return False, f"Invalid port number: {port_num}"
        except ValueError:
            return False, f"Invalid port: {parsed['port']}"
        
        valid_protocols = ['http', 'https', 'socks4', 'socks5']
        if parsed['protocol'] not in valid_protocols:
            return False, f"Invalid protocol: {parsed['protocol']}"
        
        return True, "Valid proxy format"
        
    except ValueError as e:
        return False, str(e)


def parse_proxy_list(proxy_text: str) -> list[str]:
    """
    Parse proxy list from text
    
    Args:
        proxy_text: Multi-line text containing proxy strings
    
    Returns:
        List of cleaned proxy strings
    """
    proxy_list = []
    for line in proxy_text.splitlines():
        line = line.strip()
        if line and line.lower() != 'null':
            proxy_list.append(line)
    return proxy_list
