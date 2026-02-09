"""
Comprehensive Test Suite for Enhanced Claims Processor
Tests all routing scenarios and state-specific compliance
"""

import json
from enhanced_claims_agent import EnhancedClaimsProcessor


# Test samples covering all scenarios
TEST_SAMPLES = {
    "bodily_injury_texas": """
POLICY NUMBER: AUTO-TX-2024-001
NAME OF INSURED: Sarah Johnson
DATE OF LOSS AND TIME: 02/05/2024 10:15 AM
STREET: Interstate 35 North
CITY, STATE, ZIP: Austin, TX 78701
COUNTRY: USA
DESCRIPTION OF ACCIDENT: Multi-vehicle collision. Driver transported to hospital with neck injuries. Passenger suffered whiplash.
YEAR: 2022
MAKE: Toyota
MODEL: Camry
V.I.N.: 4T1B11HK5NU123456
DRIVER'S LICENSE NUMBER: TX12345678
ESTIMATE AMOUNT: $45,000
POLICE REPORT NUMBER: APD-2024-001
""",
    
    "fast_track_arizona": """
POLICY NUMBER: AUTO-AZ-2024-002
NAME OF INSURED: David Williams
DATE OF LOSS: 01/28/2024
STREET: Parking lot Desert Mall
CITY, STATE, ZIP: Phoenix, AZ 85001
COUNTRY: USA
DESCRIPTION OF ACCIDENT: Vehicle damaged while parked. Minor dent and scratches on door.
YEAR: 2023
MAKE: Honda
MODEL: Civic
V.I.N.: 2HGFC2F59NH123456
DRIVER'S LICENSE NUMBER: AZ87654321
ESTIMATE AMOUNT: $2,800
""",
    
    "fraud_florida": """
POLICY NUMBER: AUTO-FL-2024-003
NAME OF INSURED: Jennifer Lopez
DATE OF LOSS: 02/01/2024
CITY, STATE, ZIP: Miami, FL 33101
COUNTRY: USA
DESCRIPTION OF ACCIDENT: Story is inconsistent. Initially claimed car was stolen but found with damage. Details keep changing. This appears to be a staged accident.
YEAR: 2020
MAKE: BMW
MODEL: X5
V.I.N.: 5UXKR0C58L9B12345
ESTIMATE AMOUNT: $18,500
""",
    
    "high_damage_california": """
POLICY NUMBER: AUTO-CA-2024-004
NAME OF INSURED: Robert Anderson
DATE OF LOSS: 02/07/2024
STREET: Hollywood Boulevard
CITY, STATE, ZIP: Los Angeles, CA 90028
COUNTRY: USA
DESCRIPTION OF ACCIDENT: Red light runner struck vehicle. Significant structural damage. Traffic camera footage available.
YEAR: 2023
MAKE: Tesla
MODEL: Model Y
V.I.N.: 5YJYGDEE1NF123456
DRIVER'S LICENSE NUMBER: CA D1234567
ESTIMATE AMOUNT: $42,500
POLICE REPORT NUMBER: LAPD-2024-001
""",
    
    "missing_fields": """
NAME OF INSURED: Michael Anderson
DATE OF LOSS: 01/30/2024
DESCRIPTION OF ACCIDENT: Hit and run incident.
MAKE: Subaru
MODEL: Outback
""",
    
    "injury_new_york": """
POLICY NUMBER: AUTO-NY-2024-005
NAME OF INSURED: Emily Chen
DATE OF LOSS: 02/10/2024
STREET: Broadway and 42nd Street
CITY, STATE, ZIP: New York, NY 10036
COUNTRY: USA
DESCRIPTION OF ACCIDENT: Pedestrian accident. Driver injured with broken arm and contusions. Ambulance called to scene.
YEAR: 2021
MAKE: Ford
MODEL: Explorer
V.I.N.: 1FM5K8D87MGA12345
DRIVER'S LICENSE NUMBER: NY123456789
ESTIMATE AMOUNT: $15,000
POLICE REPORT NUMBER: NYPD-2024-0210
""",
    
    "property_only_pennsylvania": """
POLICY NUMBER: AUTO-PA-2024-006
NAME OF INSURED: James Miller
DATE OF LOSS: 02/12/2024
STREET: Main Street
CITY, STATE, ZIP: Philadelphia, PA 19103
COUNTRY: USA
DESCRIPTION OF ACCIDENT: Single vehicle accident. Vehicle slid on ice into guardrail. No injuries.
YEAR: 2022
MAKE: Chevrolet
MODEL: Silverado
V.I.N.: 1GCUYEED6KZ234567
DRIVER'S LICENSE NUMBER: PA98765432
ESTIMATE AMOUNT: $8,500
POLICE REPORT NUMBER: PPD-2024-0212
"""
}


