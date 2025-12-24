/**
 * Get TikTok verification code from Hotmail via OAuth2 API
 * @author Your Name
 * @version 1.0.0
 */

const axios = require('axios');

/**
 * Fetch TikTok verification code from Hotmail
 * @param {string} email - Hotmail email address
 * @param {string} refreshToken - OAuth2 refresh token
 * @param {string} clientId - OAuth2 client ID
 * @param {number} maxRetries - Maximum retry attempts (default: 15)
 * @param {number} retryDelay - Delay between retries in ms (default: 5000)
 * @returns {Promise<string|null>} - TikTok code or null if failed
 */
async function getTikTokCode(email, refreshToken, clientId, maxRetries = 15, retryDelay = 5000) {
    const API_URL = 'https://tools.dongvanfb.net/api/get_code_oauth2';
    
    console.log(`[HOTMAIL] Fetching TikTok code for ${email}...`);
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`[HOTMAIL] Attempt ${attempt}/${maxRetries}...`);
            
            const response = await axios.post(API_URL, {
                email: email,
                refresh_token: refreshToken,
                client_id: clientId,
                type: 'tiktok'
            }, {
                headers: {
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout: 10000
            });
            
            const data = response.data;
            
            if (data.status && data.code) {
                console.log(`[HOTMAIL] ✅ Got code: ${data.code}`);
                console.log(`[HOTMAIL] Content: ${data.content}`);
                console.log(`[HOTMAIL] Date: ${data.date}`);
                return data.code;
            } else {
                console.log(`[HOTMAIL] No code yet (status: ${data.status})`);
            }
            
        } catch (error) {
            if (error.code === 'ECONNABORTED') {
                console.log(`[HOTMAIL] Request timeout`);
            } else if (error.response) {
                console.log(`[HOTMAIL] API error: ${error.response.status}`);
            } else {
                console.log(`[HOTMAIL] Error: ${error.message}`);
            }
        }
        
        // Wait before retry
        if (attempt < maxRetries) {
            console.log(`[HOTMAIL] Waiting ${retryDelay/1000}s before retry...`);
            await sleep(retryDelay);
        }
    }
    
    console.log(`[HOTMAIL] ❌ Failed to get code after ${maxRetries} attempts`);
    return null;
}

/**
 * Sleep helper function
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Parse account string format: tiktok_user|tiktok_pass|email|email_pass|refresh_token|client_id
 * @param {string} accountString - Account string with | separator
 * @returns {Object|null} - Parsed account data or null
 */
function parseHotmailAccount(accountString) {
    const parts = accountString.trim().split('|');
    
    if (parts.length < 6) {
        console.error(`[PARSE] Invalid format: need 6 parts, got ${parts.length}`);
        return null;
    }
    
    const email = parts[2].trim();
    
    if (!email.includes('@hotmail.com') && !email.includes('@outlook.com')) {
        console.error(`[PARSE] Not a Hotmail/Outlook email: ${email}`);
        return null;
    }
    
    return {
        tiktokUsername: parts[0].trim(),
        tiktokPassword: parts[1].trim(),
        email: email,
        emailPassword: parts[3].trim(),
        refreshToken: parts[4].trim(),
        clientId: parts[5].trim()
    };
}

// ============================================================
// EXAMPLE USAGE
// ============================================================

async function main() {
    // Example 1: Direct usage
    console.log('='.repeat(60));
    console.log('EXAMPLE 1: Direct usage');
    console.log('='.repeat(60));
    
    const code = await getTikTokCode(
        'dsfsd45t4dfg@hotmail.com',
        'M.C518_BAY.0.U.-CtLyFkvpx3K*0NhzBPs4WM*pnGJXJkiN6BRN90zWaaX0CsGNQifKlyVRku8uzJNqdEFTzvhhF7coNzQ1y8eWM6bAu9i4jGIWQojThUG9mRt5iOKtrNUYIpVIpzbNJmxg0ScX10OvSUpISzGHuiF6g7NPu1g7PJZKQYlraipFnfp7bbHNLN9CwhlsoN5FOWZsK!Otm5lIj6fETNXzFVKQvbaVKPJon1E1Qx*M4f3XFs8uIl*Ym*S41F9ivu3htQzEpxpsFT1vImq1mew*GeNPQj!fEkFE32GbyapC5b0YW07u2vbyXuqAttNDEaIv8O6ULdyBdeKUCjEh2AeYj32qp9k8TWBpYfCFlAbBhceLmumKYsYNIsUzlYaopWcE5ZIowDeVNYVFrbnFs5VH1keKWmDISe88bFfRzUW8OEhVW*f9!QMqOn8shv1YtWb3uquRJg$$',
        '5464fghj-bnmm-jh56-56fh-454345sdff',
        3,  // Only 3 retries for demo
        3000  // 3 seconds between retries
    );
    
    if (code) {
        console.log(`\n✅ SUCCESS! TikTok code: ${code}`);
    } else {
        console.log(`\n❌ FAILED to get code`);
    }
    
    // Example 2: Parse account string
    console.log('\n' + '='.repeat(60));
    console.log('EXAMPLE 2: Parse account string');
    console.log('='.repeat(60));
    
    const accountString = 'user6761816839023|hoang33@|vongminhtriqeagzrpxaeatxk@hotmail.com|apmgRmWXUW8496|M.C515_BAY.0.U.-Cu*bGvMnUTto03WpHe19M6ENJAijzQqzwfwveAQcZ*r9EgS6dmtWZb!eOIrdwD0p4qbr!YKuOV4uLPcrb23nH2w3tuZfGC18KFpNvDnS!XMRsdKekZxqoOoZwaWfF2qYB!4cKJM3gIvz7WolhDRGfYZDu3IPz*T*KjAMTaTsupn2vMOjxzgtTHqJ0fN4OG2XitZUiAjO1ZrrbBllZJRql9ms3a7SkhsR1hbxTc*jottZZUgfsTreLfvS7w!KY67ZM0ioVrHL!TJVvfsmMY4IDlzkye7ers35S3*l0VDXWnecF7gHY*rr2CZuUXtGnjVONEOr0vJMFmLm!njEwaSPjV6p3xmNSUkz1we4FX7QnIYxU5gUDXAmcedeqAcuFpUPhw$$|9e5f94bc-e8a4-4e73-b8be-63364c29d753';
    
    const account = parseHotmailAccount(accountString);
    
    if (account) {
        console.log('\n✅ Parsed account:');
        console.log(`  TikTok Username: ${account.tiktokUsername}`);
        console.log(`  Email: ${account.email}`);
        console.log(`  Client ID: ${account.clientId}`);
        
        // Fetch code for this account
        console.log('\nFetching code for parsed account...');
        const code2 = await getTikTokCode(
            account.email,
            account.refreshToken,
            account.clientId,
            3,
            3000
        );
        
        if (code2) {
            console.log(`\n✅ SUCCESS! TikTok code: ${code2}`);
        } else {
            console.log(`\n❌ FAILED to get code`);
        }
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

// Export for use as module
module.exports = {
    getTikTokCode,
    parseHotmailAccount,
    sleep
};
