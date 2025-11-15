import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_MAX_CONCURRENCY = 6
DEFAULT_STAGGER_SEC_RANGE = (0.3, 1.0)


def _sleep_stagger():
    low, high = DEFAULT_STAGGER_SEC_RANGE
    time.sleep(random.uniform(low, high))


def run_livestream_profiles(
    manager,
    profile_names,
    start_url,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    optimized_mode: bool = True,
    ultra_low_memory: bool = False,
):
    """
    Launch livestream for selected profiles concurrently with stagger and safety flags.
    Uses tile_automation.launch_chrome_profile which handles start_url navigation.

    Returns: list of (profile_name, success: bool, message: str)
    """
    if not profile_names:
        return []
    
    if not start_url or not start_url.strip():
        print("[ERROR] [LIVESTREAM] start_url is required!")
        return [(p, False, "No start_url provided") for p in profile_names]
    
    # ✅ FILTER: Chỉ cho phép profiles đã login
    logged_in_profiles = [p for p in profile_names if manager.is_profile_logged_in(p)]
    not_logged_in = [p for p in profile_names if p not in logged_in_profiles]
    
    if not_logged_in:
        print(f"[WARNING] [LIVESTREAM] {len(not_logged_in)} profile(s) chưa login, bỏ qua: {not_logged_in[:5]}{'...' if len(not_logged_in) > 5 else ''}")
    
    if not logged_in_profiles:
        print("[ERROR] [LIVESTREAM] Không có profile nào đã login!")
        return [(p, False, "Profile chưa login") for p in profile_names]
    
    print(f"[LIVESTREAM] [FILTER] Sử dụng {len(logged_in_profiles)}/{len(profile_names)} profiles đã login")
    
    # Sử dụng chỉ profiles đã login
    profile_names = logged_in_profiles

    results = []
    
    # Import tile automation to avoid circular import
    from core.tiles.tile_automation import launch_chrome_profile as _tile_launch

    def _launch_one(pname: str):
        try:
            print(f"[LIVESTREAM] [START] Launching profile: {pname} with URL: {start_url}")
            success = False
            message = ""
            try:
                # Call tile automation (which will call original launch method)
                ret = _tile_launch(
                    manager,
                    pname,
                    hidden=False,  # Visible for livestream
                    auto_login=False,
                    login_data=None,
                    start_url=start_url,  # Ensure this is passed!
                    optimized_mode=optimized_mode,
                    ultra_low_memory=ultra_low_memory,
                )
                # Normalize return value
                if isinstance(ret, tuple):
                    success = bool(ret[0])
                    message = ret[1] if len(ret) > 1 else ("Navigated to livestream" if success else "Launch failed")
                else:
                    success = ret is not None and ret is not False
                    message = "launched and navigated" if success else "launch returned None/False"
                
                if success:
                    print(f"[SUCCESS] [LIVESTREAM] Profile {pname} launched successfully")
                else:
                    print(f"[ERROR] [LIVESTREAM] Profile {pname} failed: {message}")
                    
            except RecursionError as re:
                success = False
                message = f"Recursion error (wrapper loop): {re}"
                print(f"[CRITICAL] [LIVESTREAM] {message}")
            except Exception as e:
                success = False
                message = str(e)
                print(f"[ERROR] [LIVESTREAM] Profile {pname} exception: {e}")
            return pname, success, message
        finally:
            _sleep_stagger()

    # Launch with controlled concurrency
    print(f"[LIVESTREAM] [BATCH] Starting {len(profile_names)} profiles with max_concurrency={max_concurrency}")
    pool = ThreadPoolExecutor(max_workers=max(1, int(max_concurrency)))
    try:
        futs = [pool.submit(_launch_one, p) for p in profile_names]
        for fut in as_completed(futs):
            results.append(fut.result())
    finally:
        pool.shutdown(wait=True)

    success_count = sum(1 for _, s, _ in results if s)
    print(f"[LIVESTREAM] [BATCH] Completed: {success_count}/{len(profile_names)} successful")
    return results