def run_comprehensive_tests():
    """Run all test scenarios"""
    
    print("\n" + "="*100)
    print("COMPREHENSIVE CLAIMS PROCESSING TEST SUITE".center(100))
    print("="*100 + "\n")
    
    processor = EnhancedClaimsProcessor()
    results = {}
    
    for test_name, test_content in TEST_SAMPLES.items():
        print(f"\n{'='*100}")
        print(f"TEST: {test_name.upper().replace('_', ' ')}")
        print(f"{'='*100}\n")
        
        try:
            result = processor.process_claim(text_content=test_content)
            results[test_name] = result
            
            # Display key information
            print(f"✅ Status: PROCESSED")
            print(f"📋 Policy: {result['extractedFields'].get('policy_number', 'N/A')}")
            print(f"👤 Insured: {result['extractedFields'].get('policyholder_name', 'N/A')}")
            print(f"📅 Date: {result['extractedFields'].get('incident_date', 'N/A')}")
            print(f"📍 Location: {result['extractedFields'].get('incident_location', 'N/A')}")
            print(f"💰 Damage: ${result['extractedFields'].get('estimated_damage', 0):,.2f}")
            print(f"🏷️  Type: {result['extractedFields'].get('claim_type', 'N/A')}")
            
            # Missing fields
            if result['missingFields']:
                print(f"\n⚠️  Missing Fields ({len(result['missingFields'])}):")
                for field in result['missingFields']:
                    print(f"   - {field}")
            else:
                print(f"\n✅ All mandatory fields present")
            
            # Fraud indicators
            if result['metadata']['fraudIndicators']:
                print(f"\n🚨 FRAUD INDICATORS DETECTED!")
                print(f"   Keywords: {', '.join(result['metadata']['fraudKeywordsFound'])}")
            
            # Injury claim
            if result['metadata']['injuryClaim']:
                print(f"\n🏥 BODILY INJURY CLAIM")
            
            # State warning
            if result['metadata']['stateWarning']:
                state_info = result['metadata']['stateWarning']
                print(f"\n⚖️  State: {state_info['state_name']} ({state_info['state_code']})")
                print(f"   Warning: {state_info['warning'][:100]}...")
            
            # Routing decision
            print(f"\n🎯 ROUTING DECISION: {result['recommendedRoute']}")
            print(f"📝 Reasoning: {result['reasoning']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results[test_name] = {"error": str(e)}
    
    # Summary
    print("\n" + "="*100)
    print("TEST SUMMARY")
    print("="*100 + "\n")
    
    routing_counts = {}
    for test_name, result in results.items():
        if 'error' not in result:
            route = result['recommendedRoute']
            routing_counts[route] = routing_counts.get(route, 0) + 1
    
    print(f"Total Tests: {len(TEST_SAMPLES)}")
    print(f"Successful: {len([r for r in results.values() if 'error' not in r])}")
    print(f"Failed: {len([r for r in results.values() if 'error' in r])}")
    
    print("\nRouting Distribution:")
    for route, count in sorted(routing_counts.items()):
        print(f"  • {route}: {count}")
    
    # Validation checks
    print("\n" + "="*100)
    print("VALIDATION CHECKS")
    print("="*100 + "\n")
    
    checks = {
        "Bodily Injury Routes to Specialist": False,
        "Fraud Routes to Investigation": False,
        "Missing Fields Routes to Manual Review": False,
        "Low Damage Routes to Fast Track": False,
        "High Damage Routes Appropriately": False,
        "State Warnings Applied": False
    }
    
    # Check bodily injury routing
    if 'bodily_injury_texas' in results and 'error' not in results['bodily_injury_texas']:
        if 'Specialist' in results['bodily_injury_texas']['recommendedRoute']:
            checks["Bodily Injury Routes to Specialist"] = True
    
    if 'injury_new_york' in results and 'error' not in results['injury_new_york']:
        if 'Specialist' in results['injury_new_york']['recommendedRoute']:
            checks["Bodily Injury Routes to Specialist"] = True
    
    # Check fraud routing
    if 'fraud_florida' in results and 'error' not in results['fraud_florida']:
        if 'Investigation' in results['fraud_florida']['recommendedRoute']:
            checks["Fraud Routes to Investigation"] = True
    
    # Check missing fields
    if 'missing_fields' in results and 'error' not in results['missing_fields']:
        if 'Manual Review' in results['missing_fields']['recommendedRoute']:
            checks["Missing Fields Routes to Manual Review"] = True
    
    # Check fast track
    if 'fast_track_arizona' in results and 'error' not in results['fast_track_arizona']:
        if 'Fast Track' in results['fast_track_arizona']['recommendedRoute']:
            checks["Low Damage Routes to Fast Track"] = True
    
    # Check high damage
    if 'high_damage_california' in results and 'error' not in results['high_damage_california']:
        route = results['high_damage_california']['recommendedRoute']
        if 'Standard Review' in route or 'Specialist' in route:
            checks["High Damage Routes Appropriately"] = True
    
    # Check state warnings
    state_warnings_found = sum(1 for r in results.values() 
                               if 'error' not in r and r['metadata'].get('stateWarning'))
    if state_warnings_found > 0:
        checks["State Warnings Applied"] = True
    
    # Display validation results
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
    
    # Export results
    output_file = "comprehensive_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results exported to: {output_file}")
    print("\n" + "="*100 + "\n")
    
    return results


if __name__ == "__main__":
    run_comprehensive_tests()
