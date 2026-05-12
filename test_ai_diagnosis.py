#!/usr/bin/env python3
"""
Test AI Diagnosis functionality in detail
"""

import requests
import json
import base64

def test_ai_diagnosis():
    # Test AI diagnosis with more detailed verification
    BACKEND_URL = 'https://crop-doctor-44.preview.emergentagent.com/api'
    TEST_EMAIL = 'farmer@test.com'
    TEST_PASSWORD = 'test123'

    # Login first
    login_data = {'email': TEST_EMAIL, 'password': TEST_PASSWORD}
    response = requests.post(f'{BACKEND_URL}/auth/login', json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
        
    auth_data = response.json()
    token = auth_data['access_token']
    user_id = auth_data['user']['id']

    # Create a simple test image (1x1 red pixel PNG)
    minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x07\n\xdb\xa8\x00\x00\x00\x00IEND\xaeB`\x82'
    test_image = base64.b64encode(minimal_png).decode('utf-8')

    # Test diagnosis
    diagnosis_data = {
        'user_id': user_id,
        'crop_name': 'Tomato',
        'image_base64': test_image,
        'location': 'Test Farm, CA'
    }

    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response = requests.post(f'{BACKEND_URL}/diagnose', json=diagnosis_data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print('✅ AI Diagnosis Test Results:')
        print(f'   Disease: {result.get("disease_name", "N/A")}')
        print(f'   Confidence: {result.get("confidence", "N/A")}')
        print(f'   Treatment: {result.get("treatment", "N/A")[:100]}...' if result.get('treatment') else '   Treatment: N/A')
        print(f'   Full response length: {len(result.get("diagnosis_text", ""))} characters')
        
        # Check if Gemini actually processed it
        if result.get('diagnosis_text') and len(result['diagnosis_text']) > 50:
            print('✅ Gemini AI integration working - detailed response received')
            print(f'   Sample response: {result["diagnosis_text"][:200]}...')
            return True
        else:
            print('⚠️  Short response - may indicate AI integration issue')
            print(f'   Response: {result.get("diagnosis_text", "No response")}')
            return False
    else:
        print(f'❌ AI Diagnosis failed: {response.status_code} - {response.text}')
        return False

if __name__ == "__main__":
    test_ai_diagnosis()