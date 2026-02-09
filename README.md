# 🚀 Quick Start Guide - FNOL Claims Processor

## 1️⃣ Fastest Way to Start (No Installation)

```bash
# Just run it!
python enhanced_claims_agent.py
```

No dependencies needed for basic text processing!

## 2️⃣ Web Interface (Recommended)

### Install Dependencies
```bash
pip install streamlit pandas PyPDF2
```

### Launch Web App
```bash
streamlit run streamlit_app.py
```

Then open: **http://localhost:8501**

## 3️⃣ Process Your First Claim

### Option A: Using Web Interface

1. Open the web app
2. Paste FNOL text in the text area
3. Click "Process Claim"
4. View results!

### Option B: Using Python

```python
from enhanced_claims_agent import EnhancedClaimsProcessor

# Your FNOL text
claim = """
POLICY NUMBER: AUTO-2024-123
NAME OF INSURED: John Smith
DATE OF LOSS: 02/15/2024
CITY, STATE, ZIP: Los Angeles, CA 90001
DESCRIPTION OF ACCIDENT: Minor fender bender
ESTIMATE AMOUNT: $3,000
"""

# Process it
processor = EnhancedClaimsProcessor()
result = processor.process_claim(text_content=claim)

# Check routing
print(f"Route: {result['recommendedRoute']}")
print(f"Reason: {result['reasoning']}")
```

## 4️⃣ Run Tests

```bash
python test_enhanced_processor.py
```

Expected output:
- ✅ 7/7 tests pass
- ✅ All routing rules validated
- ✅ State warnings applied

## 5️⃣ Common Use Cases

### Case 1: Fast Track (< $25k, no issues)

```
Input: Minor damage, all fields present, no injuries
Output: "Fast Track" - 24 hour SLA
```

### Case 2: Manual Review (missing fields)

```
Input: Missing policy number or other required fields
Output: "Manual Review" - Human verification needed
```

### Case 3: Investigation (fraud detected)

```
Input: Description contains "staged", "inconsistent", etc.
Output: "Investigation Queue" - SIU review required
```

### Case 4: Specialist (bodily injury)

```
Input: Description mentions injuries, hospital, etc.
Output: "Specialist Queue - Bodily Injury"
```

### Case 5: Standard Review (high damage)

```
Input: Damage ≥ $25,000, no other issues
Output: "Standard Review Queue"
```

## 6️⃣ Key Features

✨ **25+ Fields Extracted** - Complete ACORD form coverage
🎯 **5 Routing Destinations** - Priority-based logic
⚖️ **52 Jurisdictions** - All US states + DC + PR
🔍 **10+ Fraud Keywords** - Advanced detection
🏥 **12+ Injury Keywords** - Accurate classification
💾 **JSON Export** - Standard format output

## 7️⃣ Troubleshooting

**Q: PDF not working?**
```bash
pip install PyPDF2
```

**Q: Web interface not loading?**
```bash
pip install streamlit pandas
streamlit run streamlit_app.py
```

**Q: Getting "missing fields" errors?**

Ensure your FNOL includes:
- Policy Number
- Policyholder Name
- Incident Date
- Incident Location
- Incident Description
- Estimated Damage

## 8️⃣ Example FNOL

Here's a complete example you can test:

```
AUTOMOBILE LOSS NOTICE

POLICY NUMBER: AUTO-TX-2024-456789
NAME OF INSURED: Robert Anderson
DATE OF LOSS AND TIME: 02/08/2024 3:30 PM

LOCATION OF LOSS
STREET: Interstate 35 North
CITY, STATE, ZIP: Austin, TX 78701
COUNTRY: USA

DESCRIPTION OF ACCIDENT: 
Vehicle rear-ended at traffic light. Minor bumper damage. 
No injuries. Other driver cited for following too closely.

INSURED VEHICLE
YEAR: 2023
MAKE: Honda
MODEL: Accord
V.I.N.: 1HGCY1F53NA123456

DRIVER'S LICENSE NUMBER: TX98765432
POLICE REPORT NUMBER: APD-2024-0208

ESTIMATE AMOUNT: $4,500
```

Expected Result:
- Route: **Fast Track**
- Reason: Damage ($4,500) below threshold, all fields present, no issues

## 9️⃣ Next Steps

1. ✅ Read **README_ENHANCED.md** for full documentation
2. ✅ Check **API_DOCUMENTATION.md** for integration details
3. ✅ Review **test_enhanced_processor.py** for examples
4. ✅ Try the **Streamlit app** for interactive processing

## 🎯 Quick Reference

### Routing Priority (Highest to Lowest)

1. Missing fields → Manual Review
2. Fraud keywords → Investigation
3. Bodily injury → Specialist
4. < $25k damage → Fast Track
5. ≥ $25k damage → Standard Review

### Fraud Keywords

fraud, fraudulent, inconsistent, staged, suspicious, fabricated, collusion, false, questionable, discrepancy

### Injury Keywords

injury, hurt, hospitalized, medical, ambulance, paramedic, whiplash, fracture, pain, emergency

### Mandatory Fields

policy_number, policyholder_name, incident_date, incident_location, incident_description, claim_type, estimated_damage

---

**Need Help?**
- Check README_ENHANCED.md
- Review test examples
- Examine sample claims

**Ready to deploy?**
- See integration guide in README
- Review API documentation
- Test with your FNOL documents

🎉 **Happy Processing!**
