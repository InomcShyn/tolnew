// TikTok 2025 Livestream Debug Utility
// Check all compatibility requirements

export async function runLivestreamDebug(page) {
    return await page.evaluate(() => ({
        webglVendor: (() => {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (!gl) return null;
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                return debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR);
            } catch (e) {
                return null;
            }
        })(),
        
        webglRenderer: (() => {
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (!gl) return null;
                const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                return debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
            } catch (e) {
                return null;
            }
        })(),
        
        canPlay: (() => {
            const video = document.querySelector("video");
            return video ? video.canPlayType("video/mp4; codecs=\"avc1.42E01E\"") : null;
        })(),
        
        readyState: (() => {
            const video = document.querySelector("video");
            return video ? video.readyState : null;
        })(),
        
        wsExists: typeof window.__LIVE_ROOM__ !== "undefined" || 
                  typeof window.liveRoom !== "undefined",
        
        mediaCap: !!navigator.mediaCapabilities,
        
        videoElement: !!document.querySelector("video"),
        
        liveRoomPlayer: !!document.querySelector("div[data-e2e='live-room-player']"),
        
        playerContainer: !!document.querySelector("div[data-e2e='live-player-container']")
    }));
}

// Auto-click "Watch Live" button if video not found
export async function autoClickWatchLive(page) {
    try {
        // Try multiple selectors for "Watch Live" button
        const selectors = [
            'button:has-text("Watch Live")',
            'button:has-text("Xem trực tiếp")',
            'div[data-e2e="live-watch-button"]',
            'button[data-e2e="live-enter-button"]'
        ];
        
        for (const selector of selectors) {
            try {
                await page.click(selector, { timeout: 2000 });
                console.log(`[AUTO-CLICK] Clicked: ${selector}`);
                return true;
            } catch (e) {
                continue;
            }
        }
        
        return false;
    } catch (e) {
        console.log(`[AUTO-CLICK] Error: ${e.message}`);
        return false;
    }
}

// Scroll down to trigger video load
export async function scrollToTriggerVideo(page) {
    try {
        await page.evaluate(() => {
            window.scrollBy(0, 200);
        });
        console.log('[SCROLL] Scrolled down 200px');
        return true;
    } catch (e) {
        console.log(`[SCROLL] Error: ${e.message}`);
        return false;
    }
}

// Start engagement loop for view counting
export function startEngagementLoop(page) {
    return page.evaluate(() => {
        // Timeupdate loop for video
        const video = document.querySelector('video');
        if (video) {
            window.__timeupdateInterval = setInterval(() => {
                if (video && !video.paused) {
                    video.dispatchEvent(new Event('timeupdate'));
                }
            }, 5000);
        }
        
        // Mouse movement loop
        window.__mousemoveInterval = setInterval(() => {
            document.body.dispatchEvent(new MouseEvent('mousemove', {
                bubbles: true,
                cancelable: true,
                view: window
            }));
        }, 10000);
        
        // Visibility change loop
        window.__visibilityInterval = setInterval(() => {
            document.body.dispatchEvent(new Event('visibilitychange'));
        }, 15000);
        
        console.log('[ENGAGEMENT] Loops started');
    });
}
