#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chrome Global RAM Diagnostics Module
=====================================
Phát hiện TẤT CẢ nguồn gốc RAM của Chrome:
- JavaScript memory
- Renderer process memory
- GPU / Media / Video memory
- Network & Streaming buffers
- Chrome internal systems
- Tab lifecycle & throttling

SAFE: Chỉ observe, KHÔNG can thiệp
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# === CHROME GLOBAL RAM DIAGNOSTICS ===
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


async def check_chrome_ram_sources(page) -> Dict:
    """
    Kiểm tra TẤT CẢ nguồn gốc RAM của Chrome.
    
    Returns: {
        "timestamp": ISO_STRING,
        "jsHeap": {...},
        "rendererProcess": {...},
        "gpuProcess": {...},
        "media": {...},
        "networkBuffer": {...},
        "chromeInternal": {...},
        "pageLifecycle": {...},
        "suspectedRamSource": [...]
    }
    """
    
    try:
        # Execute comprehensive diagnostic script
        diagnostic_data = await page.evaluate("""
            async () => {
                const data = {
                    timestamp: new Date().toISOString(),
                    
                    // ═══════════════════════════════════════════════════════════
                    // A. JavaScript Memory
                    // ═══════════════════════════════════════════════════════════
                    jsHeap: null,
                    
                    // ═══════════════════════════════════════════════════════════
                    // B. Renderer Process (via performance.memory)
                    // ═══════════════════════════════════════════════════════════
                    rendererProcess: null,
                    
                    // ═══════════════════════════════════════════════════════════
                    // C. GPU / Media / Video
                    // ═══════════════════════════════════════════════════════════
                    media: {
                        videoElements: [],
                        canvasElements: 0,
                        webglContexts: 0,
                        audioContexts: 0
                    },
                    
                    // ═══════════════════════════════════════════════════════════
                    // D. Network & Streaming Buffers
                    // ═══════════════════════════════════════════════════════════
                    networkBuffer: {
                        mseBuffers: [],
                        blobUrls: 0,
                        fetchRequests: 0
                    },
                    
                    // ═══════════════════════════════════════════════════════════
                    // E. Chrome Internal Systems
                    // ═══════════════════════════════════════════════════════════
                    chromeInternal: {
                        serviceWorkers: 0,
                        webWorkers: 0,
                        sharedWorkers: 0,
                        domNodes: 0,
                        eventListeners: 0
                    },
                    
                    // ═══════════════════════════════════════════════════════════
                    // F. Page Lifecycle & Throttling
                    // ═══════════════════════════════════════════════════════════
                    pageLifecycle: {
                        visibilityState: document.visibilityState,
                        hasFocus: document.hasFocus(),
                        hidden: document.hidden,
                        webdriver: navigator.webdriver,
                        userActivation: null,
                        pageLifecycleState: null
                    }
                };
                
                // ─────────────────────────────────────────────────────────
                // A. JavaScript Memory
                // ─────────────────────────────────────────────────────────
                if (performance.memory) {
                    data.jsHeap = {
                        usedJSHeapSize_MB: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                        totalJSHeapSize_MB: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                        jsHeapSizeLimit_MB: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024),
                        usage_percent: Math.round((performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100)
                    };
                }
                
                // ─────────────────────────────────────────────────────────
                // B. Renderer Process (estimate from performance)
                // ─────────────────────────────────────────────────────────
                data.rendererProcess = {
                    estimatedFromJS: data.jsHeap ? data.jsHeap.usedJSHeapSize_MB : null,
                    domNodesCount: document.querySelectorAll('*').length,
                    iframesCount: document.querySelectorAll('iframe').length
                };
                
                // ─────────────────────────────────────────────────────────
                // C. GPU / Media / Video Memory
                // ─────────────────────────────────────────────────────────
                
                // Video elements
                const videos = document.querySelectorAll('video');
                videos.forEach((video, idx) => {
                    try {
                        const buffered = video.buffered;
                        const bufferedRanges = [];
                        for (let i = 0; i < buffered.length; i++) {
                            bufferedRanges.push({
                                start: buffered.start(i).toFixed(2),
                                end: buffered.end(i).toFixed(2),
                                duration: (buffered.end(i) - buffered.start(i)).toFixed(2)
                            });
                        }
                        
                        data.media.videoElements.push({
                            index: idx,
                            src: video.src ? video.src.substring(0, 100) : 'blob/mse',
                            currentSrc: video.currentSrc ? video.currentSrc.substring(0, 100) : null,
                            readyState: video.readyState,
                            networkState: video.networkState,
                            paused: video.paused,
                            ended: video.ended,
                            currentTime: video.currentTime.toFixed(2),
                            duration: video.duration ? video.duration.toFixed(2) : 'unknown',
                            videoWidth: video.videoWidth,
                            videoHeight: video.videoHeight,
                            bufferedRanges: bufferedRanges,
                            totalBufferedDuration: bufferedRanges.reduce((sum, r) => sum + parseFloat(r.duration), 0).toFixed(2),
                            preload: video.preload,
                            autoplay: video.autoplay,
                            loop: video.loop
                        });
                    } catch (e) {
                        data.media.videoElements.push({
                            index: idx,
                            error: e.message
                        });
                    }
                });
                
                // Canvas elements
                data.media.canvasElements = document.querySelectorAll('canvas').length;
                
                // WebGL contexts (GPU memory)
                try {
                    const canvases = document.querySelectorAll('canvas');
                    let webglCount = 0;
                    canvases.forEach(canvas => {
                        const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
                        if (gl) webglCount++;
                    });
                    data.media.webglContexts = webglCount;
                } catch (e) {
                    data.media.webglContexts = 0;
                }
                
                // Audio contexts
                try {
                    // Can't enumerate existing AudioContexts, but can check if API exists
                    data.media.audioContexts = typeof AudioContext !== 'undefined' ? 'available' : 'unavailable';
                } catch (e) {
                    data.media.audioContexts = 'error';
                }
                
                // ─────────────────────────────────────────────────────────
                // D. Network & Streaming Buffers
                // ─────────────────────────────────────────────────────────
                
                // MSE SourceBuffers
                try {
                    const mediaElements = document.querySelectorAll('video, audio');
                    mediaElements.forEach((media, idx) => {
                        if (media.src && media.src.startsWith('blob:')) {
                            // MSE detected
                            data.networkBuffer.mseBuffers.push({
                                element: media.tagName.toLowerCase(),
                                index: idx,
                                src: media.src.substring(0, 100),
                                readyState: media.readyState,
                                networkState: media.networkState
                            });
                        }
                    });
                } catch (e) {
                    // Ignore
                }
                
                // Blob URLs (memory-backed)
                try {
                    const allElements = document.querySelectorAll('[src], [href]');
                    let blobCount = 0;
                    allElements.forEach(el => {
                        const src = el.src || el.href;
                        if (src && src.startsWith('blob:')) {
                            blobCount++;
                        }
                    });
                    data.networkBuffer.blobUrls = blobCount;
                } catch (e) {
                    data.networkBuffer.blobUrls = 0;
                }
                
                // Performance resource timing (network requests)
                try {
                    const resources = performance.getEntriesByType('resource');
                    data.networkBuffer.fetchRequests = resources.length;
                } catch (e) {
                    data.networkBuffer.fetchRequests = 0;
                }
                
                // ─────────────────────────────────────────────────────────
                // E. Chrome Internal Systems
                // ─────────────────────────────────────────────────────────
                
                // Service Workers
                try {
                    if ('serviceWorker' in navigator) {
                        const registrations = await navigator.serviceWorker.getRegistrations();
                        data.chromeInternal.serviceWorkers = registrations.length;
                    }
                } catch (e) {
                    data.chromeInternal.serviceWorkers = 0;
                }
                
                // Web Workers (can't enumerate, but can check if used)
                // This is a limitation - we can't count active workers
                data.chromeInternal.webWorkers = 'unknown';
                
                // DOM nodes
                data.chromeInternal.domNodes = document.querySelectorAll('*').length;
                
                // Event listeners (estimate)
                try {
                    // Can't enumerate all listeners, but can check common elements
                    let listenerCount = 0;
                    const elements = document.querySelectorAll('*');
                    // This is just an estimate
                    data.chromeInternal.eventListeners = 'estimated';
                } catch (e) {
                    data.chromeInternal.eventListeners = 'unknown';
                }
                
                // ─────────────────────────────────────────────────────────
                // F. Page Lifecycle & Throttling
                // ─────────────────────────────────────────────────────────
                
                // User activation
                if (navigator.userActivation) {
                    data.pageLifecycle.userActivation = {
                        hasBeenActive: navigator.userActivation.hasBeenActive,
                        isActive: navigator.userActivation.isActive
                    };
                }
                
                // Page lifecycle state (if available)
                if (document.lifecycle) {
                    data.pageLifecycle.pageLifecycleState = document.lifecycle.state;
                } else {
                    data.pageLifecycle.pageLifecycleState = 'unknown';
                }
                
                return data;
            }
        """)
        
        # ═══════════════════════════════════════════════════════════
        # HEURISTIC ANALYSIS
        # ═══════════════════════════════════════════════════════════
        
        suspected_sources = []
        
        # Analyze JS Heap
        if diagnostic_data.get('jsHeap'):
            js_heap = diagnostic_data['jsHeap']
            if js_heap['usedJSHeapSize_MB'] > 150:
                suspected_sources.append(
                    f"JS Heap high: {js_heap['usedJSHeapSize_MB']} MB "
                    f"({js_heap['usage_percent']}% of limit)"
                )
            elif js_heap['usedJSHeapSize_MB'] < 150:
                suspected_sources.append(
                    f"JS Heap normal: {js_heap['usedJSHeapSize_MB']} MB - "
                    "RAM growth likely from other sources"
                )
        
        # Analyze Video/Media
        media = diagnostic_data.get('media', {})
        video_elements = media.get('videoElements', [])
        
        for video in video_elements:
            if isinstance(video, dict) and 'error' not in video:
                # Check for paused video with active buffering
                if video.get('paused') and video.get('readyState', 0) >= 3:
                    suspected_sources.append(
                        f"Video #{video['index']}: Paused but buffered "
                        f"({video.get('totalBufferedDuration', 0)}s) - "
                        "possible buffer leak"
                    )
                
                # Check for large buffered ranges
                total_buffered = float(video.get('totalBufferedDuration', 0))
                if total_buffered > 60:  # > 1 minute buffered
                    suspected_sources.append(
                        f"Video #{video['index']}: Large buffer "
                        f"({total_buffered:.1f}s) - "
                        f"Resolution: {video.get('videoWidth')}x{video.get('videoHeight')}"
                    )
                
                # Check for high resolution
                width = video.get('videoWidth', 0)
                height = video.get('videoHeight', 0)
                if width * height > 1920 * 1080:
                    suspected_sources.append(
                        f"Video #{video['index']}: High resolution "
                        f"({width}x{height}) - high decoder memory"
                    )
        
        # Check canvas/WebGL (GPU memory)
        if media.get('canvasElements', 0) > 5:
            suspected_sources.append(
                f"Many canvas elements: {media['canvasElements']} - "
                "possible GPU memory usage"
            )
        
        if media.get('webglContexts', 0) > 0:
            suspected_sources.append(
                f"WebGL contexts active: {media['webglContexts']} - "
                "GPU memory in use"
            )
        
        # Check network buffers
        network = diagnostic_data.get('networkBuffer', {})
        if len(network.get('mseBuffers', [])) > 0:
            suspected_sources.append(
                f"MSE buffers active: {len(network['mseBuffers'])} - "
                "streaming buffer memory"
            )
        
        if network.get('blobUrls', 0) > 10:
            suspected_sources.append(
                f"Many blob URLs: {network['blobUrls']} - "
                "memory-backed resources"
            )
        
        # Check DOM size
        internal = diagnostic_data.get('chromeInternal', {})
        dom_nodes = internal.get('domNodes', 0)
        if dom_nodes > 5000:
            suspected_sources.append(
                f"Large DOM: {dom_nodes} nodes - "
                "renderer memory overhead"
            )
        
        # Check service workers
        if internal.get('serviceWorkers', 0) > 0:
            suspected_sources.append(
                f"Service Workers active: {internal['serviceWorkers']} - "
                "background memory usage"
            )
        
        # Add suspected sources to result
        diagnostic_data['suspectedRamSource'] = suspected_sources
        
        return diagnostic_data
        
    except Exception as e:
        return {
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'suspectedRamSource': [f'Diagnostic failed: {e}']
        }


