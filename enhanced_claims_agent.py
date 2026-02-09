"""
Enhanced Autonomous Insurance Claims Processing Agent
Extracts, validates, and routes FNOL documents with state-specific compliance
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ExtractedClaim:
    """Data class for extracted claim information"""
    # Policy Information
    policy_number: Optional[str] = None
    policyholder_name: Optional[str] = None
    effective_dates: Optional[str] = None
    
    # Incident Information
    incident_date: Optional[str] = None
    incident_time: Optional[str] = None
    incident_location: Optional[str] = None
    incident_description: Optional[str] = None
    
    # Involved Parties
    claimant_name: Optional[str] = None
    third_party_names: Optional[List[str]] = None
    claimant_contact: Optional[str] = None
    third_party_contacts: Optional[List[str]] = None
    
    # Asset Details
    asset_type: Optional[str] = None
    asset_id: Optional[str] = None
    estimated_damage: Optional[float] = None
    
    # Other Mandatory Fields
    claim_type: Optional[str] = None
    attachments: Optional[List[str]] = None
    initial_estimate: Optional[float] = None
    
    # Additional fields
    vin: Optional[str] = None
    vehicle_year: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    driver_name: Optional[str] = None
    driver_license: Optional[str] = None
    police_report_number: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {}
        for key, value in asdict(self).items():
            if value is not None:
                result[key] = value
        return result


class EnhancedClaimsProcessor:
    """Enhanced claims processing agent with state-specific compliance"""
    
    # Routing thresholds
    FAST_TRACK_THRESHOLD = 25000
    
    # Fraud detection keywords
    FRAUD_KEYWORDS = [
        'fraud', 'fraudulent',
        'inconsistent', 'inconsistency',
        'staged', 'stage',
        'suspicious', 'suspect',
        'fabricated', 'fabricate',
        'collusion', 'collude',
        'false', 'fake',
        'questionable',
        'discrepancy', 'discrepancies'
    ]
    
    # Injury keywords
    INJURY_KEYWORDS = [
        'injury', 'injured', 'injure',
        'hurt', 'pain',
        'hospitalized', 'hospital',
        'medical', 'medic',
        'bodily', 'body',
        'ambulance',
        'paramedic',
        'emergency room', 'er',
        'whiplash',
        'fracture', 'broken',
        'contusion', 'bruise'
    ]
    
    # Mandatory fields
    MANDATORY_FIELDS = [
        'policy_number',
        'policyholder_name',
        'incident_date',
        'incident_location',
        'incident_description',
        'claim_type',
        'estimated_damage'
    ]
    
    # State fraud warnings from ACORD form
    STATE_FRAUD_WARNINGS = {
        'AL': {
            'name': 'Alabama',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for payment of a loss or benefit or who knowingly presents false information in an application for insurance is guilty of a crime and may be subject to restitution, fines, or confinement in prison, or any combination thereof.'
        },
        'AK': {
            'name': 'Alaska',
            'warning': 'A person who knowingly and with intent to injure, defraud, or deceive an insurance company files a claim containing false, incomplete, or misleading information may be prosecuted under state law.'
        },
        'AZ': {
            'name': 'Arizona',
            'warning': 'For your protection Arizona law requires the following statement to appear on this form. Any person who knowingly presents a false or fraudulent claim for payment of a loss is subject to criminal and civil penalties.'
        },
        'AR': {
            'name': 'Arkansas',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for payment of a loss or benefit or knowingly presents false information in an application for insurance is guilty of a crime and may be subject to fines and confinement in prison.'
        },
        'CA': {
            'name': 'California',
            'warning': 'For your protection California law requires the following to appear on this form. Any person who knowingly presents false or fraudulent claim for the payment of a loss is guilty of a crime and may be subject to fines and confinement in state prison.'
        },
        'CO': {
            'name': 'Colorado',
            'warning': 'It is unlawful to knowingly provide false, incomplete, or misleading facts or information to an insurance company for the purpose of defrauding or attempting to defraud the company. Penalties may include imprisonment, fines, denial of insurance and civil damages.'
        },
        'DE': {
            'name': 'Delaware',
            'warning': 'Any person who knowingly, and with intent to injure, defraud or deceive any insurer, files a statement of claim containing any false, incomplete or misleading information is guilty of a felony.'
        },
        'DC': {
            'name': 'District of Columbia',
            'warning': 'WARNING: It is a crime to provide false or misleading information to an insurer for the purpose of defrauding the insurer or any other person. Penalties include imprisonment and/or fines.'
        },
        'FL': {
            'name': 'Florida',
            'warning': 'Any person who knowingly and with intent to injure, defraud, or deceive any insurer files a statement of claim containing any false, incomplete, or misleading information is guilty of a felony of the third degree.'
        },
        'HI': {
            'name': 'Hawaii',
            'warning': 'Any person who intentionally or knowingly misrepresents or conceals material facts, opinions, intention, or law to obtain or attempt to obtain coverage, benefits, recovery, or compensation commits the offense of insurance fraud which is a crime punishable by fines or imprisonment or both.'
        },
        'ID': {
            'name': 'Idaho',
            'warning': 'Any person who knowingly, and with intent to defraud or deceive any insurance company, files a statement containing any false, incomplete or misleading information is guilty of a felony.'
        },
        'IN': {
            'name': 'Indiana',
            'warning': 'A person who knowingly and with intent to defraud an insurer files a statement of claim containing any false, incomplete, or misleading information commits a felony.'
        },
        'KS': {
            'name': 'Kansas',
            'warning': 'Any person who, knowingly and with intent to defraud, presents, causes to be presented or prepares with knowledge or belief that it will be presented to or by an insurer commits a fraudulent insurance act.'
        },
        'KY': {
            'name': 'Kentucky',
            'warning': 'Any person who knowingly and with intent to defraud any insurance company or other person files a statement of claim containing any materially false information or conceals, for the purpose of misleading, information concerning any fact material thereto commits a fraudulent insurance act, which is a crime.'
        },
        'LA': {
            'name': 'Louisiana',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for payment of a loss or benefit or knowingly presents false information in an application for insurance is guilty of a crime and may be subject to fines and confinement in prison.'
        },
        'ME': {
            'name': 'Maine',
            'warning': 'It is a crime to knowingly provide false, incomplete or misleading information to an insurance company for the purpose of defrauding the company. Penalties may include imprisonment, fines or denial of insurance benefits.'
        },
        'MD': {
            'name': 'Maryland',
            'warning': 'Any person who knowingly or willfully presents a false or fraudulent claim for payment of a loss or benefit or who knowingly or willfully presents false information in an application for insurance is guilty of a crime and may be subject to fines and confinement in prison.'
        },
        'MI': {
            'name': 'Michigan',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for payment of a loss or benefit or knowingly presents false information in an application for insurance is guilty of a crime and may be subject to fines and confinement in prison.'
        },
        'MN': {
            'name': 'Minnesota',
            'warning': 'A person who files a claim with intent to defraud or helps commit a fraud against an insurer is guilty of a crime.'
        },
        'NV': {
            'name': 'Nevada',
            'warning': 'Pursuant to NRS 686A.291, any person who knowingly and willfully files a statement of claim that contains any false, incomplete or misleading information concerning a material fact is guilty of a category D felony.'
        },
        'NH': {
            'name': 'New Hampshire',
            'warning': 'Any person who, with a purpose to injure, defraud or deceive any insurance company, files a statement of claim containing any false, incomplete or misleading information is subject to prosecution and punishment for insurance fraud as provided in RSA 638:20.'
        },
        'NJ': {
            'name': 'New Jersey',
            'warning': 'Any person who knowingly files a statement of claim containing any false or misleading information is subject to criminal and civil penalties.'
        },
        'NM': {
            'name': 'New Mexico',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for payment of a loss or benefit or knowingly presents false information in an application for insurance is guilty of a crime and may be subject to civil fines and criminal penalties.'
        },
        'NY': {
            'name': 'New York',
            'warning': 'Any person who knowingly makes or knowingly assists, abets, solicits or conspires with another to make a false report of the theft, destruction, damage or conversion of any motor vehicle commits a fraudulent insurance act, which is a crime, and shall also be subject to a civil penalty not to exceed five thousand dollars.'
        },
        'OH': {
            'name': 'Ohio',
            'warning': 'Any person who, with intent to defraud or knowing that he is facilitating a fraud against an insurer, submits an application or files a claim containing a false or deceptive statement is guilty of insurance fraud.'
        },
        'OK': {
            'name': 'Oklahoma',
            'warning': 'WARNING: Any person who knowingly, and with intent to injure, defraud or deceive any insurer, makes any claim for the proceeds of an insurance policy containing any false, incomplete or misleading information is guilty of a felony.'
        },
        'OR': {
            'name': 'Oregon',
            'warning': 'Any person who knowingly and with intent to defraud or solicit another to defraud the insurer by submitting an application containing a false statement as to any material fact may be violating state law.'
        },
        'PA': {
            'name': 'Pennsylvania',
            'warning': 'Any person who knowingly and with intent to injure or defraud any insurer files an application or claim containing any false, incomplete or misleading information shall, upon conviction, be subject to imprisonment for up to seven years and the payment of a fine of up to $15,000.'
        },
        'PR': {
            'name': 'Puerto Rico',
            'warning': 'Any person who knowingly and with the intention of defrauding presents false information in an insurance application commits a felony and, upon conviction, shall be sanctioned by a fine of not less than $5,000 and not more than $10,000, or imprisonment for three (3) years, or both.'
        },
        'RI': {
            'name': 'Rhode Island',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for payment of a loss or benefit or knowingly presents false information in an application for insurance is guilty of a crime and may be subject to fines and confinement in prison.'
        },
        'TN': {
            'name': 'Tennessee',
            'warning': 'It is a crime to knowingly provide false, incomplete or misleading information to an insurance company for the purpose of defrauding the company. Penalties include imprisonment, fines and denial of insurance benefits.'
        },
        'TX': {
            'name': 'Texas',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for the payment of a loss is guilty of a crime and may be subject to fines and confinement in state prison.'
        },
        'VA': {
            'name': 'Virginia',
            'warning': 'It is a crime to knowingly provide false, incomplete or misleading information to an insurance company for the purpose of defrauding the company. Penalties include imprisonment, fines and denial of insurance benefits.'
        },
        'WA': {
            'name': 'Washington',
            'warning': 'It is a crime to knowingly provide false, incomplete or misleading information to an insurance company for the purpose of defrauding the company. Penalties include imprisonment, fines and denial of insurance benefits.'
        },
        'WV': {
            'name': 'West Virginia',
            'warning': 'Any person who knowingly presents a false or fraudulent claim for payment of a loss or benefit or knowingly presents false information in an application for insurance is guilty of a crime and may be subject to fines and confinement in prison.'
        }
    }
    
    def __init__(self):
        """Initialize the enhanced claims processor"""
        self.extracted_data = ExtractedClaim()
    
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try importing PyPDF2 if available
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            # If PyPDF2 not available, try reading as text
            try:
                with open(pdf_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except:
                raise ValueError("Unable to process PDF. Install PyPDF2: pip install PyPDF2")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")
    
    def extract_state_from_location(self, location: str) -> Optional[str]:
        """Extract state code from location string"""
        if not location:
            return None
        
        # Look for state codes in the location
        location_upper = location.upper()
        for state_code, state_info in self.STATE_FRAUD_WARNINGS.items():
            # Check for state code (e.g., "CA", "TX")
            if re.search(r'\b' + state_code + r'\b', location_upper):
                return state_code
            # Check for full state name
            if state_info['name'].upper() in location_upper:
                return state_code
        
        return None
    
    def extract_from_text(self, text: str) -> ExtractedClaim:
        """Extract structured data from FNOL text with enhanced pattern matching"""
        
        # Policy Number
        policy_patterns = [
            r'POLICY\s+NUMBER[:\s]+([A-Z0-9\-]+)',
            r'Policy\s*#?[:\s]+([A-Z0-9\-]+)',
            r'POL[:\s]+([A-Z0-9\-]+)',
        ]
        for pattern in policy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.extracted_data.policy_number = match.group(1).strip()
                break
        
        # Policyholder Name
        name_patterns = [
            r'NAME\s+OF\s+INSURED[:\s]+\(First,\s*Middle,\s*Last\)[:\s]*([A-Za-z\s\.\-]+?)(?:\n|INSURED|DATE)',
            r'INSURED[:\s]+([A-Za-z\s\.\-]+?)(?:\n|POLICY|DATE)',
            r'Policyholder[:\s]+([A-Za-z\s\.\-]+?)(?:\n)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) < 100:  # Reasonable name length
                    self.extracted_data.policyholder_name = name
                    break
        
        # Date of Loss
        date_patterns = [
            r'DATE\s+OF\s+LOSS[:\s]+(?:AND\s+TIME[:\s]+)?(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            r'LOSS\s+DATE[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
            r'INCIDENT\s+DATE[:\s]+(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.extracted_data.incident_date = match.group(1).strip()
                break
        
        # Time of Loss
        time_patterns = [
            r'TIME[:\s]+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)',
            r'(\d{1,2}:\d{2})\s+(AM|PM)',
            r'DATE\s+OF\s+LOSS\s+AND\s+TIME[:\s]+\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\s+(\d{1,2}:\d{2}\s*(?:AM|PM)?)',
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if match.lastindex == 2:
                    self.extracted_data.incident_time = f"{match.group(1)} {match.group(2)}"
                else:
                    self.extracted_data.incident_time = match.group(1).strip()
                break
        
        # Location - Street
        street_pattern = r'STREET[:\s]+([A-Za-z0-9\s\.,\-]+?)(?:\n|CITY|LOCATION)'
        match = re.search(street_pattern, text, re.IGNORECASE)
        street = match.group(1).strip() if match else ""
        
        # Location - City, State, ZIP
        city_pattern = r'CITY,?\s*STATE,?\s*ZIP[:\s]+([A-Za-z0-9\s\.,\-]+?)(?:\n|COUNTRY)'
        match = re.search(city_pattern, text, re.IGNORECASE)
        city_state_zip = match.group(1).strip() if match else ""
        
        # Combine location
        location_parts = [p for p in [street, city_state_zip] if p]
        if location_parts:
            self.extracted_data.incident_location = ", ".join(location_parts)
            # Extract state from location
            self.extracted_data.state = self.extract_state_from_location(self.extracted_data.incident_location)
        
        # Country
        country_pattern = r'COUNTRY[:\s]+([A-Za-z\s]+?)(?:\n|CITY)'
        match = re.search(country_pattern, text, re.IGNORECASE)
        if match:
            self.extracted_data.country = match.group(1).strip()
        
        # Description of Accident
        desc_patterns = [
            r'DESCRIPTION\s+OF\s+ACCIDENT[:\s]*(?:\(.*?\))?[:\s]*([^\n]+(?:\n(?!LOSS|DRIVER|OWNER|INSURED\s+VEHICLE)[^\n]+)*)',
            r'ACCIDENT\s+DESCRIPTION[:\s]+([^\n]+(?:\n(?!LOSS|DRIVER)[^\n]+)*)',
            r'DESCRIPTION[:\s]+([^\n]+(?:\n(?!LOSS|DRIVER)[^\n]+)*)',
        ]
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                desc = match.group(1).strip()
                # Clean up the description
                desc = re.sub(r'\s+', ' ', desc)
                if len(desc) > 10:  # Ensure meaningful description
                    self.extracted_data.incident_description = desc
                    break
        
        # VIN
        vin_pattern = r'V\.?I\.?N\.?[:\s]+([A-Z0-9]{17}|[A-Z0-9\-]+)'
        match = re.search(vin_pattern, text, re.IGNORECASE)
        if match:
            vin = match.group(1).strip()
            self.extracted_data.vin = vin
            self.extracted_data.asset_id = vin
        
        # Vehicle Year
        year_pattern = r'(?:VEH\s*#\s*)?YEAR[:\s]+(\d{4})'
        match = re.search(year_pattern, text, re.IGNORECASE)
        if match:
            self.extracted_data.vehicle_year = match.group(1).strip()
        
        # Vehicle Make
        make_pattern = r'MAKE[:\s]+([A-Za-z0-9\s\-]+?)(?:\s+MODEL|:|\n)'
        match = re.search(make_pattern, text, re.IGNORECASE)
        if match:
            make = match.group(1).strip()
            if len(make) < 50:  # Reasonable length
                self.extracted_data.vehicle_make = make
        
        # Vehicle Model
        model_pattern = r'MODEL[:\s]+([A-Za-z0-9\s\-]+?)(?:\s+BODY|:|\n|VEH)'
        match = re.search(model_pattern, text, re.IGNORECASE)
        if match:
            model = match.group(1).strip()
            if len(model) < 50:
                self.extracted_data.vehicle_model = model
        
        # Asset Type
        self.extracted_data.asset_type = "Vehicle - Automobile"
        
        # Driver Name
        driver_patterns = [
            r"DRIVER'S\s+NAME\s+AND\s+ADDRESS[:\s]*(?:\(.*?\))?[:\s]*([A-Za-z\s\.\-]+?)(?:\n|PHONE)",
            r"DRIVER\s+NAME[:\s]+([A-Za-z\s\.\-]+?)(?:\n|PHONE)",
        ]
        for pattern in driver_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) < 100:
                    self.extracted_data.driver_name = name
                    break
        
        # Driver's License
        license_patterns = [
            r"DRIVER'S\s+LICENSE\s+NUMBER[:\s]+([A-Z0-9\-]+)",
            r"LICENSE\s+NUMBER[:\s]+([A-Z0-9\-]+)",
            r"DL\s*#?[:\s]+([A-Z0-9\-]+)",
        ]
        for pattern in license_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.extracted_data.driver_license = match.group(1).strip()
                break
        
        # Police Report Number
        report_patterns = [
            r'REPORT\s+NUMBER[:\s]+([A-Z0-9\-]+)',
            r'POLICE\s+REPORT[:\s]+([A-Z0-9\-]+)',
            r'CASE\s+NUMBER[:\s]+([A-Z0-9\-]+)',
        ]
        for pattern in report_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                report = match.group(1).strip()
                if report.lower() not in ['not', 'none', 'n/a']:
                    self.extracted_data.police_report_number = report
                    break
        
        # Damage Estimate
        estimate_patterns = [
            r'ESTIMATE\s+AMOUNT[:\s]+\$?\s*([0-9,]+(?:\.\d{2})?)',
            r'ESTIMATED?\s+DAMAGE[:\s]+\$?\s*([0-9,]+(?:\.\d{2})?)',
            r'DAMAGE\s+ESTIMATE[:\s]+\$?\s*([0-9,]+(?:\.\d{2})?)',
        ]
        for pattern in estimate_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    self.extracted_data.estimated_damage = amount
                    self.extracted_data.initial_estimate = amount
                    break
                except ValueError:
                    pass
        
        # Check for injury indicators (only in description, not whole text)
        injury_found = False
        description_lower = (self.extracted_data.incident_description or "").lower()
        
        for keyword in self.INJURY_KEYWORDS:
            if keyword in description_lower:
                injury_found = True
                break
        
        # Claim Type
        if injury_found:
            self.extracted_data.claim_type = "Bodily Injury"
        else:
            self.extracted_data.claim_type = "Property Damage"
        
        # Set claimant (defaults to policyholder)
        if self.extracted_data.policyholder_name:
            self.extracted_data.claimant_name = self.extracted_data.policyholder_name
        
        # Extract contact information
        phone_pattern = r'PHONE.*?(\d{3}[-\.\s]?\d{3}[-\.\s]?\d{4})'
        match = re.search(phone_pattern, text, re.IGNORECASE)
        if match:
            self.extracted_data.claimant_contact = match.group(1)
        
        return self.extracted_data
    
    def identify_missing_fields(self) -> List[str]:
        """Identify missing mandatory fields"""
        missing = []
        data_dict = self.extracted_data.to_dict()
        
        for field in self.MANDATORY_FIELDS:
            if field not in data_dict or data_dict[field] is None or data_dict[field] == "":
                missing.append(field)
        
        return missing
    
    def check_fraud_indicators(self) -> tuple[bool, List[str]]:
        """Check for fraud-related keywords in description"""
        if not self.extracted_data.incident_description:
            return False, []
        
        description_lower = self.extracted_data.incident_description.lower()
        found_keywords = []
        
        for keyword in self.FRAUD_KEYWORDS:
            if keyword in description_lower:
                found_keywords.append(keyword)
        
        return len(found_keywords) > 0, found_keywords
    
    def check_injury_claim(self) -> bool:
        """Check if claim involves injury"""
        return self.extracted_data.claim_type == "Bodily Injury"
    
    def get_state_warning(self) -> Optional[Dict[str, str]]:
        """Get state-specific fraud warning"""
        if not self.extracted_data.state:
            return None
        
        state_info = self.STATE_FRAUD_WARNINGS.get(self.extracted_data.state)
        if state_info:
            return {
                'state_code': self.extracted_data.state,
                'state_name': state_info['name'],
                'warning': state_info['warning']
            }
        return None
    
    def determine_route(self, missing_fields: List[str]) -> tuple[str, str]:
        """Determine routing based on business rules"""
        
        # Rule 1: Missing mandatory fields → Manual Review (HIGHEST PRIORITY)
        if missing_fields:
            return (
                "Manual Review",
                f"Missing mandatory fields: {', '.join(missing_fields)}. Requires human verification to complete claim data."
            )
        
        # Rule 2: Fraud indicators → Investigation (SECOND PRIORITY)
        fraud_detected, fraud_keywords = self.check_fraud_indicators()
        if fraud_detected:
            return (
                "Investigation Queue",
                f"Fraud indicators detected in incident description. Keywords found: {', '.join(fraud_keywords)}. Requires Special Investigation Unit review."
            )
        
        # Rule 3: Injury claims → Specialist Queue (THIRD PRIORITY)
        if self.check_injury_claim():
            return (
                "Specialist Queue - Bodily Injury",
                "Claim involves bodily injury. Routed to injury claims specialists for medical review and liability assessment."
            )
        
        # Rule 4: Low damage → Fast Track (FOURTH PRIORITY)
        if self.extracted_data.estimated_damage and self.extracted_data.estimated_damage < self.FAST_TRACK_THRESHOLD:
            return (
                "Fast Track",
                f"Estimated damage (${self.extracted_data.estimated_damage:,.2f}) is below fast-track threshold (${self.FAST_TRACK_THRESHOLD:,}). No missing fields, no fraud indicators, no injuries. Eligible for automated processing."
            )
        
        # Rule 5: High damage → Standard Review
        if self.extracted_data.estimated_damage and self.extracted_data.estimated_damage >= self.FAST_TRACK_THRESHOLD:
            return (
                "Standard Review Queue",
                f"Estimated damage (${self.extracted_data.estimated_damage:,.2f}) exceeds fast-track threshold (${self.FAST_TRACK_THRESHOLD:,}). Requires standard claims adjuster review and potentially on-site inspection."
            )
        
        # Default: Manual Review
        return (
            "Manual Review",
            "Unable to determine damage estimate or claim routing. Requires manual assessment."
        )
    
    def process_claim(self, file_path: str = None, text_content: str = None) -> Dict[str, Any]:
        """Main processing function"""
        
        # Extract text
        if file_path:
            text = self.extract_from_pdf(file_path)
        elif text_content:
            text = text_content
        else:
            raise ValueError("Either file_path or text_content must be provided")
        
        # Extract structured data
        self.extract_from_text(text)
        
        # Identify missing fields
        missing_fields = self.identify_missing_fields()
        
        # Determine routing
        route, reasoning = self.determine_route(missing_fields)
        
        # Get state-specific warning
        state_warning = self.get_state_warning()
        
        # Check fraud and injury
        fraud_detected, fraud_keywords = self.check_fraud_indicators()
        injury_claim = self.check_injury_claim()
        
        # Build output in exact format requested
        output = {
            "extractedFields": self.extracted_data.to_dict(),
            "missingFields": missing_fields,
            "recommendedRoute": route,
            "reasoning": reasoning
        }
        
        # Add additional metadata
        output["metadata"] = {
            "fraudIndicators": fraud_detected,
            "fraudKeywordsFound": fraud_keywords,
            "injuryClaim": injury_claim,
            "stateWarning": state_warning,
            "processingTimestamp": datetime.now().isoformat(),
            "formType": "ACORD 2 - Automobile Loss Notice"
        }
        
        return output


# Convenience function for quick processing
def process_fnol_claim(text_or_file: str, is_file: bool = False) -> Dict[str, Any]:
    """
    Quick function to process a claim
    
    Args:
        text_or_file: Either FNOL text content or file path
        is_file: True if text_or_file is a file path, False if it's text content
    
    Returns:
        Processed claim result dictionary
    """
    processor = EnhancedClaimsProcessor()
    
    if is_file:
        return processor.process_claim(file_path=text_or_file)
    else:
        return processor.process_claim(text_content=text_or_file)