#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process-Level Memory Monitor
Đo TỔNG RAM của Chrome profile (tất cả processes)
Không dựa vào JS heap
"""

import psutil
import time
import platform
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ProcessMemoryInfo:
    """Thông tin memory của một process"""
    pid: int
    name: str
    type: str  # browser, renderer, gpu, network, utility
    rss_mb: float  # Resident Set Size (RAM thực tế)
    vms_mb: float  # Virtual Memory Size
    cpu_percent: float
    num_threads: int


class ProcessMemoryMonitor:
    """
    Đo memory theo process-level
    Tổng RSS của: Browser + Renderer + GPU + Network + Utility
    """
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.memory_history: List[Tuple[float, float]] = []  # (timestamp, total_rss_mb)
        
    def discover_chrome_processes(self) -> List[Dict]:
        """
        Tìm tất cả Chrome processes của profile
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info.get('name', '')
                if not proc_name:
                    continue
                    
                # Check if Chrome process
                if 'chrome' not in proc_name.lower():
                    continue
                
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue
                
                cmdline_str = ' '.join(cmdline)
                
                # Check if belongs to this profile
                if self.profile_name in cmdline_str:
                    process_type = self._classify_process(cmdline_str)
                    
                    processes.append({
                        'pid': proc.info['pid'],
                        'type': process_type,
                        'process': proc,
                        'cmdline': cmdline_str
                    })
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return processes
    
    def _classify_process(self, cmdline: str) -> str:
        """
        Phân loại process type từ command line
        """
        if '--type=renderer' in cmdline:
            return 'renderer'
        elif '--type=gpu-process' in cmdline:
            return 'gpu'
        elif '--type=utility' in cmdline:
            return 'utility'
        elif '--type=network' in cmdline or 'NetworkService' in cmdline:
            return 'network'
        elif '--type=' not in cmdline:
            return 'browser'  # Main browser process
        else:
            return 'other'
    
    def measure_total_memory(self) -> Dict:
        """
        Đo TỔNG memory (RSS) của tất cả processes
        Returns: {
            'total_mb': float,
            'breakdown': {browser, renderer, gpu, network, utility, other},
            'process_count': int,
            'details': [...]
        }
        """
        processes = self.discover_chrome_processes()
        
        memory_breakdown = {
            'browser': 0.0,
            'renderer': 0.0,
            'gpu': 0.0,
            'network': 0.0,
            'utility': 0.0,
            'other': 0.0,
        }
        
        process_details = []
        
        for proc_info in processes:
            try:
                proc = proc_info['process']
                mem_info = proc.memory_info()
                
                # RSS = Resident Set Size (RAM thực tế đang dùng)
                rss_mb = mem_info.rss / 1024 / 1024
                vms_mb = mem_info.vms / 1024 / 1024
                
                # CPU usage
                try:
                    cpu_percent = proc.cpu_percent(interval=0.1)
                except:
                    cpu_percent = 0.0
                
                # Thread count
                try:
                    num_threads = proc.num_threads()
                except:
                    num_threads = 0
                
                proc_type = proc_info['type']
                memory_breakdown[proc_type] += rss_mb
                
                process_details.append({
                    'pid': proc_info['pid'],
                    'type': proc_type,
                    'rss_mb': round(rss_mb, 1),
                    'vms_mb': round(vms_mb, 1),
                    'cpu_percent': round(cpu_percent, 1),
                    'num_threads': num_threads
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        # Calculate total
        total_mb = sum(memory_breakdown.values())
        
        # Record history
        self.memory_history.append((time.time(), total_mb))
        
        # Keep last 30 minutes
        cutoff_time = time.time() - 1800
        self.memory_history = [
            (t, m) for t, m in self.memory_history if t > cutoff_time
        ]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_mb': round(total_mb, 1),
            'breakdown': {k: round(v, 1) for k, v in memory_breakdown.items()},
            'process_count': len(processes),
            'details': process_details
        }
    
    def get_memory_trend(self) -> Dict:
        """
        Phân tích xu hướng memory (phát hiện leak)
        """
        if len(self.memory_history) < 10:
            return {
                'trend': 'unknown',
                'slope_mb_per_min': 0.0,
                'samples': len(self.memory_history)
            }
        
        # Get last 10 samples
        recent = self.memory_history[-10:]
        times = [t for t, _ in recent]
        mems = [m for _, m in recent]
        
        # Calculate slope (MB per minute)
        time_delta_sec = times[-1] - times[0]
        mem_delta_mb = mems[-1] - mems[0]
        
        if time_delta_sec == 0:
            return {
                'trend': 'stable',
                'slope_mb_per_min': 0.0,
                'samples': len(recent)
            }
        
        slope_mb_per_sec = mem_delta_mb / time_delta_sec
        slope_mb_per_min = slope_mb_per_sec * 60
        
        # Classify trend
        if slope_mb_per_min > 5.0:  # Tăng > 5 MB/min
            trend = 'increasing'
        elif slope_mb_per_min < -5.0:  # Giảm > 5 MB/min
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'slope_mb_per_min': round(slope_mb_per_min, 2),
            'samples': len(recent),
            'avg_mb': round(sum(mems) / len(mems), 1),
            'min_mb': round(min(mems), 1),
            'max_mb': round(max(mems), 1)
        }
    
    def format_memory_report(self, mem_data: Dict) -> str:
        """
        Format memory report cho logging
        """
        lines = []
        lines.append(f"{'='*70}")
        lines.append(f"TOTAL RAM: {mem_data['total_mb']:.1f} MB ({mem_data['process_count']} processes)")
        lines.append(f"{'='*70}")
        
        breakdown = mem_data['breakdown']
        lines.append(f"  Browser:   {breakdown['browser']:>6.1f} MB")
        lines.append(f"  Renderer:  {breakdown['renderer']:>6.1f} MB")
        lines.append(f"  GPU:       {breakdown['gpu']:>6.1f} MB")
        lines.append(f"  Network:   {breakdown['network']:>6.1f} MB")
        lines.append(f"  Utility:   {breakdown['utility']:>6.1f} MB")
        if breakdown['other'] > 0:
            lines.append(f"  Other:     {breakdown['other']:>6.1f} MB")
        
        # Trend analysis
        trend = self.get_memory_trend()
        if trend['trend'] != 'unknown':
            lines.append(f"{'='*70}")
            lines.append(f"Trend: {trend['trend']} ({trend['slope_mb_per_min']:+.2f} MB/min)")
            lines.append(f"Range: {trend['min_mb']:.1f} - {trend['max_mb']:.1f} MB")
        
        lines.append(f"{'='*70}")
        
        return '\n'.join(lines)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE USAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_monitor(profile_name: str = "X-001", duration_sec: int = 60):
    """
    Test monitor với profile
    """
    print(f"\n🔍 Testing Process Memory Monitor")
    print(f"Profile: {profile_name}")
    print(f"Duration: {duration_sec} seconds\n")
    
    monitor = ProcessMemoryMonitor(profile_name)
    
    start_time = time.time()
    
    while time.time() - start_time < duration_sec:
        # Measure memory
        mem_data = monitor.measure_total_memory()
        
        # Print report
        print(f"\n[{time.strftime('%H:%M:%S')}]")
        print(monitor.format_memory_report(mem_data))
        
        # Wait
        time.sleep(10)
    
    print("\n✅ Test completed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
    else:
        profile_name = input("Profile name (e.g. X-001): ").strip()
    
    if not profile_name:
        print("❌ Profile name required")
        sys.exit(1)
    
    try:
        test_monitor(profile_name, duration_sec=300)  # 5 minutes
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
