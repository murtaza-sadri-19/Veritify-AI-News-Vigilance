# Score Always 0 - Diagnostic Guide

## 🐛 Issue: Score Always Returns 0

If your fact-checking service is always returning a score of 0, here are the most common causes and fixes:

---

## 🔍 Root Causes (Ordered by Likelihood)

### 1. ⚠️ **Boolean Query Too Complex for API** (MOST LIKELY)
**Symptom:** API returns 200 but no articles

**Cause:** The Boolean query format with `AND`, `OR`, `topic:`, etc. doesn't work with most simple news APIs.

**Fix Applied:**
```bash
# Boolean query is NOW DISABLED by default
# The system now uses simple queries that work with RapidAPI
```

**What changed:**
- `USE_BOOLEAN_QUERY` now defaults to `false` (was `true`)
- Simple query is used by default: `india asia win sports cricket`
- Boolean query only for advanced APIs: `("India" AND "win" OR "victory")`

**To verify:**
```
Look in logs for:
🔎 SIMPLE QUERY: 'india asia win sports cricket'

NOT:
🔎 BOOLEAN QUERY: '("India" AND ...)'
```

---

### 2. ❌ **No Articles Returned from API**
**Symptom:** Log shows `📰 FETCHED 0 articles`

**Possible reasons:**
- API key invalid/expired
- Query too specific (no matches)
- Date range too narrow
- Geographic restriction (country filter)

**How to diagnose:**
Check logs for:
```
❌ API returned status 401  # Invalid API key
❌ API returned status 429  # Rate limit exceeded
⚠️ API returned 200 but NO ARTICLES  # Query issue
```

**Fixes:**
1. **Check API Key:**
   ```bash
   # Verify NEWS_API_KEY is set correctly
   echo $NEWS_API_KEY  # Linux/Mac
   $env:NEWS_API_KEY   # Windows PowerShell
   ```

2. **Widen Date Range:**
   ```bash
   # Increase from 7 to 30 days
   NEWS_API_DAYS_BACK=30
   ```

3. **Remove Geographic Filter:**
   ```bash
   # Try without country restriction
   NEWS_API_COUNTRY=""
   ```

---

### 3. 🎯 **All Articles Below Relevance Threshold**
**Symptom:** API returns articles but score is still 0

**Cause:** All articles have relevance < 0.25 (default threshold)

**How to diagnose:**
Check logs for:
```
📰 FETCHED 50 articles
📊 FILTERING: 50 raw → 0 relevant
⚠️ NO RELEVANT ARTICLES FOUND! All 50 articles below threshold 0.25
```

**Fix:**
```bash
# Lower the threshold from 0.25 to 0.15
NEWS_RELEVANCE_THRESHOLD=0.15
```

**Why this happens:**
- Query terms don't match article content well
- Semantic similarity is low
- Need better query construction

---

### 4. 🔑 **No API Key Configured**
**Symptom:** Returns mock response

**How to diagnose:**
Check logs for:
```
⚠️ RAPIDAPI_KEY not configured - service will return mock responses
No API key configured, returning mock response
```

**Fix:**
```bash
# Set your RapidAPI key
export NEWS_API_KEY="your_actual_rapidapi_key_here"  # Linux/Mac
$env:NEWS_API_KEY="your_actual_rapidapi_key_here"    # Windows
```

---

### 5. 🌐 **API Endpoint Issue**
**Symptom:** Network errors or timeouts

**How to diagnose:**
Check logs for:
```
Network error querying news API: Connection timeout
Error querying news API: HTTPSConnectionPool
```

**Fix:**
```bash
# Increase timeout
NEWS_API_TIMEOUT=10.0  # Default is 5.0 seconds

# Try different API host
NEWS_API_HOST="real-time-news-data.p.rapidapi.com"
```

---

## 🔧 Step-by-Step Diagnosis

### Step 1: Check Logs
Restart Flask and look for these key log lines:

```bash
flask run
```

**✅ Good signs:**
```
📰 FETCHED 50 articles
📊 FILTERING: 50 raw → 25 relevant
📊 CREDIBILITY: Base=45, Count=15, Diversity=12, Consistency=7 → 79%
✅ FINAL RESULT: Score = 79%, Sources = 5
```

**❌ Bad signs:**
```
❌ API returned status 401
⚠️ API returned 200 but NO ARTICLES
⚠️ NO RELEVANT ARTICLES FOUND! All 50 articles below threshold 0.25
📊 FILTERING: 50 raw → 0 relevant
```

