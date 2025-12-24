"""
Chrome RAM Optimizer - Safe Mode for TikTok LIVE View Counting
================================================================

Mục tiêu: Giảm RAM xuống 180-220MB/profile
Điều kiện: Giữ nguyên khả năng tính view TikTok LIVE

Nguyên tắc:
- Chỉ tối ưu tầng hệ thống/runtime
- KHÔNG thay đổi: window focus, visibilityState, audio, user activation
- KHÔNG disable: GPU, Audio, WebGL, Canvas
- KHÔNG ép: single-process, renderer-process-limit, window-size < 320x540
- Mọi tối ưu có thể đảo ngược

Baseline đã đo:
- videoElements = 0 (LIVE render qua canvas/player)
- websocketEntries = 0
- document.visibilityState = visible
- navigator.webdriver = false
- AudioContext supported
- JS Heap ~70MB
- View được tính ✓
"""

import psutil
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess
import platform

# ============================================================================
# A. CHROME LAUNCH FLAGS - SAFE ONLY
# ============================================================================

class SafeChromeFlags:
    """
    Chỉ giữ flags giảm footprint KHÔNG ảnh hưởng render LIVE
    """
    
    # Flags SAFE - giảm cache/background services
    SAFE_FLAGS = [
        # ============================================================
        # CACHE REDUCTION (Aggressive but safe)
        # ============================================================
        '--disk-cache-size=5242880',  # 5MB (was 10MB)
        '--media-cache-size=2097152',  # 2MB (was 5MB)
        '--aggressive-cache-discard',
        '--disable-application-cache',
        
        # ============================================================
        # MEMORY MANAGEMENT (Critical for RAM reduction)
        # ============================================================
        '--js-flags=--max-old-space-size=128',  # Limit JS heap to 128MB
        '--enable-low-end-device-mode',  # Enable low-end optimizations
        '--disable-dev-shm-usage',  # Use /tmp instead of /dev/shm
        
        # ============================================================
        # BACKGROUND SERVICES (Disable non-essential)
        # ============================================================
        '--disable-background-networking',
        '--disable-background-timer-throttling=false',  # Keep timers active
        '--disable-backgrounding-occluded-windows=false',  # Keep window active
        '--disable-breakpad',
        '--disable-component-update',
        '--disable-domain-reliability',
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-client-side-phishing-detection',
        
        # ============================================================
        # FEATURES REDUCTION (Safe to disable)
        # ============================================================
        '--disable-features=TranslateUI,OptimizationHints,MediaRouter,DialMediaRouteProvider',
        '--disable-features=CalculateNativeWinOcclusion,HeavyAdIntervention',
        '--disable-features=LazyFrameLoading,LazyImageLoading',
        
        # ============================================================
        # NETWORK OPTIMIZATION
        # ============================================================
        '--dns-prefetch-disable',
        '--disable-preconnect',
        '--disable-sync',
        '--disable-cloud-import',
        
        # ============================================================
        # EXTENSIONS & PLUGINS
        # ============================================================
        '--disable-extensions-http-throttling',
        '--disable-plugins-discovery',
        
        # ============================================================
        # LOGGING & REPORTING (Reduce overhead)
        # ============================================================
        '--disable-logging',
        '--log-level=3',  # Only fatal errors
        '--silent',
        
        # ============================================================
        # RENDERER OPTIMIZATION
        # ============================================================
        '--disable-software-rasterizer',  # Use GPU (faster, less RAM)
        '--enable-gpu-rasterization',
        '--enable-zero-copy',
        
        # ============================================================
        # MISC OPTIMIZATIONS
        # ============================================================
        '--disable-default-apps',
        '--disable-extensions-file-access-check',
        '--no-default-browser-check',
        '--no-first-run',
        '--disable-popup-blocking',  # Reduce popup handling overhead
    ]
    
    # Flags FORBIDDEN - phá render/media
    FORBIDDEN_FLAGS = [
        '--disable-gpu',
        '--disable-audio',
        '--disable-webgl',
        '--disable-canvas',
        '--single-process',
        '--renderer-process-limit',
        '--disable-web-security',
        '--mute-audio',
        '--disable-audio-output',
        '--disable-video',
        '--disable-media',
    ]
    
    @classmethod
    def get_safe_flags(cls) -> List[str]:
        """Trả về danh sách flags an toàn"""
        return cls.SAFE_FLAGS.copy()
    
    @classmethod
    def validate_flags(cls, flags: List[str]) -> Tuple[List[str], List[str]]:
        """
        Kiểm tra flags có chứa forbidden không
        Returns: (safe_flags, forbidden_flags)
        """
        safe = []
        forbidden = []
        
        for flag in flags:
            flag_name = flag.split('=')[0]
            if any(f.split('=')[0] == flag_name for f in cls.FORBIDDEN_FLAGS):
                forbidden.append(flag)
            else:
                safe.append(flag)
        
        return safe, forbidden


