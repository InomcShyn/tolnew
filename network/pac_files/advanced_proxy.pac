var FindProxyForURL = function(init, profiles) {
    return function(url, host) {
        "use strict";
        var result = init, scheme = url.substr(0, url.indexOf(":"));
        do {
            if (!profiles[result]) return result;
            result = profiles[result];
            if (typeof result === "function") result = result(url, host, scheme);
        } while (typeof result !== "string" || result.charCodeAt(0) === 43);
        return result;
    };
}("+proxy", {
    "+proxy": function(url, host, scheme) {
        "use strict";
        // Local addresses - direct connection
        if (/^127\.0\.0\.1$/.test(host) || /^::1$/.test(host) || /^localhost$/.test(host)) return "DIRECT";
        
        // Chrome internal addresses - direct connection
        if (/^chrome-extension:\/\//.test(url)) return "DIRECT";
        if (/^chrome:\/\//.test(url)) return "DIRECT";
        if (/^chrome-devtools:\/\//.test(url)) return "DIRECT";
        
        // Social media sites - use real proxy
        if (/facebook\.com|twitter\.com|instagram\.com|tiktok\.com|youtube\.com/.test(host)) {
            return "PROXY 146.19.196.16:40742";
        }
        
        // Other sites - direct connection
        return "DIRECT";
    }
});