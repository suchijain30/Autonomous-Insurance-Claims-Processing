"""
Streamlit Frontend for Autonomous Insurance Claims Processing
Interactive web interface for processing FNOL documents
"""

import streamlit as st
import json
from enhanced_claims_agent import EnhancedClaimsProcessor
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="FNOL Claims Processor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2ca02c;
        margin-top: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    .danger-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def display_route_badge(route: str):
    """Display routing decision with color-coded badge"""
    if "Fast Track" in route:
        st.success(f"✅ **{route}**")
    elif "Manual Review" in route:
        st.warning(f"⚠️ **{route}**")
    elif "Investigation" in route:
        st.error(f"🚨 **{route}**")
    elif "Specialist" in route:
        st.info(f"🏥 **{route}**")
    else:
        st.info(f"📊 **{route}**")


def display_field_table(fields: dict):
    """Display extracted fields in a nice table"""
    if not fields:
        st.info("No fields extracted")
        return
    
    # Convert to DataFrame for better display
    data = []
    for key, value in fields.items():
        # Format field names nicely
        field_name = key.replace('_', ' ').title()
        field_value = value
        
        # Format currency values
        if 'damage' in key.lower() or 'estimate' in key.lower():
            if isinstance(value, (int, float)):
                field_value = f"${value:,.2f}"
        
        data.append({"Field": field_name, "Value": field_value})
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def main():
    # Header
    st.markdown('<div class="main-header">🏥 Autonomous Insurance Claims Processor</div>', unsafe_allow_html=True)
    st.markdown("### Process ACORD Automobile Loss Notice Forms (ACORD 2)")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Processing options
        st.subheader("Processing Options")
        fast_track_threshold = st.number_input(
            "Fast Track Threshold ($)",
            min_value=1000,
            max_value=100000,
            value=25000,
            step=1000,
            help="Claims below this amount will be fast-tracked"
        )
        
        st.subheader("📊 Statistics")
        if 'processed_count' not in st.session_state:
            st.session_state.processed_count = 0
        
        st.metric("Claims Processed", st.session_state.processed_count)
        
        st.subheader("📖 About")
        st.info("""
        This tool extracts and routes First Notice of Loss (FNOL) claims:
        
        **Routing Rules:**
        1. Missing fields → Manual Review
        2. Fraud keywords → Investigation
        3. Bodily injury → Specialist Queue
        4. < $25k → Fast Track
        5. ≥ $25k → Standard Review
        """)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📝 Process Claim", "📊 Sample Claims", "ℹ️ Help"])
    
    with tab1:
        st.header("Upload or Paste FNOL Document")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Paste Text", "Upload File"],
            horizontal=True
        )
        
        claim_text = None
        
        if input_method == "Paste Text":
            claim_text = st.text_area(
                "Paste FNOL document content here:",
                height=300,
                placeholder="""Example:
POLICY NUMBER: AUTO-2024-123456
NAME OF INSURED: John Smith
DATE OF LOSS: 01/15/2024
LOCATION: 123 Main St, Los Angeles, CA 90001
DESCRIPTION OF ACCIDENT: Rear-ended at traffic light...
ESTIMATE AMOUNT: $5,000
...
"""
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload FNOL document (PDF or TXT)",
                type=['pdf', 'txt'],
                help="Upload ACORD form as PDF or text file"
            )
            
            if uploaded_file:
                if uploaded_file.type == "text/plain":
                    claim_text = uploaded_file.read().decode('utf-8')
                else:
                    # For PDF, save temporarily and process
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name
                    
                    try:
                        processor = EnhancedClaimsProcessor()
                        processor.FAST_TRACK_THRESHOLD = fast_track_threshold
                        claim_text = processor.extract_from_pdf(tmp_path)
                        st.success("✅ PDF extracted successfully!")
                    except Exception as e:
                        st.error(f"❌ Error processing PDF: {e}")
                        st.info("💡 Try installing PyPDF2: `pip install PyPDF2`")
        
        # Process button
        if st.button("🚀 Process Claim", type="primary", use_container_width=True):
            if not claim_text or claim_text.strip() == "":
                st.error("❌ Please provide claim text or upload a file")
            else:
                with st.spinner("Processing claim..."):
                    try:
                        # Initialize processor
                        processor = EnhancedClaimsProcessor()
                        processor.FAST_TRACK_THRESHOLD = fast_track_threshold
                        
                        # Process the claim
                        result = processor.process_claim(text_content=claim_text)
                        
                        # Update session state
                        st.session_state.processed_count += 1
                        st.session_state.last_result = result
                        
                        # Success message
                        st.success("✅ Claim processed successfully!")
                        
                        # Display results
                        st.markdown("---")
                        
                        # Routing Decision (Most Important)
                        st.markdown("## 🎯 Routing Decision")
                        display_route_badge(result['recommendedRoute'])
                        
                        st.markdown(f"**Reasoning:** {result['reasoning']}")
                        
                        # Key Indicators
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            fraud = result['metadata']['fraudIndicators']
                            if fraud:
                                st.markdown('<div class="danger-box">🚨 <b>Fraud Indicators Detected</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="success-box">✅ <b>No Fraud Indicators</b></div>', unsafe_allow_html=True)
                        
                        with col2:
                            injury = result['metadata']['injuryClaim']
                            if injury:
                                st.markdown('<div class="warning-box">🏥 <b>Bodily Injury Claim</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="success-box">✅ <b>Property Damage Only</b></div>', unsafe_allow_html=True)
                        
                        with col3:
                            missing_count = len(result['missingFields'])
                            if missing_count > 0:
                                st.markdown(f'<div class="warning-box">⚠️ <b>{missing_count} Missing Fields</b></div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="success-box">✅ <b>All Fields Present</b></div>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        # Extracted Fields
                        st.markdown("## 📋 Extracted Fields")
                        display_field_table(result['extractedFields'])
                        
                        # Missing Fields
                        if result['missingFields']:
                            st.markdown("## ⚠️ Missing Mandatory Fields")
                            for field in result['missingFields']:
                                st.markdown(f"- **{field.replace('_', ' ').title()}**")
                        
                        # State Warning
                        if result['metadata'].get('stateWarning'):
                            st.markdown("## ⚖️ State-Specific Warning")
                            warning_info = result['metadata']['stateWarning']
                            st.warning(f"**{warning_info['state_name']} ({warning_info['state_code']})**")
                            with st.expander("View Full Warning"):
                                st.write(warning_info['warning'])
                        
                        # Fraud Keywords
                        if result['metadata']['fraudKeywordsFound']:
                            st.markdown("## 🚨 Fraud Keywords Detected")
                            st.error(f"Found keywords: {', '.join(result['metadata']['fraudKeywordsFound'])}")
                        
                        # JSON Export
                        st.markdown("---")
                        st.markdown("## 💾 Export Results")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Pretty JSON
                            json_str = json.dumps(result, indent=2)
                            st.download_button(
                                label="📥 Download JSON",
                                data=json_str,
                                file_name=f"claim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                        
                        with col2:
                            # Display JSON
                            if st.button("👁️ View Raw JSON"):
                                st.json(result)
                        
                    except Exception as e:
                        st.error(f"❌ Error processing claim: {str(e)}")
                        st.exception(e)
    
    with tab2:
        st.header("📊 Sample FNOL Documents")
        st.info("Click on any sample to load it into the processor")
        
        samples = {
            "1. Bodily Injury - High Damage ($45k)": """POLICY NUMBER: AUTO-2024-987654
NAME OF INSURED: Sarah Elizabeth Johnson
DATE OF LOSS AND TIME: 02/05/2024 10:15 AM
STREET: Interstate 35 Northbound
CITY, STATE, ZIP: Austin, TX 78701
COUNTRY: USA
DESCRIPTION OF ACCIDENT: Multi-vehicle collision during heavy rain. Driver and passenger transported to hospital with neck and back injuries. Significant damage.
YEAR: 2022
MAKE: Toyota
MODEL: Camry
V.I.N.: 4T1B11HK5NU123456
ESTIMATE AMOUNT: $45,000
POLICE REPORT NUMBER: APD-2024-0205-1234""",
            
            "2. Fast Track - Low Damage ($2.8k)": """POLICY NUMBER: AUTO-2024-555123
NAME OF INSURED: David Robert Williams
DATE OF LOSS: 01/28/2024
STREET: Parking lot of Desert Mall
CITY, STATE, ZIP: Phoenix, AZ 85001
DESCRIPTION OF ACCIDENT: Vehicle damaged while parked. Unknown party backed into driver's side door.
YEAR: 2023
MAKE: Honda
MODEL: Civic
V.I.N.: 2HGFC2F59NH123456
ESTIMATE AMOUNT: $2,800""",
            
            "3. Fraud Indicators": """POLICY NUMBER: AUTO-2024-777999
NAME OF INSURED: Jennifer Marie Lopez
DATE OF LOSS: 02/01/2024
CITY, STATE, ZIP: Miami, FL 33101
DESCRIPTION OF ACCIDENT: Details are inconsistent. Initially reported stolen but found with damage. Story keeps changing. Possible staged accident scenario.
YEAR: 2020
MAKE: BMW
MODEL: X5
V.I.N.: 5UXKR0C58L9B12345
ESTIMATE AMOUNT: $18,500""",
            
            "4. Missing Critical Fields": """NAME OF INSURED: Michael Anderson
DATE OF LOSS: 01/30/2024
DESCRIPTION OF ACCIDENT: Hit and run incident. Vehicle struck by unknown party.
MAKE: Subaru
MODEL: Outback""",
        }
        
        for name, content in samples.items():
            with st.expander(name):
                st.code(content, language="text")
                if st.button(f"Load {name}", key=f"load_{name}"):
                    st.session_state.sample_text = content
                    st.success(f"✅ Loaded! Switch to 'Process Claim' tab to process it.")
    
    with tab3:
        st.header("ℹ️ Help & Documentation")
        
        st.markdown("""
        ## 🎯 How to Use This Tool
        
        ### Step 1: Choose Input Method
        - **Paste Text**: Copy and paste ACORD form content
        - **Upload File**: Upload PDF or TXT file
        
        ### Step 2: Process the Claim
        Click the "Process Claim" button to analyze the document
        
        ### Step 3: Review Results
        The system will:
        1. Extract all relevant fields
        2. Identify missing mandatory fields
        3. Check for fraud indicators
        4. Determine claim type (injury/property)
        5. Route to appropriate queue
        
        ---
        
        ## 📋 Required Fields
        
        **Mandatory for complete processing:**
        - Policy Number
        - Policyholder Name
        - Incident Date
        - Incident Location
        - Incident Description
        - Claim Type
        - Estimated Damage
        
        ---
        
        ## 🚦 Routing Rules
        
        Claims are routed using **priority-based logic**:
        
        | Priority | Condition | Route |
        |----------|-----------|-------|
        | 1 | Missing mandatory fields | Manual Review |
        | 2 | Fraud keywords detected | Investigation Queue |
        | 3 | Bodily injury involved | Specialist Queue |
        | 4 | Damage < $25,000 | Fast Track |
        | 5 | Damage ≥ $25,000 | Standard Review |
        
        ---
        
        ## 🔍 Fraud Detection
        
        The system monitors for these keywords:
        - fraud, fraudulent
        - inconsistent, inconsistency
        - staged, stage
        - suspicious, suspect
        - fabricated, false
        - collusion, questionable
        
        ---
        
        ## 🏥 Injury Detection
        
        Keywords that trigger bodily injury classification:
        - injury, injured, hurt
        - hospitalized, medical
        - ambulance, paramedic
        - whiplash, fracture
        - pain, contusion
        
        ---
        
        ## ⚖️ State-Specific Compliance
        
        The system automatically applies fraud warnings for:
        - All 50 US States
        - District of Columbia
        - Puerto Rico
        
        Warnings are based on the incident location's state code.
        
        ---
        
        ## 💾 Export Options
        
        Results can be exported as JSON containing:
        - All extracted fields
        - Missing fields list
        - Routing recommendation
        - Detailed reasoning
        - Fraud/injury indicators
        - State warnings (if applicable)
        
        ---
        
        ## 🛠️ Troubleshooting
        
        **PDF upload not working?**
        - Install PyPDF2: `pip install PyPDF2`
        - Or paste the text content instead
        
        **Missing fields detected?**
        - Ensure all mandatory fields are present in the document
        - Check field formatting (dates, amounts, etc.)
        
        **Unexpected routing?**
        - Review the routing rules priority
        - Check for fraud keywords in description
        - Verify damage amount threshold
        """)


if __name__ == "__main__":
    # Check if sample was loaded
    if 'sample_text' in st.session_state:
        st.info("📝 Sample claim loaded! Switch to 'Process Claim' tab and paste the content to process it.")
    
    main()
