#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Live Metrics API Client
========================
Lấy thông tin livestream (viewer count, duration) qua HTTP API.
KHÔNG dùng browser, KHÔNG headless, chỉ HTTP requests.

Tối ưu RAM:
- Không lưu response thô
- Chỉ parse field cần thiết
- Không giữ session nếu không cần
"""

import re
import json
import time
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENABLE_DEBUG = False  # Set to True for verbose logging

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 2


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def debug_log(message: str):
    """Log debug message if ENABLE_DEBUG is True"""
    if ENABLE_DEBUG:
        print(f"[DEBUG] {message}")


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to HH:MM:SS
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string "HH:MM:SS"
    """
    if seconds < 0:
        return "N/A"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def extract_username_from_url(live_url: str) -> Optional[str]:
    """
    Extract username from TikTok live URL
    
    Args:
        live_url: TikTok live URL (e.g. https://www.tiktok.com/@username/live)
    
    Returns:
        Username without @ or None if not found
    """
    try:
        # Pattern: @username/live or @username
        match = re.search(r'@([^/]+)', live_url)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        debug_log(f"Error extracting username: {e}")
        return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN CLIENT CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LiveMetricsClient:
    """
    Client để lấy metrics từ TikTok LIVE qua HTTP API.
    
    Features:
    - Lấy viewer count
    - Lấy live duration
    - Timeout + retry
    - Tối ưu RAM (không lưu response thô)
    """
    
    def __init__(self, headers: Optional[Dict] = None, timeout: int = REQUEST_TIMEOUT):
        """
        Initialize client
        
        Args:
            headers: Custom headers (optional)
            timeout: Request timeout in seconds
        """
        self.headers = headers or DEFAULT_HEADERS.copy()
        self.timeout = timeout
        self.session = None  # Không giữ session để tiết kiệm RAM
    
    def get_live_metrics(self, live_url: str) -> Dict:
        """
        Lấy metrics từ TikTok LIVE URL
        
        Args:
            live_url: TikTok live URL (e.g. https://www.tiktok.com/@username/live)
        
        Returns:
            {
                "live_url": str,
                "viewer_count": int,  # -1 if failed
                "live_duration_seconds": int,  # -1 if failed
                "live_duration_human": str,  # "HH:MM:SS" or "N/A"
                "timestamp": float,  # Unix timestamp
                "status": str,  # "success" or "error"
                "error": str  # Error message if failed
            }
        """
        result = {
            'live_url': live_url,
            'viewer_count': -1,
            'live_duration_seconds': -1,
            'live_duration_human': 'N/A',
            'timestamp': time.time(),
            'status': 'error',
            'error': None
        }
        
        try:
            debug_log(f"Fetching metrics for: {live_url}")
            
            # Extract username
            username = extract_username_from_url(live_url)
            if not username:
                result['error'] = 'Invalid URL: Cannot extract username'
                debug_log(result['error'])
                return result
            
            debug_log(f"Username: @{username}")
            
            # Fetch page with retry
            html_content = self._fetch_page_with_retry(live_url)
            
            if not html_content:
                result['error'] = 'Failed to fetch page after retries'
                debug_log(result['error'])
                return result
            
            # Parse metrics from HTML
            metrics = self._parse_metrics_from_html(html_content)
            
            if metrics:
                result['viewer_count'] = metrics.get('viewer_count', -1)
                result['live_duration_seconds'] = metrics.get('live_duration_seconds', -1)
                result['live_duration_human'] = format_duration(result['live_duration_seconds'])
                result['status'] = 'success'
                result['error'] = None
                
                debug_log(f"Metrics extracted: viewers={result['viewer_count']}, duration={result['live_duration_human']}")
            else:
                result['error'] = 'Failed to parse metrics from HTML'
                debug_log(result['error'])
            
            return result
            
        except Exception as e:
            result['error'] = f'Exception: {str(e)}'
            debug_log(result['error'])
            return result
    
    def _fetch_page_with_retry(self, url: str) -> Optional[str]:
        """
        Fetch page with retry logic
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content or None if failed
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                debug_log(f"Attempt {attempt}/{MAX_RETRIES}: Fetching {url}")
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                debug_log(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    # Không lưu response.text vào biến lớn
                    # Chỉ return ngay để tiết kiệm RAM
                    return response.text
                
                elif response.status_code == 403:
                    debug_log("403 Forbidden - May need cookies or different headers")
                    return None
                
                elif response.status_code == 429:
                    debug_log("429 Too Many Requests - Rate limited")
                    if attempt < MAX_RETRIES:
                        time.sleep(2)  # Wait before retry
                        continue
                    return None
                
                elif response.status_code == 404:
                    debug_log("404 Not Found - Live may not exist")
                    return None
                
                else:
                    debug_log(f"Unexpected status code: {response.status_code}")
                    if attempt < MAX_RETRIES:
                        time.sleep(1)
                        continue
                    return None
                
            except requests.exceptions.Timeout:
                debug_log(f"Timeout on attempt {attempt}")
                if attempt < MAX_RETRIES:
                    time.sleep(1)
                    continue
                return None
            
            except requests.exceptions.RequestException as e:
                debug_log(f"Request exception on attempt {attempt}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(1)
                    continue
                return None
        
        return None
    
    def _parse_metrics_from_html(self, html: str) -> Optional[Dict]:
        """
        Parse metrics from HTML content
        
        Strategies:
        1. Try to find SIGI_STATE (TikTok's initial state)
        2. Try to find __UNIVERSAL_DATA_FOR_REHYDRATION__
        3. Try to find embedded JSON in script tags
        4. Fallback: regex patterns for viewer count
        
        Args:
            html: HTML content
        
        Returns:
            {
                'viewer_count': int,
                'live_duration_seconds': int
            }
            or None if failed
        """
        try:
            # ─────────────────────────────────────────────────────────
            # Strategy 1: SIGI_STATE (most common)
            # ─────────────────────────────────────────────────────────
            sigi_match = re.search(r'<script[^>]*id="SIGI_STATE"[^>]*>(.*?)</script>', html, re.DOTALL)
            if sigi_match:
                try:
                    sigi_data = json.loads(sigi_match.group(1))
                    metrics = self._extract_from_sigi_state(sigi_data)
                    if metrics:
                        debug_log("Metrics extracted from SIGI_STATE")
                        return metrics
                except json.JSONDecodeError:
                    debug_log("Failed to parse SIGI_STATE JSON")
            
            # ─────────────────────────────────────────────────────────
            # Strategy 2: __UNIVERSAL_DATA_FOR_REHYDRATION__
            # ─────────────────────────────────────────────────────────
            universal_match = re.search(
                r'<script[^>]*id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>',
                html,
                re.DOTALL
            )
            if universal_match:
                try:
                    universal_data = json.loads(universal_match.group(1))
                    metrics = self._extract_from_universal_data(universal_data)
                    if metrics:
                        debug_log("Metrics extracted from __UNIVERSAL_DATA_FOR_REHYDRATION__")
                        return metrics
                except json.JSONDecodeError:
                    debug_log("Failed to parse __UNIVERSAL_DATA_FOR_REHYDRATION__ JSON")
            
            # ─────────────────────────────────────────────────────────
            # Strategy 3: Any script tag with JSON
            # ─────────────────────────────────────────────────────────
            script_tags = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
            for script_content in script_tags:
                if 'userCount' in script_content or 'viewerCount' in script_content:
                    try:
                        # Try to extract JSON
                        json_match = re.search(r'\{.*"userCount".*\}', script_content, re.DOTALL)
                        if json_match:
                            data = json.loads(json_match.group(0))
                            metrics = self._extract_from_generic_json(data)
                            if metrics:
                                debug_log("Metrics extracted from generic script JSON")
                                return metrics
                    except:
                        continue
            
            # ─────────────────────────────────────────────────────────
            # Strategy 4: Regex fallback for viewer count
            # ─────────────────────────────────────────────────────────
            viewer_patterns = [
                r'"userCount["\s:]+(\d+)',
                r'"viewerCount["\s:]+(\d+)',
                r'"user_count["\s:]+(\d+)',
                r'"viewer_count["\s:]+(\d+)',
            ]
            
            for pattern in viewer_patterns:
                match = re.search(pattern, html)
                if match:
                    viewer_count = int(match.group(1))
                    debug_log(f"Viewer count found via regex: {viewer_count}")
                    return {
                        'viewer_count': viewer_count,
                        'live_duration_seconds': -1  # Cannot determine from regex
                    }
            
            debug_log("No metrics found in HTML")
            return None
            
        except Exception as e:
            debug_log(f"Error parsing metrics: {e}")
            return None
    
    def _extract_from_sigi_state(self, data: Dict) -> Optional[Dict]:
        """Extract metrics from SIGI_STATE data structure"""
        try:
            # Navigate through nested structure
            # Common paths:
            # - LiveRoom.liveRoomUserInfo.user_count
            # - RoomStore.roomInfo.user_count
            
            # Try LiveRoom path
            if 'LiveRoom' in data:
                live_room = data['LiveRoom']
                if 'liveRoomUserInfo' in live_room:
                    user_info = live_room['liveRoomUserInfo']
                    if 'user_count' in user_info:
                        viewer_count = int(user_info['user_count'])
                        
                        # Try to get duration
                        duration = -1
                        if 'liveRoomInfo' in live_room:
                            room_info = live_room['liveRoomInfo']
                            if 'create_time' in room_info:
                                create_time = int(room_info['create_time'])
                                current_time = int(time.time())
                                duration = current_time - create_time
                        
                        return {
                            'viewer_count': viewer_count,
                            'live_duration_seconds': duration
                        }
            
            # Try RoomStore path
            if 'RoomStore' in data:
                room_store = data['RoomStore']
                if 'roomInfo' in room_store:
                    room_info = room_store['roomInfo']
                    if 'user_count' in room_info:
                        viewer_count = int(room_info['user_count'])
                        
                        # Try to get duration
                        duration = -1
                        if 'create_time' in room_info:
                            create_time = int(room_info['create_time'])
                            current_time = int(time.time())
                            duration = current_time - create_time
                        
                        return {
                            'viewer_count': viewer_count,
                            'live_duration_seconds': duration
                        }
            
            return None
            
        except Exception as e:
            debug_log(f"Error extracting from SIGI_STATE: {e}")
            return None
    
    def _extract_from_universal_data(self, data: Dict) -> Optional[Dict]:
        """Extract metrics from __UNIVERSAL_DATA_FOR_REHYDRATION__ data structure"""
        try:
            # Similar structure to SIGI_STATE
            # Try common paths
            
            if '__DEFAULT_SCOPE__' in data:
                default_scope = data['__DEFAULT_SCOPE__']
                
                # Try webapp.video-detail path
                if 'webapp.video-detail' in default_scope:
                    video_detail = default_scope['webapp.video-detail']
                    if 'itemInfo' in video_detail:
                        item_info = video_detail['itemInfo']
                        if 'itemStruct' in item_info:
                            item_struct = item_info['itemStruct']
                            if 'stats' in item_struct:
                                stats = item_struct['stats']
                                if 'playCount' in stats:
                                    viewer_count = int(stats['playCount'])
                                    return {
                                        'viewer_count': viewer_count,
                                        'live_duration_seconds': -1
                                    }
            
            return None
            
        except Exception as e:
            debug_log(f"Error extracting from __UNIVERSAL_DATA_FOR_REHYDRATION__: {e}")
            return None
    
    def _extract_from_generic_json(self, data: Dict) -> Optional[Dict]:
        """Extract metrics from generic JSON data"""
        try:
            # Try common field names
            viewer_count = None
            
            if 'userCount' in data:
                viewer_count = int(data['userCount'])
            elif 'viewerCount' in data:
                viewer_count = int(data['viewerCount'])
            elif 'user_count' in data:
                viewer_count = int(data['user_count'])
            elif 'viewer_count' in data:
                viewer_count = int(data['viewer_count'])
            
            if viewer_count is not None:
                return {
                    'viewer_count': viewer_count,
                    'live_duration_seconds': -1
                }
            
            return None
            
        except Exception as e:
            debug_log(f"Error extracting from generic JSON: {e}")
            return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONVENIENCE FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_live_metrics(live_url: str) -> Dict:
    """
    Convenience function to get metrics without creating client instance
    
    Args:
        live_url: TikTok live URL
    
    Returns:
        Metrics dict (see LiveMetricsClient.get_live_metrics)
    """
    client = LiveMetricsClient()
    return client.get_live_metrics(live_url)


def print_metrics(metrics: Dict):
    """
    Print metrics in human-readable format
    
    Args:
        metrics: Metrics dict from get_live_metrics()
    """
    print("\n" + "="*70)
    print("📊 LIVE METRICS")
    print("="*70)
    print(f"Live URL:  {metrics['live_url']}")
    print(f"Status:    {metrics['status']}")
    
    if metrics['status'] == 'success':
        print(f"Viewers:   {metrics['viewer_count']:,}")
        print(f"Duration:  {metrics['live_duration_human']}")
    else:
        print(f"Error:     {metrics['error']}")
    
    print(f"Timestamp: {datetime.fromtimestamp(metrics['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN - TEST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("🔍 LIVE METRICS API CLIENT - TEST")
    print("="*70)
    
    # Get live URL from command line or prompt
    if len(sys.argv) > 1:
        live_url = sys.argv[1]
    else:
        print("\nExample: https://www.tiktok.com/@username/live")
        live_url = input("Enter TikTok live URL: ").strip()
    
    if not live_url:
        print("❌ Live URL required")
        sys.exit(1)
    
    # Enable debug mode for testing
    ENABLE_DEBUG = True
    
    # Get metrics
    print(f"\n🔄 Fetching metrics for: {live_url}\n")
    
    client = LiveMetricsClient()
    metrics = client.get_live_metrics(live_url)
    
    # Print results
    print_metrics(metrics)
    
    # Print raw data
    if ENABLE_DEBUG:
        print("\n📋 Raw Data:")
        print(json.dumps(metrics, indent=2))