def run_livestream_advanced(
    manager,
    profile_names,
    start_url: str,
    auto_out_minutes: int,
    replace_delay_seconds: int,
    max_viewers: int,
    hidden: bool,
    launch_delay: int,
    check_interval: int,
    max_retries: int,
    memory_optimization: bool,
    auto_cleanup: bool,
    show_stats: bool,
):
    """
    Advanced livestream runner for profiles already logged-in.
    - Launch up to max_viewers concurrently
    - Periodically replace viewers exceeding auto_out_minutes
    - Uses manager.launch_chrome_profile with start_url

    Returns: dict with statistics and per-profile results
    {
      'successful': [profile_names...],
      'failed': [(profile_name, message)],
      'replacements': int,
      'total_launched': int
    }
    """
    import time as _time
    import gc as _gc
    import random as _rand

    if not profile_names or not start_url:
        return {
            'successful': [],
            'failed': [(p, 'no start_url' if not start_url else 'no profiles') for p in (profile_names or [])],
            'replacements': 0,
            'total_launched': 0,
        }
    
    # ✅ FILTER: Chỉ cho phép profiles đã login
    logged_in_profiles = [p for p in profile_names if manager.is_profile_logged_in(p)]
    not_logged_in = [p for p in profile_names if p not in logged_in_profiles]
    
    if not_logged_in:
        print(f"[WARNING] [LIVESTREAM-ADV] {len(not_logged_in)} profile(s) chưa login, bỏ qua: {not_logged_in[:5]}{'...' if len(not_logged_in) > 5 else ''}")
    
    if not logged_in_profiles:
        print("[ERROR] [LIVESTREAM-ADV] Không có profile nào đã login!")
        return {
            'successful': [],
            'failed': [(p, 'Profile chưa login') for p in profile_names],
            'replacements': 0,
            'total_launched': 0,
        }
    
    print(f"[LIVESTREAM-ADV] [FILTER] Sử dụng {len(logged_in_profiles)}/{len(profile_names)} profiles đã login")
    
    # Sử dụng chỉ profiles đã login
    profile_names = logged_in_profiles

    active_viewers = {}  # profile_name -> {'start_time': float, 'retry_count': int}
    profile_pool = list(profile_names)
    # Skip profiles that are currently running (do not reuse until closed)
    try:
        profile_pool = [p for p in profile_pool if not getattr(manager, 'is_profile_in_use', lambda x: False)(p)]
        if len(profile_pool) < len(profile_names):
            skipped = set(profile_names) - set(profile_pool)
            if skipped:
                print(f"[LIVESTREAM] [SKIP] {len(skipped)} profile(s) already running, skipped: {', '.join(list(skipped)[:5])}{'...' if len(skipped)>5 else ''}")
    except Exception:
        pass
    successful = []
    failed = []
    replacements = 0
    total_launched = 0

    def _launch_one(profile_name: str, retry_count: int = 0):
        nonlocal total_launched
        try:
            # If profile turned running since last check, skip
            try:
                if getattr(manager, 'is_profile_in_use', lambda x: False)(profile_name):
                    failed.append((profile_name, 'in use'))
                    return False
            except Exception:
                pass
            total_launched += 1
            ok = False
            res = None
            # Retry loop
            for attempt in range(max(1, int(max_retries))):
                ok, res = manager.launch_chrome_profile(
                    profile_name,
                    start_url=start_url,
                    hidden=hidden,
                    auto_login=False,
                    login_data=None,
                    optimized_mode=True,
                    ultra_low_memory=True,
                )
                if ok:
                    break
                _time.sleep(2)
            if ok:
                active_viewers[profile_name] = {
                    'start_time': _time.time(),
                    'retry_count': retry_count,
                }
                if profile_name not in successful:
                    successful.append(profile_name)
                return True
            else:
                failed.append((profile_name, str(res)))
                return False
        finally:
            if launch_delay:
                _time.sleep(max(0, int(launch_delay)))

    # Initial batch - launch concurrently using ThreadPoolExecutor
    initial = profile_pool[: max(0, min(max_viewers, len(profile_pool)))]
    if initial:
        print(f"[LIVESTREAM] [ADVANCED] Launching {len(initial)} profiles concurrently...")
        from concurrent.futures import ThreadPoolExecutor as _TPE
        with _TPE(max_workers=min(len(initial), max_viewers)) as executor:
            futures = {executor.submit(_launch_one, p): p for p in initial}
            for fut in futures:
                try:
                    fut.result(timeout=120)  # Max 2 minutes per profile
                except Exception as e:
                    pname = futures[fut]
                    print(f"[ERROR] [LIVESTREAM] Profile {pname} launch exception: {e}")
                    failed.append((pname, str(e)))
    # Remove launched from pool
    profile_pool = [p for p in profile_pool if p not in active_viewers]

    # Main loop
    last_cleanup = _time.time()
    while True:
        try:
            now = _time.time()
            to_replace = []

            # Determine which viewers to replace
            for p, info in list(active_viewers.items()):
                elapsed = now - info['start_time']
                if elapsed >= max(1, int(auto_out_minutes)) * 60:
                    to_replace.append(p)

            # Replace viewers
            for p in to_replace:
                try:
                    # Stop old viewer via manager if possible (no driver handle in native mode)
                    # We rely on Chrome relaunch to supersede previous instance
                    del active_viewers[p]
                except Exception:
                    pass

                # Pick next from pool (cycle)
                next_profile = None
                if profile_pool:
                    next_profile = profile_pool.pop(0)
                else:
                    # If no pool, reuse the same profile (continuous viewing)
                    next_profile = p
                ok = _launch_one(next_profile)
                if ok:
                    replacements += 1
                _time.sleep(max(1, int(replace_delay_seconds)))

            # Top-up to maintain max_viewers
            while len(active_viewers) < max_viewers and profile_pool:
                np = profile_pool.pop(0)
                # Skip if now in-use
                if getattr(manager, 'is_profile_in_use', lambda x: False)(np):
                    failed.append((np, 'in use'))
                    continue
                _launch_one(np)

            # Cleanup/memory optimization
            if memory_optimization and (now - last_cleanup) >= max(10, int(check_interval) * 4):
                try:
                    _gc.collect()
                except Exception:
                    pass
                last_cleanup = now

            # Exit condition: nothing active and nothing left
            if not active_viewers and not profile_pool:
                break

            _time.sleep(max(1, int(check_interval)))
        except KeyboardInterrupt:
            break
        except Exception as _e:
            # Keep going on errors
            _time.sleep(max(1, int(check_interval)))

    if auto_cleanup:
        try:
            # Best-effort cleanup via manager hooks if any
            pass
        except Exception:
            pass

    return {
        'successful': successful,
        'failed': failed,
        'replacements': replacements,
        'total_launched': total_launched,
    }