---

### Step 2: Test with Simple Claim
Try a claim that should definitely have results:

```
Claim: "India"
```

This should return many results. If it returns 0, the issue is API-related.

---

### Step 3: Check Environment Variables
```bash
# Required
echo $NEWS_API_KEY          # Must be valid RapidAPI key

# Optional (check if set incorrectly)
echo $NEWS_RELEVANCE_THRESHOLD  # Should be 0.15-0.30
echo $NEWS_API_DAYS_BACK       # Should be 7-30
echo $USE_BOOLEAN_QUERY        # Should be 'false' or unset
```

---

### Step 4: Enable Debug Logging
Add to your Flask logs to see raw API response:

In `fact_check_service.py`, temporarily add:
```python
logger.info(f"📦 Raw API response sample: {str(response_data)[:500]}")
```

---

## 🚀 Quick Fixes

### Fix 1: Use Simple Query (APPLIED)
```bash
# This is now the default - no action needed!
USE_BOOLEAN_QUERY=false
```

### Fix 2: Lower Threshold
```bash
NEWS_RELEVANCE_THRESHOLD=0.15
```

### Fix 3: Widen Date Range
```bash
NEWS_API_DAYS_BACK=30
```

### Fix 4: Remove Filters
```bash
NEWS_API_COUNTRY=""
NEWS_SOURCE_WHITELIST=""
NEWS_SOURCE_BLACKLIST=""
```

### Fix 5: Check API Key
```bash
# Test your API key manually
curl -H "x-rapidapi-key: YOUR_KEY" \
     -H "x-rapidapi-host: real-time-news-data.p.rapidapi.com" \
     "https://real-time-news-data.p.rapidapi.com/search?query=india&limit=10"
```

---

## 📊 Expected Log Output (Healthy)

```
🔍 STARTING NEWS SEARCH for claim: 'India win Asia cup 2025'
🔤 EXTRACTED KEYWORDS: ['india', 'win', 'asia', 'cup']
🎯 EXTRACTED ENTITIES: []
📂 EXTRACTED TOPIC CONTEXT: ['sports', 'cricket']
📍 EXTRACTED LOCATION CONTEXT: India
🔎 SIMPLE QUERY: 'india win asia cup sports cricket India'
📅 DATE RANGE: 2025-09-30 to 2025-10-07
🌐 API ENDPOINT: https://real-time-news-data.p.rapidapi.com/search?query=...
📰 FETCHED 50 articles
📊 FILTERING: 50 raw → 25 relevant (analyzed: 25)
📄 COMBINING RESULTS
📰 NEWS: 25 relevant from 50 total
📊 Avg relevance: 0.508 | Top-5 avg: 0.602 | Count: 25 | Unique sources: 18
📊 CREDIBILITY: Base=45, Count=15, Diversity=12, Consistency=7 → 79%
🎯 NEWS ONLY: 79%
✅ FINAL RESULT: Score = 79%, Sources = 5
⏱️ Total processing time: 8.42s
```

---

## 📞 Still Getting 0?

If score is still 0 after trying these fixes:

1. **Share your logs** - Copy the output from Flask terminal
2. **Check API status** - Visit RapidAPI dashboard to verify:
   - API key is valid
   - You have remaining quota
   - No service outages

3. **Test with cURL** - Manually test the API:
   ```bash
   curl -X GET "https://real-time-news-data.p.rapidapi.com/search?query=india&limit=5" \
        -H "x-rapidapi-key: YOUR_KEY_HERE" \
        -H "x-rapidapi-host: real-time-news-data.p.rapidapi.com"
   ```

4. **Check response format** - The API might have changed its response structure. Look for:
   ```
   ⚠️ API returned 200 but NO ARTICLES. Response keys: ['status', 'message', 'results']
   ```

---

## ✅ Summary of Fixes Applied

| Issue | Fix | Status |
|-------|-----|--------|
| Boolean query too complex | Disabled by default | ✅ Fixed |
| No error details on API failure | Added error response logging | ✅ Fixed |
| No warning when articles filtered | Added threshold warning | ✅ Fixed |
| No empty response detection | Added empty article warning | ✅ Fixed |

**Restart Flask** to apply these fixes:
```bash
# Stop: Ctrl+C
flask run
```

Then test with: "India win Asia cup 2025"
