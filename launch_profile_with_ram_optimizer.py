"""
Launch Profile với RAM Optimizer Safe
Tích hợp vào hệ thống khởi động profiles hiện tại
"""

import sys
import os
import time
import threading
from pathlib import Path

sys.path.insert(0, os.getcwd())

from core.chrome_manager import ChromeProfileManager
from core.managers.profile_manager import ProfileManager
from chrome_ram_optimizer_safe import ChromeRAMOptimizerSafe, SafeChromeFlags


class ProfileLauncherWithRAMOptimizer:
    """
    Launch profiles với RAM optimization
    """
    
    def __init__(self):
        self.chrome_manager = ChromeProfileManager()
        self.profile_manager = ProfileManager()
        self.ram_optimizers = {}  # {profile_name: optimizer}
        self.monitor_threads = {}  # {profile_name: thread}
        
    def launch_profile(self, profile_name: str, hidden: bool = False, 
                      enable_ram_optimization: bool = True,
                      monitor_duration: int = 3600,
                      livestream_url: str = None):
        """
        Launch profile với RAM optimization
        
        Args:
            profile_name: Tên profile (vd: "001")
            hidden: Minimize window
            enable_ram_optimization: Bật RAM optimization
            monitor_duration: Thời gian monitor (giây), None = vô hạn
            livestream_url: URL livestream để vào thẳng (optional)
        """
        print("\n" + "="*80)
        print("🚀 LAUNCH PROFILE WITH RAM OPTIMIZER")
        print("="*80)
        print(f"Profile: {profile_name}")
        print(f"Hidden: {hidden}")
        print(f"RAM Optimization: {enable_ram_optimization}")
        if livestream_url:
            print(f"Livestream URL: {livestream_url}")
        print("="*80 + "\n")
        
        # Check profile exists
        profiles = self.profile_manager.get_all_profiles()
        if profile_name not in profiles:
            print(f"❌ Profile '{profile_name}' not found")
            return False
        
        # Initialize RAM optimizer
        if enable_ram_optimization:
            optimizer = ChromeRAMOptimizerSafe(profile_name=profile_name)
            self.ram_optimizers[profile_name] = optimizer
            
            # Get safe flags
            safe_flags = optimizer.get_safe_chrome_flags()
            print(f"[RAM] Applying {len(safe_flags)} safe flags")
            
            # TODO: Apply flags to chrome_manager
            # Hiện tại chrome_manager chưa hỗ trợ custom flags
            # Cần modify chrome_manager để accept extra_args
            print("[RAM] Note: Flags will be applied when chrome_manager supports extra_args")
        
        # Determine start URL
        if livestream_url:
            start_url = livestream_url
            auto_mark_live = True
            print(f"[LIVE] Will navigate to livestream URL")
        else:
            start_url = "https://www.tiktok.com"
            auto_mark_live = False
        
        # Launch Chrome profile
        print(f"\n[LAUNCH] Starting profile: {profile_name}")
        
        try:
            success, result = self.chrome_manager.launch_chrome_profile(
                profile_name,
                hidden=hidden,
                auto_login=False,
                login_data=None,
                start_url=start_url
            )
            
            if not success:
                print(f"❌ Failed to launch profile: {result}")
                return False
            
            print(f"✅ Profile launched successfully!")
            
            # Auto mark as LIVE if livestream URL provided
            if auto_mark_live and enable_ram_optimization:
                time.sleep(3)  # Wait for page load
                self.set_live_status(profile_name, True)
                print(f"[LIVE] Auto-marked as LIVE ACTIVE")
            
            # Start RAM monitoring in background
            if enable_ram_optimization:
                self._start_ram_monitoring(profile_name, monitor_duration)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _start_ram_monitoring(self, profile_name: str, duration: int):
        """Start RAM monitoring trong background thread"""
        optimizer = self.ram_optimizers.get(profile_name)
        if not optimizer:
            return
        
        print(f"\n[RAM] Starting monitoring for {profile_name}")
        print(f"[RAM] Duration: {duration}s ({duration//60} minutes)")
        print(f"[RAM] Logs will be saved to: ram_logs/")
        
        def monitor_thread():
            try:
                optimizer.start_monitoring(duration_seconds=duration)
            except Exception as e:
                print(f"[RAM] Monitoring error: {e}")
        
        thread = threading.Thread(target=monitor_thread, daemon=True)
        thread.start()
        self.monitor_threads[profile_name] = thread
        
        print(f"[RAM] Monitoring started in background")
    
    def set_live_status(self, profile_name: str, is_active: bool):
        """Đánh dấu profile đang xem LIVE"""
        optimizer = self.ram_optimizers.get(profile_name)
        if optimizer:
            optimizer.monitor.set_live_status(is_active)
            status = "ACTIVE" if is_active else "INACTIVE"
            print(f"[RAM] {profile_name} LIVE status: {status}")
    
    def get_ram_status(self, profile_name: str):
        """Lấy RAM status của profile"""
        optimizer = self.ram_optimizers.get(profile_name)
        if not optimizer:
            print(f"[RAM] No optimizer for {profile_name}")
            return None
        
        status = optimizer.get_current_status()
        return status
    
    def print_ram_status(self, profile_name: str):
        """In RAM status ra console"""
        status = self.get_ram_status(profile_name)
        if not status:
            return
        
        memory = status['memory']['memory_by_type_mb']
        total = memory['total']
        
        print(f"\n[RAM] {profile_name} Status:")
        print(f"  Total:    {total:.1f} MB")
        print(f"  Browser:  {memory['browser']:.1f} MB")
        print(f"  Renderer: {memory['renderer']:.1f} MB")
        print(f"  GPU:      {memory['gpu']:.1f} MB")
        print(f"  Utility:  {memory['utility']:.1f} MB")
        print(f"  Target:   {status['target_ram_mb']} ± {status['tolerance_mb']} MB")
        print(f"  In Range: {status['in_target_range']}")
        print(f"  LIVE:     {status['live_active']}")


