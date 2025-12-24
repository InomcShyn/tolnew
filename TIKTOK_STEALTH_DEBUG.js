// ============================================================
// TIKTOK STEALTH DEBUG SCRIPT
// Copy toàn bộ script này vào Chrome DevTools Console
// ============================================================

console.log("=".repeat(80));
console.log("🔍 TIKTOK STEALTH VERIFICATION SCRIPT");
console.log("=".repeat(80));

const results = {
    checks: {},
    warnings: [],
    errors: [],
    score: 0,
    maxScore: 0
};

// ============================================================
// 1. NAVIGATOR CHECKS
// ============================================================
console.log("\n📋 1. NAVIGATOR CHECKS");
console.log("-".repeat(80));

// 1.1 webdriver
results.checks.webdriver = navigator.webdriver === false;
results.maxScore++;
if (results.checks.webdriver) {
    console.log("✅ navigator.webdriver:", navigator.webdriver);
    results.score++;
} else {
    console.log("❌ navigator.webdriver:", navigator.webdriver, "(should be false)");
    results.errors.push("navigator.webdriver is not false - TikTok will detect bot!");
}

// 1.2 plugins
results.checks.plugins = navigator.plugins.length > 0;
results.maxScore++;
if (results.checks.plugins) {
    console.log("✅ navigator.plugins.length:", navigator.plugins.length);
    results.score++;
} else {
    console.log("❌ navigator.plugins.length:", navigator.plugins.length, "(should be > 0)");
    results.errors.push("No plugins detected - headless indicator!");
}

// 1.3 mimeTypes
results.checks.mimeTypes = navigator.mimeTypes.length > 0;
results.maxScore++;
if (results.checks.mimeTypes) {
    console.log("✅ navigator.mimeTypes.length:", navigator.mimeTypes.length);
    results.score++;
} else {
    console.log("❌ navigator.mimeTypes.length:", navigator.mimeTypes.length, "(should be > 0)");
    results.errors.push("No mimeTypes detected - headless indicator!");
}

// 1.4 languages
results.checks.languages = navigator.languages && navigator.languages.length > 0;
results.maxScore++;
if (results.checks.languages) {
    console.log("✅ navigator.languages:", navigator.languages);
    results.score++;
} else {
    console.log("❌ navigator.languages:", navigator.languages, "(should have values)");
    results.warnings.push("Languages not set properly");
}

// 1.5 hardwareConcurrency
results.checks.hardwareConcurrency = navigator.hardwareConcurrency > 0;
results.maxScore++;
if (results.checks.hardwareConcurrency) {
    console.log("✅ navigator.hardwareConcurrency:", navigator.hardwareConcurrency);
    results.score++;
} else {
    console.log("❌ navigator.hardwareConcurrency:", navigator.hardwareConcurrency);
    results.warnings.push("hardwareConcurrency not set");
}

// 1.6 platform
console.log("ℹ️  navigator.platform:", navigator.platform);

// 1.7 userAgent
console.log("ℹ️  navigator.userAgent:", navigator.userAgent);
if (navigator.userAgent.includes('Headless')) {
    results.errors.push("'Headless' found in User-Agent!");
}

// ============================================================
// 2. WEBGL CHECKS (CRITICAL!)
// ============================================================
console.log("\n🎨 2. WEBGL CHECKS (CRITICAL)");
console.log("-".repeat(80));

try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    
    if (!gl) {
        console.log("❌ WebGL not available!");
        results.errors.push("WebGL not available - TikTok will NOT count views!");
        results.checks.webgl = false;
        results.maxScore++;
    } else {
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        
        if (!debugInfo) {
            console.log("⚠️  Cannot get GPU debug info");
            results.warnings.push("Cannot get GPU debug info");
            results.checks.webgl = false;
            results.maxScore++;
        } else {
            const vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
            const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
            
            console.log("   Vendor:", vendor);
            console.log("   Renderer:", renderer);
            
            // Check for headless indicators
            const headlessIndicators = ['swiftshader', 'llvmpipe', 'mesa', 'google swiftshader'];
            const isHeadlessGPU = headlessIndicators.some(indicator => 
                renderer.toLowerCase().includes(indicator)
            );
            
            results.checks.webgl = !isHeadlessGPU;
            results.maxScore++;
            
            if (isHeadlessGPU) {
                console.log("❌ HEADLESS GPU DETECTED!");
                console.log("   Renderer:", renderer);
                results.errors.push("Headless GPU detected: " + renderer + " - TikTok will NOT count views!");
            } else {
                console.log("✅ Real GPU detected");
                results.score++;
            }
        }
    }
} catch (e) {
    console.log("❌ Error checking WebGL:", e);
    results.errors.push("WebGL check error: " + e.message);
    results.checks.webgl = false;
    results.maxScore++;
}

