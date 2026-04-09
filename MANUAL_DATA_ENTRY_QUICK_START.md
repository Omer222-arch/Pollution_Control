# Manual Data Entry Dashboard - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Login
1. Open the application
2. Enter your email and password
3. Click "Login"

### Step 2: Navigate to Manual Entry
1. Click "🚗 Manual Entry" button on home page
2. Or go to Home → 🚗 Manual Entry

### Step 3: Enter Vehicle Data

**Enter the number of vehicles for your time slot:**

```
🚗 Cars:        100 (or your value)
🏍️ Bikes:       50  (or your value)
🚚 Trucks:      20  (or your value)
🚌 Buses:       10  (or your value)
```

### Step 4: Select Time Slot

```
📅 Date:        Today (default)
🕐 Hour:        12:00 (noon, default)
⏱️  Duration:    60 minutes (default)
```

### Step 5: Set Fuel Mix (Optional)

```
⛽ Petrol:      60% (default)
⛽ Diesel:      30% (default)
⛽ Electric:    10% (default)
```

### Step 6: Generate Predictions

Click the **"🔮 Get Predictions"** button

### Step 7: View Results

You'll see:
- 📊 Pollution levels for each pollutant
- 📈 Interactive charts
- ⏰ 24-hour predictions
- ⚕️ Health recommendations
- 💡 Key insights

## 📊 Understanding Your Results

### Quick Look at Metrics

| Metric | What It Means | Normal Range |
|--------|---------------|--------------|
| **PM2.5** | Fine particles | 0-15 μg/m³ (Good) |
| **PM10** | Coarse particles | 0-45 μg/m³ (Good) |
| **NO2** | Nitrogen dioxide | 0-40 μg/m³ (Good) |
| **CO** | Carbon monoxide | 0-10000 μg/m³ (Good) |

### Green = Good ✅
All pollutants below WHO guidelines

### Yellow = Moderate ⚠️
Some pollutants elevated, sensitive groups at risk

### Red = Unhealthy ⛔
Multiple pollutants above guidelines, action needed

## 🎯 Common Scenarios

### Scenario 1: Morning Commute (8 AM)
```
Vehicles:  Cars 400, Bikes 200, Trucks 30, Buses 20
Hour:      08:00 (Rush hour)
Fuel:      60% Petrol, 30% Diesel, 10% Electric

Expected Result: ⚠️ Moderate pollution, peak hours
```

### Scenario 2: Midnight Traffic (2 AM)
```
Vehicles:  Cars 50, Bikes 20, Trucks 15, Buses 2
Hour:      02:00 (Night hours)
Fuel:      60% Petrol, 30% Diesel, 10% Electric

Expected Result: ✅ Good air quality
```

### Scenario 3: Clear Air Day (Off-Peak)
```
Vehicles:  Cars 100, Bikes 30, Trucks 10, Buses 5
Hour:      14:00 (Off-peak)
Fuel:      60% Petrol, 30% Diesel, 50% Electric

Expected Result: ✅ Good air quality
```

### Scenario 4: Heavy Traffic (5 PM Rush)
```
Vehicles:  Cars 600, Bikes 300, Trucks 50, Buses 30
Hour:      17:00 (Evening rush)
Fuel:      60% Petrol, 30% Diesel, 10% Electric

Expected Result: 🚨 Very unhealthy pollution levels
```

## 💾 Saving Your Results

### Download CSV (Users)
- Click "📥 Download History as CSV"
- Opens file with all predictions
- Uses: Excel, spreadsheet apps, analysis tools

### Export Full Data (Admin)
- Click "📊 Export Full Data (CSV)"
- Includes all user predictions
- For analysis and reporting

## ❓ FAQ

### Q: How accurate are these predictions?
**A:** The predictions are based on scientific emission factors and traffic patterns. Actual pollution can vary based on weather, wind, and atmospheric conditions.

### Q: What if vehicles are 100% electric?
**A:** EV percentage is factored in automatically. In the example above with 50% electric, emissions reduce by ~35%.

### Q: Can I use historical data?
**A:** Yes! Use the date picker to select past dates. This helps you estimate what pollution might have been.

### Q: Do I need special permissions?
**A:** No! Any registered user can access this feature. Admins have additional export options.

### Q: How is rush hour determined?
**A:** Automatically from the hour you select:
- **Morning Rush**: 7-10 AM (+50% multiplier)
- **Evening Rush**: 5-8 PM (+50% multiplier)
- **Night**: 10 PM-5 AM (-60% multiplier)

### Q: Can I compare different scenarios?
**A:** Yes! Keep entering different values and comparing results. Your history shows all entries for side-by-side comparison.

## ⚙️ Tips & Tricks

### Tip 1: Use Realistic Numbers
Research typical traffic volumes in your area for accurate predictions.

### Tip 2: Try Different Fuel Mixes
Compare 0% vs 50% vs 100% electric vehicles to see impact.

### Tip 3: Check Peak Hours
Enter 8:00, 12:00, 17:00, 22:00 to see variation throughout day.

### Tip 4: Export and Analyze
Download CSV data and create your own charts in Excel/Google Sheets.

### Tip 5: Share Results
Screenshot charts or download CSV to share with team/community.

## 🔧 Troubleshooting

### Nothing Happens After Clicking Predict
- ✅ Check you entered vehicle counts
- ✅ Click button in center of screen (not sidebar)
- ✅ Wait a few seconds for calculation
- ✅ Refresh page if still stuck

### Predictions Seem Too Low/High
- ✅ Review WHO guidelines (column shows comparison)
- ✅ Check fuel mix - more electric = lower
- ✅ Verify hour (night = lower, rush = higher)
- ✅ Compare with WHO guidelines table

### Can't Download Data
- ✅ Make sure you're logged in
- ✅ Try different browser
- ✅ Check browser download settings
- ✅ Try admin role for full export

### Charts Not Showing
- ✅ Enter non-zero vehicle counts
- ✅ Refresh page
- ✅ Try different browser
- ✅ Check internet connection

## 📞 Need Help?

- **In-app**: See ℹ️ info boxes on dashboard
- **Full Docs**: See MANUAL_DATA_ENTRY_GUIDE.md
- **Admin**: Contact system administrator

## 🎓 Learn More

### Emission Factors
Different vehicle types produce different amounts of emissions:
- **Bikes**: Lowest emissions (small engines)
- **Cars**: Medium emissions (efficient engines)
- **Buses**: Higher emissions (larger engines, more capacity)
- **Trucks**: Highest emissions (heavy diesel engines)

### Air Quality Standards
WHO sets daily guidelines for air quality. If your predictions exceed these, pollution is unhealthy.

### Temporal Patterns
Traffic varies throughout the day:
- **Rush hours**: 7-10 AM, 5-8 PM (50% more traffic)
- **Midday**: 10 AM-5 PM (normal traffic)
- **Night**: 10 PM-5 AM (60% less traffic)

### Fuel Mix Impact
Different fuels have different emissions:
- **Electric**: -70% emissions compared to petrol
- **Diesel**: +20% emissions compared to petrol
- **Petrol**: Baseline (100%)

---

## 🚀 You're Ready!

Now go to the Manual Data Entry page and start predicting!

**Happy predicting! 🌍**

---

**Last Updated**: 2026-04-07
