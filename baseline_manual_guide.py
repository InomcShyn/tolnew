#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📖 BASELINE COLLECTION - MANUAL GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hướng dẫn thu thập baseline THỦ CÔNG cho TikTok LIVE 2025

LUỒNG KHỞI ĐỘNG (BẮT BUỘC):
1. python launcher.py
2. Mở gui_manager_modern
3. Khởi động profile bằng nút "Starting" (không auto-join)
4. Thao tác THỦ CÔNG trên trình duyệt để vào TikTok LIVE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import time
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

from baseline_collector_2025 import (
    BaselineCollector,
    get_browser_state_script,
    get_video_state_script,
    get_audio_state_script,
    get_websocket_state_script
)


def print_header(title: str):
    """Print section header"""
    print("\n" + "="*70)
    print(title)
    print("="*70)


def print_step(step_num: int, title: str, description: str):
    """Print step instructions"""
    print(f"\n{'━'*70}")
    print(f"BƯỚC {step_num}: {title}")
    print(f"{'━'*70}")
    print(description)
    print()


def wait_for_user(prompt: str = "Nhấn Enter để tiếp tục..."):
    """Wait for user input"""
    input(f"👉 {prompt}")


def main():
    """Main guide for manual baseline collection"""
    
    print_header("📊 BASELINE COLLECTION - MANUAL GUIDE")
    
    print("""
Hướng dẫn này sẽ giúp bạn thu thập baseline behavior THỦ CÔNG
cho TikTok LIVE 2025.

MỤC TIÊU:
- Ghi nhận toàn bộ dữ liệu runtime khi khởi động Chrome
- So sánh trạng thái khi LIVE được tính view vs không được tính
- Làm nền tảng để tối ưu RAM từng bước mà không phá view eligibility

CHUẨN BỊ:
- Profile đã login TikTok
- Biết username TikTok đang LIVE
- Không tối ưu RAM trước khi có baseline
- Không inject script trước khi profile start
    """)
    
    wait_for_user("Nhấn Enter để bắt đầu...")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 1: Initialize collector
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_step(1, "KHỞI TẠO COLLECTOR", """
Nhập thông tin profile để bắt đầu thu thập baseline.
    """)
    
    profile_id = input("Profile ID (e.g. 001, X-001): ").strip()
    session_name = input("Session name (optional, Enter to auto): ").strip()
    
    collector = BaselineCollector(profile_id, session_name)
    
    print(f"\n✅ Collector initialized")
    print(f"   Output: {collector.output_dir}")
    
    # Collect bootstrap
    collector.collect_bootstrap(note="Manual baseline collection started")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 2: Launch profile
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_step(2, "KHỞI ĐỘNG PROFILE", """
1. Mở terminal mới
2. Chạy: python launcher.py
3. Mở gui_manager_modern
4. Chọn profile: {profile_id}
5. Click nút "Starting" (KHÔNG auto-join)
6. Chờ Chrome mở và profile load xong
    """.format(profile_id=profile_id))
    
    wait_for_user("Đã khởi động profile? Nhấn Enter...")
    
    # Get Chrome info
    print("\nNhập thông tin Chrome:")
    chrome_pid = int(input("  Chrome PID: ").strip())
    
    print("\nĐang lấy Chrome command line...")
    try:
        import psutil
        process = psutil.Process(chrome_pid)
        chrome_command = " ".join(process.cmdline())
        print(f"  ✅ Command: {chrome_command[:100]}...")
    except Exception as e:
        print(f"  ⚠️  Không lấy được command: {e}")
        chrome_command = input("  Nhập Chrome command thủ công: ").strip()
    
    window_size = input("  Window size (e.g. 360x640): ").strip() or "360x640"
    user_agent = input("  User agent (Enter to skip): ").strip() or "Unknown"
    
    # Collect profile started
    collector.collect_profile_started(
        chrome_pid=chrome_pid,
        chrome_command=chrome_command,
        window_size=window_size,
        user_agent=user_agent,
        note="Profile started via Starting button"
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 3: Navigate to profile page
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_step(3, "TRUY CẬP PROFILE PAGE", """
1. Trong Chrome, truy cập: https://www.tiktok.com/@username
2. Chờ trang load hoàn chỉnh
3. Mở DevTools (F12)
4. Chạy script để lấy browser state
    """)
    
    username = input("TikTok username (without @): ").strip()
    profile_url = f"https://www.tiktok.com/@{username}"
    
    print(f"\n👉 Truy cập: {profile_url}")
    wait_for_user("Đã load xong profile page? Nhấn Enter...")
    
    print("\n📋 Copy script này vào Console:")
    print("─"*70)
    print(get_browser_state_script())
    print("─"*70)
    
    wait_for_user("Đã chạy script? Nhấn Enter...")
    
    print("\nNhập kết quả (JSON):")
    print("(Paste JSON và nhấn Enter 2 lần)")
    
    browser_state_lines = []
    while True:
        line = input()
        if not line:
            break
        browser_state_lines.append(line)
    
    try:
        import json
        browser_state = json.loads("\n".join(browser_state_lines))
    except:
        print("⚠️  JSON không hợp lệ, dùng placeholder")
        browser_state = {"error": "Invalid JSON"}
    
    dom_ready_ms = float(input("DOMContentLoaded time (ms): ").strip() or "0")
    full_render_ms = float(input("Full render time (ms): ").strip() or "0")
    
    # Collect profile page loaded
    collector.collect_profile_page_loaded(
        url=profile_url,
        dom_ready_ms=dom_ready_ms,
        full_render_ms=full_render_ms,
        browser_state=browser_state,
        note="Profile page loaded manually"
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 4: Detect LIVE badge
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_step(4, "PHÁT HIỆN LIVE BADGE", """
1. Tìm LIVE badge trên trang
2. Inspect element để lấy selector
3. Ghi nhận thông tin element
    """)
    
    has_live = input("Có LIVE badge? (y/n): ").strip().lower() == 'y'
    
    if has_live:
        badge_selector = input("Badge selector (CSS): ").strip()
        
        print("\n📋 Copy script này vào Console để lấy element info:")
        print("─"*70)
        print(f"document.querySelector('{badge_selector}')")
        print("─"*70)
        
        badge_element = {
            "selector": badge_selector,
            "found": True
        }
        
        dom_state = {
            "video_elements": int(input("Số video elements: ").strip() or "0"),
            "websockets_open": int(input("Số websockets mở: ").strip() or "0")
        }
        
        collector.collect_live_badge_detected(
            badge_selector=badge_selector,
            badge_element=badge_element,
            dom_state=dom_state,
            note="LIVE badge detected manually"
        )
    else:
        print("⚠️  Không có LIVE badge, bỏ qua bước này")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 5: Click LIVE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    if has_live:
        print_step(5, "CLICK VÀO LIVE", """
1. Ghi nhận URL hiện tại
2. Click vào LIVE badge
3. Chờ chuyển trang
4. Ghi nhận URL mới
        """)
        
        url_before = input("URL trước khi click: ").strip() or profile_url
        
        wait_for_user("Click vào LIVE badge, sau đó nhấn Enter...")
        
        url_after = input("URL sau khi click: ").strip()
        navigation_type = input("Navigation type (SPA/hard): ").strip() or "SPA"
        history_length = int(input("history.length: ").strip() or "0")
        transition_ms = float(input("Transition time (ms): ").strip() or "0")
        
        collector.collect_live_clicked(
            url_before=url_before,
            url_after=url_after,
            navigation_type=navigation_type,
            history_length=history_length,
            transition_ms=transition_ms,
            note="LIVE clicked manually"
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 6: LIVE playing
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_step(6, "LIVE ĐANG PHÁT", """
1. Chờ video bắt đầu phát
2. Chạy scripts để lấy video/audio/websocket state
    """)
    
    wait_for_user("Video đã bắt đầu phát? Nhấn Enter...")
    
    print("\n📋 VIDEO STATE - Copy script vào Console:")
    print("─"*70)
    print(get_video_state_script())
    print("─"*70)
    
    # Simplified input
    video_state = {
        "readyState": int(input("video.readyState (0-4): ").strip() or "0"),
        "paused": input("video.paused (true/false): ").strip().lower() == "true",
        "muted": input("video.muted (true/false): ").strip().lower() == "true",
        "currentTime": float(input("video.currentTime: ").strip() or "0")
    }
    
    print("\n📋 AUDIO STATE - Copy script vào Console:")
    print("─"*70)
    print(get_audio_state_script())
    print("─"*70)
    
    audio_state = {
        "state": input("AudioContext.state (suspended/running): ").strip() or "unknown"
    }
    
    print("\n📋 WEBSOCKET STATE:")
    websocket_state = {
        "connected": input("WebSocket connected? (y/n): ").strip().lower() == 'y'
    }
    
    collector.collect_live_playing(
        video_state=video_state,
        audio_state=audio_state,
        websocket_state=websocket_state,
        note="LIVE playing state collected"
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STEP 7: View window elapsed
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_step(7, "CHỜ VIEW WINDOW (8-12 GIÂY)", """
1. Xem LIVE ít nhất 8-12 giây
2. Không chuyển tab, không minimize
3. Giữ video trong viewport
    """)
    
    print("\n⏱️  Đang đếm ngược 10 giây...")
    for i in range(10, 0, -1):
        print(f"   {i}...", end="\r")
        time.sleep(1)
    print("   ✅ Hoàn thành!")
    
    watch_duration = float(input("\nThời gian xem thực tế (giây): ").strip() or "10")
    
    view_eligibility = {
        "document_hasFocus": input("document.hasFocus() (true/false): ").strip().lower() == "true",
        "document_visibilityState": input("document.visibilityState: ").strip() or "visible",
        "video_playback_duration": float(input("Video playback duration (s): ").strip() or "0"),
        "websocket_stable": input("WebSocket stable? (y/n): ").strip().lower() == 'y'
    }
    
    final_state = {
        "note": input("Ghi chú cuối (view có được tính?): ").strip()
    }
    
    collector.collect_view_window_elapsed(
        watch_duration_s=watch_duration,
        view_eligibility=view_eligibility,
        final_state=final_state,
        note="View window elapsed - manual observation"
    )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # GENERATE SUMMARY
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    print_header("📊 GENERATING SUMMARY")
    
    summary_file = collector.generate_summary()
    
    print(f"\n✅ Baseline collection complete!")
    print(f"   Output directory: {collector.output_dir}")
    print(f"   Summary file: {summary_file}")
    
    print("\n📁 Files created:")
    for file in sorted(collector.output_dir.glob("*.json")):
        print(f"   - {file.name}")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Review collected data in:", collector.output_dir)
    print("2. Run another session with different settings")
    print("3. Compare sessions using: python baseline_compare.py")
    print("4. Identify safe RAM optimizations")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