# ============================================================================
# B. PROCESS LIFECYCLE CONTROL
# ============================================================================

@dataclass
class ProcessMemoryInfo:
    """Thông tin memory của một process"""
    pid: int
    name: str
    type: str  # browser, renderer, gpu, utility
    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    cpu_percent: float
    num_threads: int
    timestamp: str


class ChromeProcessMonitor:
    """
    Theo dõi RAM theo từng Chrome process
    KHÔNG kill process khi LIVE đang chạy
    """
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.logger = logging.getLogger(f"RAMMonitor.{profile_name}")
        self.baseline_memory: Optional[Dict] = None
        self.is_live_active = False
        
    def get_chrome_processes(self) -> List[psutil.Process]:
        """Lấy tất cả Chrome processes của profile"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and self.profile_name in ' '.join(cmdline):
                        processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def classify_process_type(self, proc: psutil.Process) -> str:
        """Phân loại process type từ cmdline"""
        try:
            cmdline = ' '.join(proc.cmdline())
            
            if '--type=renderer' in cmdline:
                return 'renderer'
            elif '--type=gpu-process' in cmdline:
                return 'gpu'
            elif '--type=utility' in cmdline:
                return 'utility'
            elif '--type=' not in cmdline:
                return 'browser'
            else:
                return 'other'
        except:
            return 'unknown'
    
    def get_process_memory_info(self, proc: psutil.Process) -> ProcessMemoryInfo:
        """Lấy thông tin memory chi tiết của process"""
        try:
            mem_info = proc.memory_info()
            cpu_percent = proc.cpu_percent(interval=0.1)
            
            return ProcessMemoryInfo(
                pid=proc.pid,
                name=proc.name(),
                type=self.classify_process_type(proc),
                rss_mb=mem_info.rss / 1024 / 1024,
                vms_mb=mem_info.vms / 1024 / 1024,
                cpu_percent=cpu_percent,
                num_threads=proc.num_threads(),
                timestamp=datetime.now().isoformat()
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def get_total_memory_usage(self) -> Dict:
        """Tính tổng RAM usage theo từng loại process"""
        processes = self.get_chrome_processes()
        
        memory_by_type = {
            'browser': 0.0,
            'renderer': 0.0,
            'gpu': 0.0,
            'utility': 0.0,
            'other': 0.0,
            'total': 0.0
        }
        
        process_details = []
        
        for proc in processes:
            info = self.get_process_memory_info(proc)
            if info:
                memory_by_type[info.type] += info.rss_mb
                memory_by_type['total'] += info.rss_mb
                process_details.append(asdict(info))
        
        return {
            'profile': self.profile_name,
            'timestamp': datetime.now().isoformat(),
            'memory_by_type_mb': memory_by_type,
            'process_count': len(processes),
            'process_details': process_details
        }
    
    def set_live_status(self, is_active: bool):
        """Đánh dấu trạng thái LIVE"""
        self.is_live_active = is_active
        self.logger.info(f"LIVE status: {'ACTIVE' if is_active else 'INACTIVE'}")
    
    def can_cleanup(self) -> bool:
        """
        Kiểm tra có thể cleanup không
        KHÔNG cleanup khi LIVE đang active
        """
        if self.is_live_active:
            self.logger.warning("Cannot cleanup: LIVE is ACTIVE")
            return False
        return True


# ============================================================================
# C. MEMORY TRIMMING - PASSIVE
# ============================================================================

class PassiveMemoryTrimmer:
    """
    Memory trimming với aggressive mode
    SAFE: Chỉ trim khi KHÔNG ảnh hưởng LIVE playback
    """
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.logger = logging.getLogger(f"MemTrimmer.{profile_name}")
        self.last_trim_time = 0
        self.trim_interval = 120  # 2 phút (was 5)
        self.aggressive_mode = True  # Enable aggressive trimming
        
    def can_trim_now(self) -> bool:
        """Kiểm tra có thể trim không (theo interval)"""
        now = time.time()
        if now - self.last_trim_time < self.trim_interval:
            return False
        return True
    
    def trim_os_level(self, processes: List[psutil.Process]) -> Dict:
        """
        Gọi OS-level memory trim
        Windows: EmptyWorkingSet
        Linux: drop_caches hint
        """
        results = {
            'trimmed_count': 0,
            'errors': [],
            'platform': platform.system(),
            'freed_mb': 0
        }
        
        if platform.system() == 'Windows':
            # Windows: Try to trim working set
            for proc in processes:
                try:
                    # Get memory before
                    mem_before = proc.memory_info().rss / 1024 / 1024
                    
                    # Windows API call to trim (if available)
                    try:
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        handle = ctypes.c_void_p(proc.pid)
                        # EmptyWorkingSet
                        kernel32.K32EmptyWorkingSet(handle)
                        
                        # Get memory after
                        time.sleep(0.1)
                        mem_after = proc.memory_info().rss / 1024 / 1024
                        freed = mem_before - mem_after
                        
                        if freed > 0:
                            results['freed_mb'] += freed
                            self.logger.info(f"Trimmed PID {proc.pid}: {freed:.1f} MB")
                        
                        results['trimmed_count'] += 1
                    except:
                        # Fallback: just log
                        self.logger.debug(f"Trim hint for PID {proc.pid}")
                        results['trimmed_count'] += 1
                        
                except Exception as e:
                    results['errors'].append(str(e))
        
        elif platform.system() == 'Linux':
            # Linux: sync + drop caches
            try:
                # Sync first
                subprocess.run(['sync'], check=False)
                
                # Try to drop caches (may need sudo)
                try:
                    subprocess.run(
                        ['sudo', 'sh', '-c', 'echo 1 > /proc/sys/vm/drop_caches'],
                        check=False,
                        timeout=5
                    )
                    self.logger.info("Dropped system caches")
                except:
                    self.logger.debug("Cannot drop caches (need sudo)")
            except Exception as e:
                results['errors'].append(str(e))
        
        self.last_trim_time = time.time()
        return results
    
    def aggressive_trim_js(self) -> str:
        """
        JavaScript để aggressive trim memory
        SAFE: Chỉ clear non-essential data
        """
        return """
        (function() {
            try {
                // Clear console logs
                if (console.clear) console.clear();
                
                // Clear performance entries (old data)
                if (performance.clearResourceTimings) {
                    performance.clearResourceTimings();
                }
                if (performance.clearMarks) {
                    performance.clearMarks();
                }
                if (performance.clearMeasures) {
                    performance.clearMeasures();
                }
                
                // Hint browser to release memory
                if (window.gc && document.visibilityState === 'visible') {
                    // Only hint, don't force
                    setTimeout(() => {
                        try { window.gc(); } catch(e) {}
                    }, 100);
                }
                
                return {success: true, message: 'Memory trim hints sent'};
            } catch (e) {
                return {success: false, error: e.message};
            }
        })();
        """
    
    def suggest_gc_hint(self) -> str:
        """
        Trả về JavaScript code để hint GC
        """
        if self.aggressive_mode:
            return self.aggressive_trim_js()
        else:
            return """
            // GC hint - PASSIVE only
            if (document.visibilityState === 'hidden') {
                if (window.gc) {
                    console.log('[RAM] GC hint available');
                }
            }
            """


# ============================================================================
# D. OBSERVATION SYSTEM
# ============================================================================

class RAMObserver:
    """
    Ghi log RAM, JS heap, visibility, audio state
    KHÔNG thay đổi runtime behavior
    """
    
    def __init__(self, profile_name: str, log_dir: Path):
        self.profile_name = profile_name
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"RAMObserver.{profile_name}")
        
        # Setup file handler
        log_file = self.log_dir / f"ram_observer_{profile_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.log_file = log_file
        self.observations = []
    
    def observe(self, monitor: ChromeProcessMonitor, extra_data: Optional[Dict] = None) -> Dict:
        """
        Thu thập observation snapshot
        """
        observation = {
            'timestamp': datetime.now().isoformat(),
            'profile': self.profile_name,
            'memory': monitor.get_total_memory_usage(),
            'live_active': monitor.is_live_active,
        }
        
        if extra_data:
            observation['extra'] = extra_data
        
        self.observations.append(observation)
        
        # Log summary
        total_mb = observation['memory']['memory_by_type_mb']['total']
        self.logger.info(f"RAM: {total_mb:.1f} MB | LIVE: {monitor.is_live_active}")
        
        return observation
    
    def save_observations(self):
        """Lưu tất cả observations ra file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'profile': self.profile_name,
                'observation_count': len(self.observations),
                'observations': self.observations
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved {len(self.observations)} observations to {self.log_file}")
    
    def get_browser_state_js(self) -> str:
        """
        JavaScript để đọc browser state
        KHÔNG thay đổi gì
        """
        return """
        (function() {
            return {
                visibilityState: document.visibilityState,
                hasFocus: document.hasFocus(),
                webdriver: navigator.webdriver,
                audioContext: typeof AudioContext !== 'undefined',
                jsHeapSize: performance.memory ? {
                    used: performance.memory.usedJSHeapSize / 1024 / 1024,
                    total: performance.memory.totalJSHeapSize / 1024 / 1024,
                    limit: performance.memory.jsHeapSizeLimit / 1024 / 1024
                } : null,
                videoElements: document.querySelectorAll('video').length,
                canvasElements: document.querySelectorAll('canvas').length
            };
        })();
        """


