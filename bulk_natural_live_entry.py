#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 BULK NATURAL LIVE ENTRY - Chạy hàng loạt accounts
Sử dụng 100% logic từ natural_live_entry.py
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.chrome_manager import ChromeProfileManager
from core.managers.profile_manager import ProfileManager

# Import natural_live_entry function từ natural_live_entry.py
from natural_live_entry import natural_live_entry


class BulkNaturalLiveEntry:
    """Manager để chạy hàng loạt natural live entry"""
    
    def __init__(self):
        self.chrome_manager = ChromeProfileManager()
        self.profile_manager = ProfileManager()
        self.sessions = []  # Store active sessions
        self.results = []   # Store results
    
    async def launch_single_profile(
        self,
        profile_name: str,
        creator_username: str,
        hidden: bool = False
    ) -> Dict:
        """
        Launch 1 profile và vào livestream
        
        Returns:
            Dict với kết quả
        """
        start_time = time.time()
        result = {
            'profile': profile_name,
            'creator': creator_username,
            'status': 'pending',
            'launch_time': 0,
            'nav_type': 'unknown',
            'history_length': 0,
            'video_exists': False,
            'error': None
        }
        
        try:
            print(f"\n{'='*70}")
            print(f"🚀 [{profile_name}] → @{creator_username}")
            print(f"{'='*70}")
            
            # Launch Chrome profile (không navigate yet)
            success, page = self.chrome_manager.launch_chrome_profile(
                profile_name,
                hidden=hidden,
                auto_login=False,
                login_data=None,
                start_url=None  # Không navigate - để natural_live_entry làm
            )
            
            if not success:
                result['status'] = 'failed'
                result['error'] = f'Failed to launch: {page}'
                print(f"❌ [{profile_name}] Failed to launch")
                return result
            
            print(f"✅ [{profile_name}] Profile launched")
            
            # Gọi natural_live_entry từ natural_live_entry.py
            # Function này sẽ làm tất cả:
            # - Open homepage
            # - User interaction
            # - Navigate to profile
            # - Click LIVE badge
            # - Verify navigation context
            success, nav_context = await natural_live_entry(
                page,
                creator_username,
                profile_name
            )
            
            # Parse kết quả
            if success:
                result['status'] = 'success'
            else:
                result['status'] = 'warning'
            
            # Extract navigation context
            if isinstance(nav_context, dict):
                result['nav_type'] = nav_context.get('navigationType', 'unknown')
                result['history_length'] = nav_context.get('historyLength', 0)
                result['video_exists'] = nav_context.get('videoExists', False)
            
            # Calculate time
            result['launch_time'] = round(time.time() - start_time, 2)
            
            # Store session
            self.sessions.append({
                'profile': profile_name,
                'page': page,
                'creator': creator_username
            })
            
            print(f"✅ [{profile_name}] Completed in {result['launch_time']}s")
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['launch_time'] = round(time.time() - start_time, 2)
            print(f"❌ [{profile_name}] Error: {e}")
        
        return result
    
    async def launch_bulk(
        self,
        profiles: List[str],
        creator_username: str,
        hidden: bool = False,
        delay_between: int = 5
    ):
        """
        Launch nhiều profiles
        
        Args:
            profiles: List profile names
            creator_username: TikTok username (không có @)
            hidden: Hidden mode
            delay_between: Delay giữa các profiles (seconds)
        """
        print("\n" + "="*70)
        print("🚀 BULK NATURAL LIVE ENTRY")
        print("="*70)
        print(f"Total Profiles:  {len(profiles)}")
        print(f"Creator:         @{creator_username}")
        print(f"Hidden Mode:     {hidden}")
        print(f"Delay Between:   {delay_between}s")
        print("="*70)
        
        start_time = time.time()
        
        # Launch từng profile (sequential)
        for i, profile in enumerate(profiles, 1):
            print(f"\n[{i}/{len(profiles)}] Processing: {profile}")
            
            result = await self.launch_single_profile(
                profile,
                creator_username,
                hidden
            )
            
            self.results.append(result)
            
            # Delay trước profile tiếp theo
            if i < len(profiles) and delay_between > 0:
                print(f"\n⏳ Waiting {delay_between}s before next profile...")
                await asyncio.sleep(delay_between)
        
        # Print summary
        total_time = round(time.time() - start_time, 2)
        self.print_summary(total_time)
    
    def print_summary(self, total_time: float):
        """Print summary"""
        print("\n" + "="*70)
        print("📊 BULK LAUNCH SUMMARY")
        print("="*70)
        
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        warning_count = sum(1 for r in self.results if r['status'] == 'warning')
        failed_count = sum(1 for r in self.results if r['status'] == 'failed')
        error_count = sum(1 for r in self.results if r['status'] == 'error')
        
        print(f"Total:           {len(self.results)}")
        print(f"✅ Success:      {success_count}")
        print(f"⚠️  Warning:      {warning_count}")
        print(f"❌ Failed:       {failed_count}")
        print(f"🔥 Error:        {error_count}")
        print(f"⏱️  Total Time:   {total_time}s")
        if self.results:
            print(f"⏱️  Avg/Profile:  {round(total_time/len(self.results), 2)}s")
        print("="*70)
        
        # Detailed results
        print("\n📋 DETAILED RESULTS")
        print("="*70)
        for r in self.results:
            status_icon = {
                'success': '✅',
                'warning': '⚠️',
                'failed': '❌',
                'error': '🔥'
            }.get(r['status'], '❓')
            
            nav_info = f"{r['nav_type']}/{r['history_length']}"
            video_icon = "📹" if r['video_exists'] else "❌"
            
            print(f"{status_icon} {r['profile']:<15} | {r['launch_time']:>6}s | Nav: {nav_info:<15} | Video: {video_icon}")
            
            if r['error']:
                print(f"   └─ {r['error']}")
        
        print("="*70)
    
    async def keep_alive(self, duration_minutes: int = 60):
        """
        Giữ tất cả sessions alive
        
        Args:
            duration_minutes: Thời gian giữ alive (minutes)
        """
        if not self.sessions:
            print("\n⚠️  No active sessions to keep alive")
            return
        
        print(f"\n⏳ Keeping {len(self.sessions)} sessions alive for {duration_minutes} minutes...")
        print("Press Ctrl+C to stop early\n")
        
        end_time = time.time() + (duration_minutes * 60)
        check_interval = 60  # Check every 60s
        
        try:
            while time.time() < end_time:
                remaining = round((end_time - time.time()) / 60, 1)
                print(f"\n⏱️  {remaining} minutes remaining...")
                
                # Check each session
                for session in self.sessions:
                    try:
                        # Check if page is still alive
                        url = await session['page'].evaluate("() => window.location.href")
                        print(f"  ✅ {session['profile']}: Active")
                    except Exception as e:
                        print(f"  ❌ {session['profile']}: Disconnected")
                
                await asyncio.sleep(check_interval)
            
            print("\n✅ Keep-alive duration completed!")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Keep-alive stopped by user")


