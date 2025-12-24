#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Livestream Launcher
- Launch 0-100 profiles
- Open livestream link
- Kill all Chrome
"""

import os
import sys
import time
import asyncio
import psutil
import configparser

# Add current directory to path
sys.path.insert(0, os.getcwd())

from core.chrome_manager import ChromeProfileManager
from core.omocaptcha_client import OMOcaptchaClient
from core.tiktok_captcha_solver import TikTokCaptchaSolver


class SimpleLivestreamLauncher:
    def __init__(self):
        self.manager = ChromeProfileManager()
        self.launched_profiles = []
        self.loop = None
        
        # ✅ Load OMOcaptcha API key from config
        self.captcha_solver = None
        self._init_captcha_solver()
    
    def _init_captcha_solver(self):
        """Initialize captcha solver from config"""
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            
            api_key = config.get('CAPTCHA', 'omocaptcha_api_key', fallback='')
            
            if api_key and api_key.strip():
                print(f"[CAPTCHA] ✅ OMOcaptcha API key loaded")
                omocaptcha_client = OMOcaptchaClient(api_key=api_key.strip())
                self.captcha_solver = TikTokCaptchaSolver(omocaptcha_client)
            else:
                print(f"[CAPTCHA] ⚠️ No API key in config.ini - captcha auto-solve disabled")
                print(f"[CAPTCHA]    Add your key to [CAPTCHA] section: omocaptcha_api_key = YOUR_KEY")
        except Exception as e:
            print(f"[CAPTCHA] ⚠️ Failed to load captcha solver: {e}")
    
    def get_all_profiles(self):
        """Get all profiles"""
        return self.manager.get_all_profiles()
    
    def kill_all_chrome(self):
        """Kill all Chrome processes"""
        try:
            print("\n" + "=" * 70)
            print("KILLING ALL CHROME PROCESSES")
            print("=" * 70)
            
            killed_count = 0
            chrome_processes = []
            
            # Find all Chrome processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'chrome' in proc_name or 'chromium' in proc_name:
                        chrome_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if not chrome_processes:
                print("\n✅ No Chrome processes running")
                return True
            
            print(f"\nFound {len(chrome_processes)} Chrome processes")
            
            # Kill processes
            for proc in chrome_processes:
                try:
                    proc.terminate()
                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Wait
            time.sleep(2)
            
            # Force kill if still running
            for proc in chrome_processes:
                try:
                    if proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            print(f"\n✅ Killed {killed_count} Chrome processes")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error killing Chrome: {e}")
            return False
    
    async def launch_profile_async(self, profile_name: str, url: str, hidden: bool = False, fake_headless: bool = False, true_headless: bool = False, max_retries: int = 3):
        """Launch single profile (async) with retry logic - ✅ PATCH 15: Improved retry"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"   Retry {attempt}/{max_retries-1}...")
                    # ✅ PATCH 15: Exponential backoff
                    wait_time = 2 ** attempt  # 2s, 4s, 8s
                    print(f"   Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                
                # Headless mode configuration
                # Extensions are no longer supported
                
                # Map fake_headless/true_headless to headless parameter
                # fake_headless (NEW mode) = headless with "new" channel
                # true_headless (HEADLESS mode) = headless=True
                use_headless = true_headless  # Only true_headless uses headless=True
                
                # Only use ultra_low_memory for headless modes
                use_ultra_low = true_headless or fake_headless
                
                success, result = await self.manager.launch_chrome_profile_async(
                    profile_name=profile_name,
                    hidden=hidden if not fake_headless else False,  # fake_headless doesn't use hidden
                    start_url=url,
                    optimized_mode=False,
                    ultra_low_memory=use_ultra_low,  # Only for headless modes
                    headless=use_headless
                )
                
                if success:
                    # ✅ PATCH 15: Verify page is responsive
                    try:
                        await asyncio.wait_for(
                            result.evaluate('1 + 1'),
                            timeout=5.0
                        )
                        print(f"   ✅ Page verified responsive")
                    except Exception as e:
                        print(f"   ⚠️ Page not responsive: {e}")
                        last_error = f"Page not responsive: {e}"
                        if attempt < max_retries - 1:
                            print(f"   Will retry...")
                            continue
                        else:
                            return False
                    
                    # ✅ Auto-solve captcha if enabled and page available
                    if self.captcha_solver and result:
                        try:
                            page = result  # result is the page object
                            print(f"   [CAPTCHA] Checking for captcha...")
                            
                            # Wait and solve captcha (timeout 15s)
                            captcha_solved = await self.captcha_solver.wait_and_solve_captcha(
                                page, 
                                timeout=15
                            )
                            
                            if captcha_solved:
                                print(f"   [CAPTCHA] ✅ Ready (no captcha or solved)")
                            else:
                                print(f"   [CAPTCHA] ⚠️ Captcha detection timeout or failed")
                        except Exception as e:
                            print(f"   [CAPTCHA] ⚠️ Error: {e}")
                    
                    self.launched_profiles.append(profile_name)
                    return True
                else:
                    if attempt < max_retries - 1:
                        print(f"   Failed, will retry...")
                    else:
                        return False
                    
            except Exception as e:
                error_msg = str(e)
                if "Connection closed" in error_msg or "timeout" in error_msg.lower():
                    if attempt < max_retries - 1:
                        print(f"   Connection error, retrying...")
                    else:
                        print(f"❌ Error after {max_retries} attempts: {e}")
                        return False
                else:
                    print(f"❌ Error: {e}")
                    return False
        
        return False
    
    async def launch_multiple_async(
        self,
        profiles: list,
        url: str,
        delay: float = 1.0,
        hidden: bool = False,
        fake_headless: bool = False,
        true_headless: bool = False
    ):
        """Launch multiple profiles (async)"""
        print("\n" + "=" * 70)
        print("LAUNCHING PROFILES")
        print("=" * 70)
        print(f"Profiles: {len(profiles)}")
        print(f"URL: {url}")
        
        if true_headless:
            mode_text = "HEADLESS (True headless, max RAM save)"
        elif fake_headless:
            mode_text = "NEW (Window 1x1 pixel)"
        elif hidden:
            mode_text = "HIDDEN (Minimize to taskbar)"
        else:
            mode_text = "VISIBLE"
        
        print(f"Mode: {mode_text}")
        print(f"RAM Optimization: {'ULTRA LOW' if (fake_headless or true_headless) else 'NORMAL (GPU enabled)'}")
        print(f"Delay: {delay}s")
        print("=" * 70)
        
        success_count = 0
        failed_count = 0
        start_time = time.time()
        
        for i, profile_name in enumerate(profiles, 1):
            print(f"\n[{i}/{len(profiles)}] Launching {profile_name}...")
            
            success = await self.launch_profile_async(profile_name, url, hidden, fake_headless, true_headless)
            
            if success:
                print(f"✅ {profile_name} launched")
                success_count += 1
            else:
                print(f"❌ {profile_name} failed")
                failed_count += 1
            
            # Delay before next launch
            if i < len(profiles):
                # Delay before next launch
                await asyncio.sleep(delay)
        
        total_time = time.time() - start_time
        
        # Results
        print("\n" + "=" * 70)
        print("RESULTS")
        print("=" * 70)
        print(f"✅ Success: {success_count}/{len(profiles)}")
        print(f"❌ Failed: {failed_count}/{len(profiles)}")
        print(f"⏱️  Total time: {total_time:.1f}s")
        print(f"⚡ Average: {total_time/len(profiles):.2f}s per profile")
        print("=" * 70)
        
        return success_count, failed_count
    
    def launch_multiple(self, profiles: list, url: str, delay: float = 1.0, hidden: bool = False, fake_headless: bool = False, true_headless: bool = False):
        """Launch multiple profiles (sync wrapper)"""
        # Sử dụng cùng một event loop để tránh Playwright connection bị đóng
        if self.loop is None or self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        # ✅ Extensions are no longer supported - always skip
        return self.loop.run_until_complete(self.launch_multiple_async(profiles, url, delay, hidden, fake_headless, true_headless))
    
    def cleanup(self):
        """Cleanup"""
        try:
            self.manager.shutdown()
        except:
            pass
        
        # Close event loop
        if self.loop and not self.loop.is_closed():
            try:
                self.loop.close()
            except:
                pass


async def test_hidden_launch(launcher):
    """Test launch với hidden mode"""
    print("\n" + "=" * 70)
    print("TEST HIDDEN LAUNCH")
    print("=" * 70)
    
    # Get profiles
    all_profiles = launcher.get_all_profiles()
    
    if not all_profiles:
        print("\n❌ No profiles found")
        input("Press Enter to continue...")
        return
    
    print(f"\n✅ Found {len(all_profiles)} profiles")
    
    # Test với 1 profile
    test_profile = all_profiles[0]
    test_url = "https://www.google.com"
    
    print(f"\nTest profile: {test_profile}")
    print(f"Test URL: {test_url}")
    print(f"Mode: HIDDEN (Minimize)")
    
    confirm = input("\nContinue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    # Launch
    print(f"\nLaunching...")
    
    try:
        success = await launcher.launch_profile_async(
            profile_name=test_profile,
            url=test_url,
            hidden=True  # HIDDEN MODE
        )
        
        if success:
            print(f"\n✅ SUCCESS!")
            print(f"Profile {test_profile} launched in HIDDEN mode")
            print(f"\nCheck taskbar - Chrome should be minimized")
            print(f"Window should NOT be visible on screen")
            
            # Wait to observe
            print(f"\nWaiting 10 seconds to observe...")
            await asyncio.sleep(10)
            
            print(f"\n✅ Test completed successfully")
            
        else:
            print(f"\n❌ FAILED to launch profile")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")


def main():
    """Main function"""
    
    # Fix encoding for Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    
    launcher = SimpleLivestreamLauncher()
    
    while True:
        print("\n" + "=" * 70)
        print("SIMPLE LIVESTREAM LAUNCHER")
        print("=" * 70)
        print("\n1. Launch profiles (VISIBLE mode)")
        print("2. Launch profiles (HIDDEN mode - Minimize to taskbar)")
        print("3. Launch profiles (NEW mode - Window 1x1 pixel)")
        print("4. Launch profiles (HEADLESS mode - True headless, max RAM save)")
        print("5. Manual launch (Choose profiles one by one)")
        print("6. Test HIDDEN mode (1 profile)")
        print("7. Test NEW mode (1 profile - Window 1x1 pixel)")
        print("8. Test HEADLESS mode (1 profile - True headless)")
        print("9. Kill all Chrome processes")
        print("10. Exit")
        
        choice = input("\nChoice (1-10): ").strip()
        
        if choice in ('1', '2', '3', '4'):
            # Launch profiles (visible, hidden, NEW, or HEADLESS)
            hidden = (choice == '2')
            fake_headless = (choice == '3')  # Window 1x1 pixel
            true_headless = (choice == '4')  # True headless
            
            all_profiles = launcher.get_all_profiles()
            
            if not all_profiles:
                print("\n❌ No profiles found in chrome_profiles/")
                continue
            
            print(f"\n✅ Found {len(all_profiles)} profiles")
            
            # Get number of profiles to launch
            print(f"\nHow many profiles to launch? (1-{len(all_profiles)})")
            try:
                count = int(input("Count: ").strip())
                if count < 1 or count > len(all_profiles):
                    print(f"❌ Invalid count. Must be 1-{len(all_profiles)}")
                    continue
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                continue
            
            profiles = all_profiles[:count]
            
            # Get livestream URL
            print("\nEnter livestream URL:")
            print("Example: https://www.tiktok.com/@username/live")
            url = input("URL: ").strip()
            
            if not url:
                print("❌ URL is required!")
                continue
            
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Get delay
            print("\nDelay between launches (seconds):")
            print("Recommended: 2.0-3.0 seconds (to avoid connection errors)")
            try:
                delay = float(input("Delay (default 2.0): ").strip() or "2.0")
                if delay < 0.5:
                    print("⚠️  Delay too short, using minimum 0.5s")
                    delay = 0.5
            except ValueError:
                delay = 2.0
            
            # Confirm
            print("\n" + "=" * 70)
            print("READY TO LAUNCH")
            print("=" * 70)
            print(f"Profiles: {count}")
            print(f"URL: {url}")
            
            if true_headless:
                mode_text = "HEADLESS (True headless, max RAM save)"
            elif fake_headless:
                mode_text = "NEW (Window 1x1 pixel)"
            elif hidden:
                mode_text = "HIDDEN (Minimize to taskbar)"
            else:
                mode_text = "VISIBLE"
            
            print(f"Mode: {mode_text}")
            print(f"Delay: {delay}s")
            print(f"Estimated time: {count * delay:.0f}s ({count * delay / 60:.1f} minutes)")
            print("=" * 70)
            
            confirm = input("\nContinue? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Cancelled")
                continue
            
            # Launch
            try:
                success_count, failed_count = launcher.launch_multiple(
                    profiles=profiles,
                    url=url,
                    delay=delay,
                    hidden=hidden,
                    fake_headless=fake_headless,
                    true_headless=true_headless
                )
                
                print(f"\n✅ COMPLETE!")
                print(f"Launched {success_count} profiles successfully")
                
                if failed_count > 0:
                    print(f"⚠️  {failed_count} profiles failed")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("Press Enter to continue...")
        
        # ✅ choice == '4' is handled above (Launch profiles HEADLESS mode)
        
        elif choice == '5':
            # Manual launch - choose profiles one by one
            all_profiles = launcher.get_all_profiles()
            
            if not all_profiles:
                print("\n❌ No profiles found in chrome_profiles/")
                continue
            
            print(f"\n✅ Found {len(all_profiles)} profiles")
            
            # Choose mode
            print("\nChoose launch mode:")
            print("1. VISIBLE")
            print("2. HIDDEN (Minimize)")
            print("3. NEW (Window 1x1 pixel)")
            print("4. HEADLESS (True headless)")
            mode_choice = input("Mode (1-4): ").strip()
            
            if mode_choice not in ('1', '2', '3', '4'):
                print("❌ Invalid mode")
                continue
            
            hidden = (mode_choice == '2')
            fake_headless = (mode_choice == '3')
            true_headless = (mode_choice == '4')
                        
            # Get URL
            print("\nEnter URL to open:")
            url = input("URL: ").strip()
            if not url:
                print("❌ URL is required!")
                continue
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Manual launch loop
            print("\n" + "=" * 70)
            print("MANUAL LAUNCH MODE")
            print("=" * 70)
            
            if true_headless:
                mode_text = "HEADLESS (True headless)"
            elif fake_headless:
                mode_text = "NEW (Window 1x1 pixel)"
            elif hidden:
                mode_text = "HIDDEN (Minimize)"
            else:
                mode_text = "VISIBLE"
            
            print(f"Mode: {mode_text}")
            print(f"URL: {url}")
            print("\nType profile number to launch (or 'q' to quit)")
            print("=" * 70)
            
            launched_count = 0
            
            while True:
                # Show available profiles
                print(f"\nAvailable profiles ({len(all_profiles)}):")
                for i, profile in enumerate(all_profiles[:20], 1):  # Show first 20
                    status = "✅" if profile in launcher.launched_profiles else "⭕"
                    print(f"{i:2d}. {status} {profile}")
                
                if len(all_profiles) > 20:
                    print(f"... and {len(all_profiles) - 20} more")
                
                print(f"\nLaunched: {launched_count}/{len(all_profiles)}")
                
                choice_input = input("\nProfile number (or 'q' to quit, 'all' for remaining): ").strip().lower()
                
                if choice_input == 'q':
                    print("Exiting manual launch mode...")
                    break
                
                if choice_input == 'all':
                    # Launch all remaining profiles
                    remaining = [p for p in all_profiles if p not in launcher.launched_profiles]
                    if not remaining:
                        print("✅ All profiles already launched!")
                        continue
                    
                    print(f"\nLaunching {len(remaining)} remaining profiles...")
                    confirm = input("Continue? (yes/no): ").strip().lower()
                    if confirm != 'yes':
                        continue
                    
                    try:
                        if launcher.loop is None or launcher.loop.is_closed():
                            launcher.loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(launcher.loop)
                        
                        success_count, failed_count = launcher.launch_multiple(
                            profiles=remaining,
                            url=url,
                            delay=2.0,
                            hidden=hidden,
                            fake_headless=fake_headless,
                            true_headless=true_headless
                        )
                        
                        launched_count += success_count
                        print(f"\n✅ Batch complete! Total launched: {launched_count}")
                        
                    except Exception as e:
                        print(f"\n❌ Error: {e}")
                    
                    continue
                
                try:
                    profile_idx = int(choice_input) - 1
                    if profile_idx < 0 or profile_idx >= len(all_profiles):
                        print("❌ Invalid profile number")
                        continue
                    
                    profile_name = all_profiles[profile_idx]
                    
                    if profile_name in launcher.launched_profiles:
                        print(f"⚠️  {profile_name} already launched!")
                        continue
                    
                    # Launch profile
                    print(f"\nLaunching {profile_name}...")
                    
                    try:
                        if launcher.loop is None or launcher.loop.is_closed():
                            launcher.loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(launcher.loop)
                        
                        success = launcher.loop.run_until_complete(
                            launcher.launch_profile_async(profile_name, url, hidden, fake_headless, true_headless)
                        )
                        
                        if success:
                            print(f"✅ {profile_name} launched successfully!")
                            launched_count += 1
                        else:
                            print(f"❌ {profile_name} failed to launch")
                    
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                except ValueError:
                    print("❌ Please enter a valid number")
            
            input("\nPress Enter to continue...")
        
        elif choice == '6':
            # Test HIDDEN mode
            try:
                if launcher.loop is None or launcher.loop.is_closed():
                    launcher.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(launcher.loop)
                
                launcher.loop.run_until_complete(test_hidden_launch(launcher))
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("Press Enter to continue...")
        
        elif choice == '7':
            # Test NEW mode (Window 1x1 pixel)
            async def test_new_mode():
                # Get profiles
                all_profiles = launcher.get_all_profiles()
                
                if not all_profiles:
                    print("\n❌ No profiles found")
                    input("Press Enter to continue...")
                    return
                
                print(f"\n✅ Found {len(all_profiles)} profiles")
                
                # Test với 1 profile
                test_profile = all_profiles[0]
                test_url = "https://www.google.com"
                
                print(f"\nTest profile: {test_profile}")
                print(f"Test URL: {test_url}")
                print(f"Mode: NEW (Headless)")
                print(f"No window visible - Chrome runs in background")
                
                confirm = input("\nContinue? (yes/no): ").strip().lower()
                if confirm != 'yes':
                    print("❌ Cancelled")
                    return
                
                # Launch with headless=True
                print(f"\nLaunching in NEW mode (headless)...")
                
                try:
                    success = await launcher.launch_profile_async(
                        profile_name=test_profile,
                        url=test_url,
                        hidden=False,
                        fake_headless=True,  # NEW MODE = Window 1x1 pixel
                        true_headless=False
                    )
                except Exception as e:
                    print(f"❌ Error: {e}")
                    success = False
                
                if success:
                    print(f"\n✅ SUCCESS!")
                    print(f"Profile {test_profile} launched in NEW mode")
                    print(f"\nNo window visible - Chrome runs in background")
                    print(f"Check Task Manager to see Chrome process")
                    
                    # Wait to observe
                    print(f"\nWaiting 10 seconds to observe...")
                    await asyncio.sleep(10)
                    
                    print(f"\n✅ Test completed successfully")
                    
                else:
                    print(f"\n❌ FAILED to launch profile")
                
                input("\nPress Enter to continue...")
            
            try:
                if launcher.loop is None or launcher.loop.is_closed():
                    launcher.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(launcher.loop)
                
                launcher.loop.run_until_complete(test_new_mode())
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("Press Enter to continue...")
        
        elif choice == '8':
            # Test HEADLESS mode (True headless)
            async def test_headless():
                # Get profiles
                all_profiles = launcher.get_all_profiles()
                
                if not all_profiles:
                    print("\n❌ No profiles found")
                    input("Press Enter to continue...")
                    return
                
                print(f"\n✅ Found {len(all_profiles)} profiles")
                
                # Test với 1 profile
                test_profile = all_profiles[0]
                test_url = "https://www.google.com"
                
                print(f"\nTest profile: {test_profile}")
                print(f"Test URL: {test_url}")
                print(f"Mode: HEADLESS (No window, background only)")
                
                confirm = input("\nContinue? (yes/no): ").strip().lower()
                if confirm != 'yes':
                    print("❌ Cancelled")
                    return
                
                # Launch
                print(f"\nLaunching in HEADLESS mode...")
                
                success = await launcher.launch_profile_async(
                    profile_name=test_profile,
                    url=test_url,
                    hidden=False,
                    headless=True  # HEADLESS MODE
                )
                
                if success:
                    print(f"\n✅ SUCCESS!")
                    print(f"Profile {test_profile} launched in HEADLESS mode")
                    print(f"\nNo window should be visible - Chrome runs in background")
                    print(f"Check Task Manager to see Chrome process running")
                    
                    # Wait to observe
                    print(f"\nWaiting 10 seconds to observe...")
                    await asyncio.sleep(10)
                    
                    print(f"\n✅ Test completed successfully")
                    
                else:
                    print(f"\n❌ FAILED to launch profile")
                
                input("\nPress Enter to continue...")
            
            try:
                if launcher.loop is None or launcher.loop.is_closed():
                    launcher.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(launcher.loop)
                
                launcher.loop.run_until_complete(test_headless())
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                input("Press Enter to continue...")
        
        elif choice == '9':
            # Kill all Chrome
            print("\n⚠️  This will close ALL Chrome windows!")
            confirm = input("Continue? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                launcher.kill_all_chrome()
                input("\nPress Enter to continue...")
            else:
                print("❌ Cancelled")
        
        elif choice == '10':
            # Exit
            print("\n👋 Goodbye!")
            launcher.cleanup()
            break
        
        else:
            print("\n❌ Invalid choice. Please enter 1-10.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

