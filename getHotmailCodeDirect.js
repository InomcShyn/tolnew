/**
 * Get TikTok verification code directly from Microsoft Graph API
 * No third-party service required
 * @version 1.0.0
 */

const axios = require('axios');

/**
 * Microsoft Graph API endpoints
 */
const MS_GRAPH_API = {
    TOKEN: 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
    MESSAGES: 'https://graph.microsoft.com/v1.0/me/messages'
};

/**
 * Get access token from refresh token
 * @param {string} refreshToken - OAuth2 refresh token
 * @param {string} clientId - OAuth2 client ID
 * @returns {Promise<string|null>} - Access token or null
 */
async function getAccessToken(refreshToken, clientId) {
    try {
        const response = await axios.post(MS_GRAPH_API.TOKEN, new URLSearchParams({
            client_id: clientId,
            scope: 'https://graph.microsoft.com/Mail.Read offline_access',
            refresh_token: refreshToken,
            grant_type: 'refresh_token'
        }), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
        
        return response.data.access_token;
    } catch (error) {
        console.error(`[TOKEN] Error: ${error.response?.data?.error_description || error.message}`);
        return null;
    }
}

/**
 * Search for TikTok verification email
 * @param {string} accessToken - Microsoft Graph access token
 * @param {number} maxResults - Maximum number of emails to check
 * @returns {Promise<Object|null>} - Email object or null
 */
async function searchTikTokEmail(accessToken, maxResults = 10) {
    try {
        const response = await axios.get(MS_GRAPH_API.MESSAGES, {
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
            params: {
                '$top': maxResults,
                '$orderby': 'receivedDateTime DESC',
                '$select': 'subject,bodyPreview,body,receivedDateTime,from',
                '$filter': "contains(subject, 'TikTok') or contains(from/emailAddress/address, 'tiktok')"
            }
        });
        
        const messages = response.data.value;
        
        if (messages && messages.length > 0) {
            // Return most recent TikTok email
            return messages[0];
        }
        
        return null;
    } catch (error) {
        console.error(`[SEARCH] Error: ${error.response?.data?.error?.message || error.message}`);
        return null;
    }
}

/**
 * Extract 6-digit code from email content
 * @param {Object} email - Email object from Graph API
 * @returns {string|null} - 6-digit code or null
 */
function extractCode(email) {
    if (!email) return null;
    
    // Try to extract from body
    const bodyText = email.body?.content || email.bodyPreview || '';
    
    // Look for 6-digit code
    const codeMatch = bodyText.match(/\b(\d{6})\b/);
    
    if (codeMatch) {
        return codeMatch[1];
    }
    
    return null;
}

/**
 * Get TikTok verification code from Hotmail (Direct - No third party)
 * @param {string} refreshToken - OAuth2 refresh token
 * @param {string} clientId - OAuth2 client ID
 * @param {number} maxRetries - Maximum retry attempts
 * @param {number} retryDelay - Delay between retries in ms
 * @returns {Promise<string|null>} - TikTok code or null
 */
async function getTikTokCodeDirect(refreshToken, clientId, maxRetries = 15, retryDelay = 5000) {
    console.log(`[HOTMAIL-DIRECT] Fetching TikTok code via Microsoft Graph API...`);
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            console.log(`[HOTMAIL-DIRECT] Attempt ${attempt}/${maxRetries}...`);
            
            // Step 1: Get access token
            console.log(`[HOTMAIL-DIRECT] Getting access token...`);
            const accessToken = await getAccessToken(refreshToken, clientId);
            
            if (!accessToken) {
                console.log(`[HOTMAIL-DIRECT] Failed to get access token`);
                if (attempt < maxRetries) {
                    await sleep(retryDelay);
                    continue;
                }
                return null;
            }
            
            console.log(`[HOTMAIL-DIRECT] ✅ Got access token`);
            
            // Step 2: Search for TikTok email
            console.log(`[HOTMAIL-DIRECT] Searching for TikTok email...`);
            const email = await searchTikTokEmail(accessToken, 10);
            
            if (!email) {
                console.log(`[HOTMAIL-DIRECT] No TikTok email found yet`);
                if (attempt < maxRetries) {
                    console.log(`[HOTMAIL-DIRECT] Waiting ${retryDelay/1000}s before retry...`);
                    await sleep(retryDelay);
                    continue;
                }
                return null;
            }
            
            console.log(`[HOTMAIL-DIRECT] ✅ Found TikTok email`);
            console.log(`[HOTMAIL-DIRECT] Subject: ${email.subject}`);
            console.log(`[HOTMAIL-DIRECT] From: ${email.from?.emailAddress?.address}`);
            console.log(`[HOTMAIL-DIRECT] Date: ${email.receivedDateTime}`);
            
            // Step 3: Extract code
            const code = extractCode(email);
            
            if (code) {
                console.log(`[HOTMAIL-DIRECT] ✅ Extracted code: ${code}`);
                return code;
            } else {
                console.log(`[HOTMAIL-DIRECT] Could not extract code from email`);
                if (attempt < maxRetries) {
                    await sleep(retryDelay);
                    continue;
                }
            }
            
        } catch (error) {
            console.error(`[HOTMAIL-DIRECT] Error: ${error.message}`);
            if (attempt < maxRetries) {
                await sleep(retryDelay);
            }
        }
    }
    
    console.log(`[HOTMAIL-DIRECT] ❌ Failed to get code after ${maxRetries} attempts`);
    return null;
}