def load_profiles_from_file(filename: str = "profiles.txt") -> List[str]:
    """Load profiles từ file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            profiles = [line.strip() for line in f if line.strip()]
        return profiles
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []


async def main():
    """Main function"""
    print("\n" + "="*70)
    print("🚀 BULK NATURAL LIVE ENTRY")
    print("="*70)
    print("\nSử dụng 100% logic từ natural_live_entry.py")
    print("Flow: Homepage → Profile → Click LIVE → Verify")
    print("="*70 + "\n")
    
    # Get input method
    print("Choose input method:")
    print("1. Enter profile names manually")
    print("2. Load from profiles.txt file")
    choice = input("Choice (1/2): ").strip()
    
    profiles = []
    
    if choice == "2":
        profiles = load_profiles_from_file("profiles.txt")
        if not profiles:
            print("❌ No profiles loaded")
            return
        print(f"✅ Loaded {len(profiles)} profiles from file")
    else:
        print("\nEnter profile names (one per line, empty to finish):")
        while True:
            profile = input("Profile: ").strip()
            if not profile:
                break
            profiles.append(profile)
        
        if not profiles:
            print("❌ No profiles entered")
            return
    
    # Get creator username
    creator_username = input("\nCreator username (e.g. hoariviu1): ").strip()
    if not creator_username:
        print("❌ Creator username is required")
        return
    
    # Remove @ if included
    creator_username = creator_username.lstrip('@')
    
    # Get options
    hidden_input = input("Hidden mode? (y/n, default: n): ").strip().lower()
    hidden = (hidden_input == 'y')
    
    delay_input = input("Delay between launches (seconds, default: 5): ").strip()
    delay = int(delay_input) if delay_input.isdigit() else 5
    
    keep_alive_input = input("Keep alive duration (minutes, default: 60): ").strip()
    keep_alive = int(keep_alive_input) if keep_alive_input.isdigit() else 60
    
    # Confirm
    print("\n" + "="*70)
    print("CONFIRMATION")
    print("="*70)
    print(f"Profiles:        {len(profiles)}")
    print(f"Creator:         @{creator_username}")
    print(f"Hidden:          {hidden}")
    print(f"Delay:           {delay}s")
    print(f"Keep Alive:      {keep_alive} minutes")
    print("="*70)
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    # Launch
    manager = BulkNaturalLiveEntry()
    
    await manager.launch_bulk(
        profiles=profiles,
        creator_username=creator_username,
        hidden=hidden,
        delay_between=delay
    )
    
    # Keep alive
    if manager.sessions:
        await manager.keep_alive(duration_minutes=keep_alive)
    
    print("\n✅ Bulk launch completed!")
    print("Press Enter to close all browsers...")
    input()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
