
// Proxy credentials
const PROXY_USERNAME = "sA5hg";
const PROXY_PASSWORD = "AkG1u";

// Listen for auth requests
chrome.webRequest.onAuthRequired.addListener(
    function(details, callbackFn) {
        console.log('[PROXY-AUTH] Authentication required for:', details.url);
        
        // Return credentials
        callbackFn({
            authCredentials: {
                username: PROXY_USERNAME,
                password: PROXY_PASSWORD
            }
        });
    },
    { urls: ["<all_urls>"] },
    ['asyncBlocking']
);

console.log('[PROXY-AUTH] Extension loaded. Username:', PROXY_USERNAME);
