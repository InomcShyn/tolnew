# ⚡ Quick Start - Launch Livestream TikTok

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```bash
pip install playwright psutil
playwright install chromium
```

### Step 2: Configure (Optional)

Edit `config.ini`:
```ini
[CAPTCHA]
omocaptcha_api_key = YOUR_API_KEY_HERE
```

### Step 3: Launch!

```bash
python launch_livestream_tiktok.py
```

---

## 📋 Menu Options

```
1. Launch profiles (HEADLESS + Mobile - RAM optimized)  ← Recommended
2. Launch profiles (VISIBLE + Mobile)                   ← For testing
3. Launch profiles (HEADLESS + Desktop)
4. Kill all Chrome processes
5. View RAM statistics
6. Exit
```

---

## 🎯 First Launch Example

```
Choice: 1
Count: 10
URL: https://www.tiktok.com/@username/live
Delay: 2.0
Continue? yes
```

**Result:**
- 10 profiles launched
- ~1.8GB RAM total (~180MB per profile)
- Real-time monitoring active
- Logs saved to `ram_logs/`

---

## 📊 Check Results

### View RAM Report

```
Choice: 5
```

**Output:** `system_monitor/RAM_REPORT.md`

**Shows:**
- Average RAM per profile
- Scaling predictions
- GPU health
- Memory leak detection

---

## 🎓 Learn More

- **Complete Guide:** `LAUNCH_LIVESTREAM_TIKTOK_GUIDE.md`
- **Monitor Docs:** `system_monitor/README.md`
- **Upgrade Info:** `UPGRADE_COMPLETE.md`

---

## 🆘 Troubleshooting

### High RAM (> 220MB per profile)

```bash
# Check Chrome flags
# Ensure headless mode enabled
# Use mobile viewport
```

### SwiftShader Detected

```bash
# Install GPU drivers
# Check GPU flags in Chrome
```

### Captcha Not Solving

```bash
# Add API key to config.ini
# Check OMOcaptcha balance
```

---

## ✅ Success Checklist

- [ ] Profiles launch successfully
- [ ] RAM ~150-220MB per profile
- [ ] GPU: Real GPU (not SwiftShader)
- [ ] Stealth: Active (100%)
- [ ] Views counted on TikTok

---

**Ready to scale?** Start with 10 → 50 → 100 → 300 profiles!

**Questions?** Read `LAUNCH_LIVESTREAM_TIKTOK_GUIDE.md`