/**
 * Sleep helper
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Parse account string
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
    console.log('='.repeat(60));
    console.log('DIRECT HOTMAIL CODE FETCHER (No Third Party)');
    console.log('Using Microsoft Graph API');
    console.log('='.repeat(60));
    
    // Example account string
    const accountString = 'user6761816839023|hoang33@|vongminhtriqeagzrpxaeatxk@hotmail.com|apmgRmWXUW8496|M.C515_BAY.0.U.-Cu*bGvMnUTto03WpHe19M6ENJAijzQqzwfwveAQcZ*r9EgS6dmtWZb!eOIrdwD0p4qbr!YKuOV4uLPcrb23nH2w3tuZfGC18KFpNvDnS!XMRsdKekZxqoOoZwaWfF2qYB!4cKJM3gIvz7WolhDRGfYZDu3IPz*T*KjAMTaTsupn2vMOjxzgtTHqJ0fN4OG2XitZUiAjO1ZrrbBllZJRql9ms3a7SkhsR1hbxTc*jottZZUgfsTreLfvS7w!KY67ZM0ioVrHL!TJVvfsmMY4IDlzkye7ers35S3*l0VDXWnecF7gHY*rr2CZuUXtGnjVONEOr0vJMFmLm!njEwaSPjV6p3xmNSUkz1we4FX7QnIYxU5gUDXAmcedeqAcuFpUPhw$$|9e5f94bc-e8a4-4e73-b8be-63364c29d753';
    
    const account = parseHotmailAccount(accountString);
    
    if (!account) {
        console.error('Failed to parse account');
        return;
    }
    
    console.log('\n✅ Parsed account:');
    console.log(`  Email: ${account.email}`);
    console.log(`  Client ID: ${account.clientId}`);
    
    console.log('\nFetching TikTok code...\n');
    
    const code = await getTikTokCodeDirect(
        account.refreshToken,
        account.clientId,
        3,    // Only 3 retries for demo
        3000  // 3 seconds delay
    );
    
    if (code) {
        console.log(`\n${'='.repeat(60)}`);
        console.log(`✅ SUCCESS! TikTok Code: ${code}`);
        console.log('='.repeat(60));
    } else {
        console.log(`\n${'='.repeat(60)}`);
        console.log('❌ FAILED to get code');
        console.log('='.repeat(60));
    }
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

// Export
module.exports = {
    getTikTokCodeDirect,
    getAccessToken,
    searchTikTokEmail,
    extractCode,
    parseHotmailAccount,
    sleep
};