def format_ram_diagnostic_report(data: Dict) -> str:
    """
    Format diagnostic data thành human-readable report
    """
    lines = []
    lines.append("\n" + "="*80)
    lines.append("🔍 CHROME RAM DIAGNOSTIC REPORT")
    lines.append("="*80)
    lines.append(f"Timestamp: {data.get('timestamp', 'unknown')}")
    lines.append("="*80)
    
    # JS Heap
    if data.get('jsHeap'):
        js = data['jsHeap']
        lines.append("\n📊 JavaScript Heap:")
        lines.append(f"  Used:    {js['usedJSHeapSize_MB']} MB")
        lines.append(f"  Total:   {js['totalJSHeapSize_MB']} MB")
        lines.append(f"  Limit:   {js['jsHeapSizeLimit_MB']} MB")
        lines.append(f"  Usage:   {js['usage_percent']}%")
    
    # Media
    if data.get('media'):
        media = data['media']
        lines.append("\n🎬 Media & GPU:")
        lines.append(f"  Video elements:  {len(media.get('videoElements', []))}")
        lines.append(f"  Canvas elements: {media.get('canvasElements', 0)}")
        lines.append(f"  WebGL contexts:  {media.get('webglContexts', 0)}")
        lines.append(f"  Audio contexts:  {media.get('audioContexts', 'unknown')}")
        
        # Video details
        for video in media.get('videoElements', []):
            if isinstance(video, dict) and 'error' not in video:
                lines.append(f"\n  Video #{video['index']}:")
                lines.append(f"    Resolution:  {video.get('videoWidth')}x{video.get('videoHeight')}")
                lines.append(f"    State:       {'Paused' if video.get('paused') else 'Playing'}")
                lines.append(f"    Ready:       {video.get('readyState')}/4")
                lines.append(f"    Buffered:    {video.get('totalBufferedDuration')}s")
                lines.append(f"    Current:     {video.get('currentTime')}s / {video.get('duration')}s")
    
    # Network buffers
    if data.get('networkBuffer'):
        net = data['networkBuffer']
        lines.append("\n🌐 Network & Buffers:")
        lines.append(f"  MSE buffers:     {len(net.get('mseBuffers', []))}")
        lines.append(f"  Blob URLs:       {net.get('blobUrls', 0)}")
        lines.append(f"  Fetch requests:  {net.get('fetchRequests', 0)}")
    
    # Chrome internal
    if data.get('chromeInternal'):
        internal = data['chromeInternal']
        lines.append("\n⚙️  Chrome Internal:")
        lines.append(f"  DOM nodes:       {internal.get('domNodes', 0)}")
        lines.append(f"  Service Workers: {internal.get('serviceWorkers', 0)}")
        lines.append(f"  Web Workers:     {internal.get('webWorkers', 'unknown')}")
    
    # Page lifecycle
    if data.get('pageLifecycle'):
        lifecycle = data['pageLifecycle']
        lines.append("\n🔄 Page Lifecycle:")
        lines.append(f"  Visibility:      {lifecycle.get('visibilityState', 'unknown')}")
        lines.append(f"  Has focus:       {lifecycle.get('hasFocus', False)}")
        lines.append(f"  Hidden:          {lifecycle.get('hidden', False)}")
        lines.append(f"  Webdriver:       {lifecycle.get('webdriver', False)}")
    
    # Suspected sources
    if data.get('suspectedRamSource'):
        lines.append("\n⚠️  SUSPECTED RAM SOURCES:")
        for source in data['suspectedRamSource']:
            lines.append(f"  • {source}")
    
    lines.append("\n" + "="*80)
    
    return '\n'.join(lines)