def launch_single_profile():
    """Launch 1 profile với RAM monitoring"""
    launcher = ProfileLauncherWithRAMOptimizer()
    
    print("\n" + "="*80)
    print("LAUNCH SINGLE PROFILE WITH RAM OPTIMIZER")
    print("="*80)
    
    # Get profile name
    profile_name = input("\nProfile name (e.g. 001): ").strip()
    if not profile_name:
        print("❌ Profile name required")
        return
    
    # Livestream URL
    print("\n📺 Livestream URL (optional):")
    print("  - Leave empty: Open TikTok homepage")
    print("  - Enter URL: Navigate directly to livestream")
    livestream_url = input("URL (or Enter to skip): ").strip()
    
    if livestream_url and not livestream_url.startswith('http'):
        print("⚠️  Invalid URL, will open TikTok homepage instead")
        livestream_url = None
    
    # Hidden mode
    hidden_input = input("\nHidden mode? (y/n, default: n): ").strip().lower()
    hidden = (hidden_input == 'y')
    
    # RAM optimization
    ram_input = input("Enable RAM optimization? (y/n, default: y): ").strip().lower()
    enable_ram = (ram_input != 'n')
    
    # Monitor duration
    if enable_ram:
        duration_input = input("Monitor duration (minutes, default: 60): ").strip()
        try:
            duration_minutes = int(duration_input) if duration_input else 60
            duration_seconds = duration_minutes * 60
        except ValueError:
            duration_seconds = 3600
    else:
        duration_seconds = 0
    
    # Launch
    success = launcher.launch_profile(
        profile_name=profile_name,
        hidden=hidden,
        enable_ram_optimization=enable_ram,
        monitor_duration=duration_seconds,
        livestream_url=livestream_url
    )
    
    if not success:
        return
    
    # Interactive menu
    print("\n" + "="*80)
    print("INTERACTIVE MENU")
    print("="*80)
    print("Commands:")
    print("  status  - Show RAM status")
    print("  live    - Mark as LIVE active")
    print("  exit    - Mark as LIVE inactive")
    print("  quit    - Close browser")
    print("="*80 + "\n")
    
    try:
        while True:
            cmd = input(f"[{profile_name}] > ").strip().lower()
            
            if cmd == 'status':
                launcher.print_ram_status(profile_name)
            
            elif cmd == 'live':
                launcher.set_live_status(profile_name, True)
            
            elif cmd == 'exit':
                launcher.set_live_status(profile_name, False)
            
            elif cmd == 'quit':
                print("\n⚠️  Closing browser...")
                break
            
            elif cmd == 'help':
                print("\nCommands:")
                print("  status  - Show RAM status")
                print("  live    - Mark as LIVE active")
                print("  exit    - Mark as LIVE inactive")
                print("  quit    - Close browser")
            
            else:
                print(f"Unknown command: {cmd} (type 'help' for commands)")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")