// ============================================================
// 3. VISIBILITY CHECKS
// ============================================================
console.log("\n👁️  3. VISIBILITY CHECKS");
console.log("-".repeat(80));

// 3.1 document.hidden
results.checks.hidden = document.hidden === false;
results.maxScore++;
if (results.checks.hidden) {
    console.log("✅ document.hidden:", document.hidden);
    results.score++;
} else {
    console.log("❌ document.hidden:", document.hidden, "(should be false)");
    results.errors.push("Page is hidden - TikTok will NOT count views!");
}

// 3.2 document.visibilityState
results.checks.visibilityState = document.visibilityState === 'visible';
results.maxScore++;
if (results.checks.visibilityState) {
    console.log("✅ document.visibilityState:", document.visibilityState);
    results.score++;
} else {
    console.log("❌ document.visibilityState:", document.visibilityState, "(should be 'visible')");
    results.errors.push("visibilityState is not 'visible' - TikTok will NOT count views!");
}

// ============================================================
// 4. CHROME OBJECT CHECKS
// ============================================================
console.log("\n🌐 4. CHROME OBJECT CHECKS");
console.log("-".repeat(80));

// 4.1 window.chrome
results.checks.chrome = typeof window.chrome !== 'undefined';
results.maxScore++;
if (results.checks.chrome) {
    console.log("✅ window.chrome exists");
    results.score++;
} else {
    console.log("❌ window.chrome does not exist");
    results.warnings.push("window.chrome not defined");
}

// 4.2 chrome.runtime
if (window.chrome) {
    results.checks.chromeRuntime = typeof window.chrome.runtime !== 'undefined';
    results.maxScore++;
    if (results.checks.chromeRuntime) {
        console.log("✅ window.chrome.runtime exists");
        results.score++;
    } else {
        console.log("⚠️  window.chrome.runtime does not exist");
        results.warnings.push("chrome.runtime not defined");
    }
}

// ============================================================
// 5. PERMISSIONS CHECKS
// ============================================================
console.log("\n🔐 5. PERMISSIONS CHECKS");
console.log("-".repeat(80));

// Check notifications permission
navigator.permissions.query({name: 'notifications'}).then(result => {
    results.checks.permissions = result.state === 'prompt' || result.state === 'granted';
    results.maxScore++;
    
    if (results.checks.permissions) {
        console.log("✅ notifications permission:", result.state);
        results.score++;
    } else {
        console.log("❌ notifications permission:", result.state, "(should be 'prompt' or 'granted')");
        results.warnings.push("Permissions state suspicious: " + result.state);
    }
    
    // Continue with video checks after permissions
    checkVideo();
}).catch(e => {
    console.log("⚠️  Error checking permissions:", e);
    results.warnings.push("Cannot check permissions");
    checkVideo();
});