# ============================================================================
# E. STABILITY OVER TIME
# ============================================================================

class StabilityMonitor:
    """
    Theo dõi RAM stability theo thời gian
    Phát hiện memory leak
    """
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.logger = logging.getLogger(f"Stability.{profile_name}")
        self.memory_history: List[Tuple[float, float]] = []  # (timestamp, memory_mb)
        self.spike_threshold = 50  # MB
        
    def record_memory(self, memory_mb: float):
        """Ghi lại memory usage"""
        timestamp = time.time()
        self.memory_history.append((timestamp, memory_mb))
        
        # Giữ lại 30 phút gần nhất
        cutoff = timestamp - 1800
        self.memory_history = [(t, m) for t, m in self.memory_history if t > cutoff]
    
    def check_stability(self) -> Dict:
        """
        Kiểm tra stability
        Returns: {stable, trend, spike_detected, recommendation}
        """
        if len(self.memory_history) < 10:
            return {'stable': True, 'reason': 'insufficient_data'}
        
        recent_10 = self.memory_history[-10:]
        memories = [m for _, m in recent_10]
        
        avg_memory = sum(memories) / len(memories)
        max_memory = max(memories)
        min_memory = min(memories)
        
        # Kiểm tra spike
        spike_detected = (max_memory - min_memory) > self.spike_threshold
        
        # Kiểm tra trend (tăng dần?)
        first_half = memories[:5]
        second_half = memories[5:]
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        trend = 'increasing' if avg_second > avg_first + 10 else 'stable'
        
        result = {
            'stable': not spike_detected and trend == 'stable',
            'avg_memory_mb': avg_memory,
            'max_memory_mb': max_memory,
            'min_memory_mb': min_memory,
            'spike_detected': spike_detected,
            'trend': trend,
            'recommendation': self._get_recommendation(spike_detected, trend, avg_memory)
        }
        
        if not result['stable']:
            self.logger.warning(f"Stability issue: {result}")
        
        return result
    
    def _get_recommendation(self, spike: bool, trend: str, avg_mb: float) -> str:
        """Đưa ra khuyến nghị"""
        if spike:
            return "Memory spike detected. Consider checking for memory leaks."
        if trend == 'increasing':
            return "Memory increasing over time. Monitor for potential leak."
        if avg_mb > 250:
            return "Average memory above target (220MB). Review optimization settings."
        return "Memory usage stable."