def detect_ram_spike(current_total_mb: float, previous_total_mb: float, threshold_mb: float = 150) -> Optional[str]:
    """
    Phát hiện RAM spike (tăng đột ngột)
    
    Returns: Warning message nếu có spike, None nếu không
    """
    if previous_total_mb is None:
        return None
    
    delta = current_total_mb - previous_total_mb
    
    if delta > threshold_mb:
        return f"⚠️  RAM SPIKE DETECTED: +{delta:.1f} MB (from {previous_total_mb:.1f} to {current_total_mb:.1f} MB)"
    
    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXAMPLE USAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def example_periodic_diagnostic(page, interval_seconds: int = 60, duration_seconds: int = 300):
    """
    Example: Chạy diagnostic định kỳ
    """
    print("\n🔍 Starting periodic Chrome RAM diagnostics...")
    print(f"Interval: {interval_seconds}s")
    print(f"Duration: {duration_seconds}s\n")
    
    start_time = time.time()
    previous_total_mb = None
    
    while time.time() - start_time < duration_seconds:
        # Run diagnostic
        diagnostic_data = await check_chrome_ram_sources(page)
        
        # Print report
        report = format_ram_diagnostic_report(diagnostic_data)
        print(report)
        
        # Check for RAM spike (if we have process-level memory)
        # This would need to be integrated with ProcessMemoryMonitor
        # For now, just log the diagnostic
        
        # Save to file (optional)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ram_diagnostic_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(diagnostic_data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved to: {filename}")
        
        # Wait
        await asyncio.sleep(interval_seconds)
    
    print("\n✅ Diagnostic completed")


if __name__ == "__main__":
    print("This module should be imported and used with Playwright page object")
    print("Example:")
    print("  from chrome_ram_diagnostics import check_chrome_ram_sources")
    print("  diagnostic_data = await check_chrome_ram_sources(page)")