// ============================================================
// 6. VIDEO PLAYBACK CHECKS
// ============================================================
function checkVideo() {
    console.log("\n📹 6. VIDEO PLAYBACK CHECKS");
    console.log("-".repeat(80));
    
    const video = document.querySelector('video');
    
    if (!video) {
        console.log("⚠️  No video element found (may not be on livestream page)");
        results.warnings.push("No video element found");
        results.checks.video = false;
        results.maxScore++;
    } else {
        console.log("✅ Video element found");
        console.log("   paused:", video.paused);
        console.log("   muted:", video.muted);
        console.log("   volume:", video.volume);
        console.log("   currentTime:", video.currentTime);
        console.log("   duration:", video.duration);
        
        results.checks.video = !video.paused;
        results.maxScore++;
        
        if (video.paused) {
            console.log("❌ Video is PAUSED - views will NOT be counted!");
            results.errors.push("Video is paused - TikTok will NOT count views!");
        } else {
            console.log("✅ Video is PLAYING");
            results.score++;
        }
        
        if (video.muted && video.volume === 0) {
            console.log("⚠️  Video is MUTED with volume 0");
            results.warnings.push("Video is completely muted");
        }
    }
    
    // Continue with screen checks
    checkScreen();
}

// ============================================================
// 7. SCREEN PROPERTIES CHECKS
// ============================================================
function checkScreen() {
    console.log("\n🖥️  7. SCREEN PROPERTIES CHECKS");
    console.log("-".repeat(80));
    
    console.log("   screen.width:", screen.width);
    console.log("   screen.height:", screen.height);
    console.log("   screen.availWidth:", screen.availWidth);
    console.log("   screen.availHeight:", screen.availHeight);
    console.log("   screen.colorDepth:", screen.colorDepth);
    console.log("   window.innerWidth:", window.innerWidth);
    console.log("   window.innerHeight:", window.innerHeight);
    
    results.checks.screen = screen.width > 0 && screen.height > 0;
    results.maxScore++;
    
    if (results.checks.screen) {
        console.log("✅ Screen properties look normal");
        results.score++;
    } else {
        console.log("❌ Screen size is 0!");
        results.errors.push("Screen size is 0 - headless indicator!");
    }
    
    // Show final summary
    showSummary();
}

// ============================================================
// 8. FINAL SUMMARY
// ============================================================
function showSummary() {
    console.log("\n" + "=".repeat(80));
    console.log("📊 FINAL SUMMARY");
    console.log("=".repeat(80));
    
    const percentage = Math.round((results.score / results.maxScore) * 100);
    
    console.log("\n🎯 SCORE:", results.score + "/" + results.maxScore, "(" + percentage + "%)");
    
    if (percentage >= 90) {
        console.log("\n✅ EXCELLENT! TikTok should count views");
        console.log("   All critical checks passed");
    } else if (percentage >= 70) {
        console.log("\n⚠️  GOOD, but some issues detected");
        console.log("   Views may be counted, but not guaranteed");
    } else if (percentage >= 50) {
        console.log("\n⚠️  FAIR - Multiple issues detected");
        console.log("   Views may NOT be counted reliably");
    } else {
        console.log("\n❌ POOR - Critical issues detected");
        console.log("   TikTok will likely NOT count views!");
    }
    
    // Show errors
    if (results.errors.length > 0) {
        console.log("\n❌ ERRORS (" + results.errors.length + "):");
        results.errors.forEach((error, i) => {
            console.log("   " + (i+1) + ". " + error);
        });
    }
    
    // Show warnings
    if (results.warnings.length > 0) {
        console.log("\n⚠️  WARNINGS (" + results.warnings.length + "):");
        results.warnings.forEach((warning, i) => {
            console.log("   " + (i+1) + ". " + warning);
        });
    }
    
    // Show passed checks
    console.log("\n✅ PASSED CHECKS:");
    Object.entries(results.checks).forEach(([key, value]) => {
        if (value) {
            console.log("   ✅", key);
        }
    });
    
    // Show failed checks
    const failedChecks = Object.entries(results.checks).filter(([key, value]) => !value);
    if (failedChecks.length > 0) {
        console.log("\n❌ FAILED CHECKS:");
        failedChecks.forEach(([key, value]) => {
            console.log("   ❌", key);
        });
    }
    
    console.log("\n" + "=".repeat(80));
    console.log("🔍 Debug complete!");
    console.log("=".repeat(80));
    
    // Return results object for programmatic access
    return results;
}

// ============================================================
// EXPORT RESULTS
// ============================================================
window.tiktokStealthResults = results;
console.log("\n💡 TIP: Access results via window.tiktokStealthResults");