# ============================================================================
# MAIN OPTIMIZER CLASS
# ============================================================================

class ChromeRAMOptimizerSafe:
    """
    Main optimizer class - tích hợp tất cả components
    """
    
    def __init__(self, profile_name: str, log_dir: str = "ram_logs"):
        self.profile_name = profile_name
        self.log_dir = Path(log_dir)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f"RAMOptimizer.{profile_name}")
        
        # Components
        self.monitor = ChromeProcessMonitor(profile_name)
        self.trimmer = PassiveMemoryTrimmer(profile_name)
        self.observer = RAMObserver(profile_name, self.log_dir)
        self.stability = StabilityMonitor(profile_name)
        
        # Config
        self.config = {
            'target_ram_mb': 180,  # Lower target (was 200)
            'tolerance_mb': 20,
            'observation_interval': 60,  # 1 phút
            'trim_enabled': True,
            'trim_aggressive': True,  # Enable aggressive trimming
            'flags_enabled': True,
            'auto_cleanup_interval': 120,  # Auto cleanup every 2 minutes
        }
        
        self.logger.info(f"Initialized RAM Optimizer for {profile_name}")
    
    def get_safe_chrome_flags(self) -> List[str]:
        """Lấy danh sách safe flags"""
        if not self.config['flags_enabled']:
            return []
        return SafeChromeFlags.get_safe_flags()
    
    def start_monitoring(self, duration_seconds: Optional[int] = None):
        """
        Bắt đầu monitoring loop với auto cleanup
        duration_seconds: None = chạy mãi, hoặc số giây cụ thể
        """
        self.logger.info(f"Starting monitoring (duration: {duration_seconds or 'infinite'}s)")
        self.logger.info(f"Target RAM: {self.config['target_ram_mb']} MB")
        self.logger.info(f"Aggressive trim: {self.config.get('trim_aggressive', False)}")
        
        start_time = time.time()
        observation_count = 0
        last_cleanup_time = time.time()
        
        try:
            while True:
                # Check duration
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    break
                
                # Observe
                obs = self.observer.observe(self.monitor)
                total_mb = obs['memory']['memory_by_type_mb']['total']
                
                # Record for stability
                self.stability.record_memory(total_mb)
                
                # Check if RAM is too high
                target = self.config['target_ram_mb']
                tolerance = self.config['tolerance_mb']
                max_allowed = target + tolerance
                
                if total_mb > max_allowed:
                    self.logger.warning(f"RAM too high: {total_mb:.1f} MB (max: {max_allowed} MB)")
                    
                    # Force trim if aggressive mode
                    if self.config.get('trim_aggressive', False):
                        if self.monitor.can_cleanup():
                            self.logger.info("Forcing aggressive trim...")
                            processes = self.monitor.get_chrome_processes()
                            trim_result = self.trimmer.trim_os_level(processes)
                            self.logger.info(f"Trim result: {trim_result}")
                
                # Check stability
                if observation_count % 10 == 0:  # Mỗi 10 lần
                    stability = self.stability.check_stability()
                    self.logger.info(f"Stability: {stability}")
                
                # Regular trim if needed
                if self.config['trim_enabled'] and self.trimmer.can_trim_now():
                    if self.monitor.can_cleanup():
                        processes = self.monitor.get_chrome_processes()
                        trim_result = self.trimmer.trim_os_level(processes)
                        if trim_result.get('freed_mb', 0) > 0:
                            self.logger.info(f"Freed {trim_result['freed_mb']:.1f} MB")
                
                # Auto cleanup interval
                auto_cleanup_interval = self.config.get('auto_cleanup_interval', 120)
                if time.time() - last_cleanup_time > auto_cleanup_interval:
                    if self.monitor.can_cleanup():
                        self.logger.info("Auto cleanup triggered")
                        processes = self.monitor.get_chrome_processes()
                        self.trimmer.trim_os_level(processes)
                        last_cleanup_time = time.time()
                
                observation_count += 1
                time.sleep(self.config['observation_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self.observer.save_observations()
            self.logger.info(f"Total observations: {observation_count}")
    
    def get_current_status(self) -> Dict:
        """Lấy status hiện tại"""
        memory = self.monitor.get_total_memory_usage()
        stability = self.stability.check_stability()
        
        total_mb = memory['memory_by_type_mb']['total']
        target = self.config['target_ram_mb']
        tolerance = self.config['tolerance_mb']
        
        in_target = (target - tolerance) <= total_mb <= (target + tolerance)
        
        return {
            'profile': self.profile_name,
            'timestamp': datetime.now().isoformat(),
            'memory': memory,
            'stability': stability,
            'target_ram_mb': target,
            'tolerance_mb': tolerance,
            'in_target_range': in_target,
            'live_active': self.monitor.is_live_active,
            'config': self.config
        }
    
    def compare_before_after(self, before_file: Path, after_file: Path) -> Dict:
        """So sánh RAM trước và sau optimization"""
        with open(before_file, 'r') as f:
            before_data = json.load(f)
        
        with open(after_file, 'r') as f:
            after_data = json.load(f)
        
        # Tính average
        before_avg = sum(
            obs['memory']['memory_by_type_mb']['total']
            for obs in before_data['observations']
        ) / len(before_data['observations'])
        
        after_avg = sum(
            obs['memory']['memory_by_type_mb']['total']
            for obs in after_data['observations']
        ) / len(after_data['observations'])
        
        reduction_mb = before_avg - after_avg
        reduction_percent = (reduction_mb / before_avg) * 100
        
        return {
            'before_avg_mb': before_avg,
            'after_avg_mb': after_avg,
            'reduction_mb': reduction_mb,
            'reduction_percent': reduction_percent,
            'target_achieved': 180 <= after_avg <= 220
        }


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_basic_monitoring():
    """Example: Monitoring cơ bản"""
    optimizer = ChromeRAMOptimizerSafe(profile_name="X-001")
    
    # Lấy safe flags để launch Chrome
    safe_flags = optimizer.get_safe_chrome_flags()
    print("Safe Chrome flags:", safe_flags)
    
    # Đánh dấu LIVE active
    optimizer.monitor.set_live_status(True)
    
    # Monitor trong 5 phút
    optimizer.start_monitoring(duration_seconds=300)
    
    # Lấy status
    status = optimizer.get_current_status()
    print(json.dumps(status, indent=2))


def example_compare_optimization():
    """Example: So sánh trước/sau optimization"""
    optimizer = ChromeRAMOptimizerSafe(profile_name="X-001")
    
    before_file = Path("ram_logs/before_optimization.json")
    after_file = Path("ram_logs/after_optimization.json")
    
    comparison = optimizer.compare_before_after(before_file, after_file)
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*80)
    print("Chrome RAM Optimizer - Safe Mode")
    print("="*80)
    print("\nUsage:")
    print("  optimizer = ChromeRAMOptimizerSafe(profile_name='X-001')")
    print("  optimizer.start_monitoring(duration_seconds=300)")
    print("\nSee example_basic_monitoring() for full example")