def launch_multiple_profiles():
    """Launch nhiều profiles với RAM monitoring"""
    launcher = ProfileLauncherWithRAMOptimizer()
    
    print("\n" + "="*80)
    print("LAUNCH MULTIPLE PROFILES WITH RAM OPTIMIZER")
    print("="*80)
    
    # Get profile names
    profiles_input = input("\nProfile names (comma-separated, e.g. 001,002,003): ").strip()
    if not profiles_input:
        print("❌ Profile names required")
        return
    
    profile_names = [p.strip() for p in profiles_input.split(',')]
    
    # Livestream URL
    print("\n📺 Livestream URL (optional):")
    print("  - Leave empty: Open TikTok homepage for all")
    print("  - Enter URL: All profiles navigate to same livestream")
    livestream_url = input("URL (or Enter to skip): ").strip()
    
    if livestream_url and not livestream_url.startswith('http'):
        print("⚠️  Invalid URL, will open TikTok homepage instead")
        livestream_url = None
    
    # Hidden mode
    hidden_input = input("\nHidden mode? (y/n, default: y): ").strip().lower()
    hidden = (hidden_input != 'n')
    
    # RAM optimization
    ram_input = input("Enable RAM optimization? (y/n, default: y): ").strip().lower()
    enable_ram = (ram_input != 'n')
    
    # Monitor duration
    if enable_ram:
        duration_input = input("Monitor duration (minutes, default: 60): ").strip()
        try:
            duration_minutes = int(duration_input) if duration_input else 60
            duration_seconds = duration_minutes * 60
        except ValueError:
            duration_seconds = 3600
    else:
        duration_seconds = 0
    
    # Launch all profiles
    print(f"\n[LAUNCH] Starting {len(profile_names)} profiles...")
    
    for profile_name in profile_names:
        print(f"\n--- Launching {profile_name} ---")
        success = launcher.launch_profile(
            profile_name=profile_name,
            hidden=hidden,
            enable_ram_optimization=enable_ram,
            monitor_duration=duration_seconds,
            livestream_url=livestream_url
        )
        
        if success:
            print(f"✅ {profile_name} launched")
        else:
            print(f"❌ {profile_name} failed")
        
        # Delay giữa các launches
        time.sleep(2)
    
    # Show summary
    print("\n" + "="*80)
    print("LAUNCH SUMMARY")
    print("="*80)
    print(f"Total profiles: {len(profile_names)}")
    print(f"Launched: {len(launcher.ram_optimizers)}")
    print("="*80 + "\n")
    
    # Monitor loop
    print("Monitoring RAM every 30 seconds...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(30)
            
            print("\n" + "="*80)
            print(f"RAM STATUS - {time.strftime('%H:%M:%S')}")
            print("="*80)
            
            for profile_name in launcher.ram_optimizers.keys():
                launcher.print_ram_status(profile_name)
            
            print("="*80)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoring stopped")


def show_safe_flags():
    """Hiển thị safe flags"""
    print("\n" + "="*80)
    print("SAFE CHROME FLAGS FOR RAM OPTIMIZATION")
    print("="*80)
    
    flags = SafeChromeFlags.get_safe_flags()
    
    print(f"\nTotal: {len(flags)} flags\n")
    
    for flag in flags:
        print(f"  {flag}")
    
    print("\n" + "="*80)
    print("These flags are SAFE for TikTok LIVE view counting")
    print("="*80)


def main():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("PROFILE LAUNCHER WITH RAM OPTIMIZER")
        print("="*80)
        print("\nOptions:")
        print("  1. Launch Single Profile")
        print("  2. Launch Multiple Profiles")
        print("  3. Show Safe Flags")
        print("  0. Exit")
        print("="*80)
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            launch_single_profile()
        
        elif choice == '2':
            launch_multiple_profiles()
        
        elif choice == '3':
            show_safe_flags()
        
        elif choice == '0':
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
