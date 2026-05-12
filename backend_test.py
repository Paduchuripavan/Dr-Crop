#!/usr/bin/env python3
"""
Dr Crop Backend API Testing Suite
Tests all backend endpoints comprehensively
"""

import requests
import json
import base64
import time
from typing import Dict, Any, Optional
import sys

# Configuration
BACKEND_URL = "https://crop-doctor-44.preview.emergentagent.com/api"
TEST_EMAIL = "farmer@test.com"
TEST_PASSWORD = "test123"
TEST_NAME = "Test Farmer"
TEST_LOCATION = "Test Farm, CA"

class DrCropAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> requests.Response:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if self.auth_token:
            default_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=default_headers, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def create_test_image_base64(self) -> str:
        """Create a small test image in base64 format"""
        # Create a simple 10x10 pixel PNG image (red square)
        import io
        try:
            from PIL import Image
            img = Image.new('RGB', (10, 10), color='red')
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_data = buffer.getvalue()
            return base64.b64encode(img_data).decode('utf-8')
        except ImportError:
            # Fallback: create a minimal base64 encoded image
            # This is a 1x1 red pixel PNG
            minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x07\n\xdb\xa8\x00\x00\x00\x00IEND\xaeB`\x82'
            return base64.b64encode(minimal_png).decode('utf-8')
    
    def test_auth_register(self):
        """Test user registration"""
        test_name = "Auth Registration"
        
        # First try to register with test credentials
        register_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "location": TEST_LOCATION
        }
        
        try:
            response = self.make_request("POST", "/auth/register", register_data)
            
            if response.status_code == 400 and "already registered" in response.text:
                # User already exists, that's fine for testing
                self.log_result(test_name, True, "User already exists (expected for repeated tests)")
                return True
            elif response.status_code == 201 or response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result(test_name, True, "Registration successful")
                    return True
                else:
                    self.log_result(test_name, False, "Registration response missing required fields", data)
                    return False
            else:
                self.log_result(test_name, False, f"Registration failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Registration request failed: {str(e)}")
            return False
    
    def test_auth_login(self):
        """Test user login"""
        test_name = "Auth Login"
        
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.make_request("POST", "/auth/login", login_data)
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    self.user_id = data["user"]["id"]
                    self.log_result(test_name, True, "Login successful")
                    return True
                else:
                    self.log_result(test_name, False, "Login response missing required fields", data)
                    return False
            else:
                self.log_result(test_name, False, f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Login request failed: {str(e)}")
            return False
    
    def test_get_crops(self):
        """Test getting all crops"""
        test_name = "Get All Crops"
        
        try:
            response = self.make_request("GET", "/crops")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if crops have required fields
                    crop = data[0]
                    required_fields = ["id", "name", "scientific_name", "description", "icon", "growing_tips"]
                    if all(field in crop for field in required_fields):
                        self.log_result(test_name, True, f"Retrieved {len(data)} crops successfully")
                        return data
                    else:
                        self.log_result(test_name, False, "Crops missing required fields", crop)
                        return None
                else:
                    self.log_result(test_name, False, "No crops returned or invalid format", data)
                    return None
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return None
    
    def test_get_single_crop(self, crop_id: str):
        """Test getting a single crop by ID"""
        test_name = "Get Single Crop"
        
        try:
            response = self.make_request("GET", f"/crops/{crop_id}")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "name", "scientific_name", "description", "icon", "growing_tips"]
                if all(field in data for field in required_fields):
                    self.log_result(test_name, True, f"Retrieved crop '{data['name']}' successfully")
                    return True
                else:
                    self.log_result(test_name, False, "Crop missing required fields", data)
                    return False
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_get_diseases(self):
        """Test getting all diseases"""
        test_name = "Get All Diseases"
        
        try:
            response = self.make_request("GET", "/diseases")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    disease = data[0]
                    required_fields = ["id", "name", "crop_name", "symptoms", "causes", "treatment", "prevention", "severity"]
                    if all(field in disease for field in required_fields):
                        self.log_result(test_name, True, f"Retrieved {len(data)} diseases successfully")
                        return data
                    else:
                        self.log_result(test_name, False, "Diseases missing required fields", disease)
                        return None
                else:
                    self.log_result(test_name, False, "No diseases returned or invalid format", data)
                    return None
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return None
    
    def test_get_diseases_by_crop(self):
        """Test filtering diseases by crop"""
        test_name = "Get Diseases by Crop (Tomato)"
        
        try:
            response = self.make_request("GET", "/diseases?crop_name=Tomato")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Check that all returned diseases are for Tomato
                    tomato_diseases = [d for d in data if d.get("crop_name") == "Tomato"]
                    if len(tomato_diseases) == len(data) and len(data) > 0:
                        self.log_result(test_name, True, f"Retrieved {len(data)} tomato diseases successfully")
                        return True
                    elif len(data) == 0:
                        self.log_result(test_name, True, "No tomato diseases found (valid result)")
                        return True
                    else:
                        self.log_result(test_name, False, "Some diseases not for Tomato", data)
                        return False
                else:
                    self.log_result(test_name, False, "Invalid response format", data)
                    return False
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_ai_diagnosis(self):
        """Test AI plant diagnosis"""
        test_name = "AI Plant Diagnosis"
        
        if not self.user_id:
            self.log_result(test_name, False, "No user_id available for diagnosis")
            return False
        
        try:
            # Create test image
            test_image = self.create_test_image_base64()
            
            diagnosis_data = {
                "user_id": self.user_id,
                "crop_name": "Tomato",
                "image_base64": test_image,
                "location": TEST_LOCATION
            }
            
            response = self.make_request("POST", "/diagnose", diagnosis_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "user_id", "diagnosis_text", "timestamp"]
                if all(field in data for field in required_fields):
                    # Check if AI actually processed the image
                    if data.get("diagnosis_text") and len(data["diagnosis_text"]) > 10:
                        self.log_result(test_name, True, "AI diagnosis completed successfully")
                        return data
                    else:
                        self.log_result(test_name, False, "AI diagnosis text too short or empty", data)
                        return None
                else:
                    self.log_result(test_name, False, "Diagnosis response missing required fields", data)
                    return None
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return None
    
    def test_community_posts(self):
        """Test community post creation and retrieval"""
        test_name = "Community Posts"
        
        if not self.user_id:
            self.log_result(test_name, False, "No user_id available for community posts")
            return False
        
        try:
            # Create a test post
            post_data = {
                "user_id": self.user_id,
                "user_name": TEST_NAME,
                "title": "Test Post - Disease in my tomatoes",
                "content": "I'm seeing some brown spots on my tomato leaves. Any advice?",
                "crop_type": "Tomato",
                "images": []
            }
            
            response = self.make_request("POST", "/community/posts", post_data)
            
            if response.status_code == 200:
                post = response.json()
                post_id = post.get("id")
                
                if post_id:
                    # Test getting all posts
                    response = self.make_request("GET", "/community/posts")
                    if response.status_code == 200:
                        posts = response.json()
                        if isinstance(posts, list):
                            self.log_result(test_name, True, f"Created post and retrieved {len(posts)} posts")
                            return post_id
                        else:
                            self.log_result(test_name, False, "Invalid posts format", posts)
                            return None
                    else:
                        self.log_result(test_name, False, f"Failed to get posts: {response.status_code}", response.text)
                        return None
                else:
                    self.log_result(test_name, False, "Post creation response missing ID", post)
                    return None
            else:
                self.log_result(test_name, False, f"Failed to create post: {response.status_code}", response.text)
                return None
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return None
    
    def test_post_like(self, post_id: str):
        """Test liking a post"""
        test_name = "Like Post"
        
        try:
            response = self.make_request("POST", f"/community/posts/{post_id}/like")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_result(test_name, True, "Post liked successfully")
                    return True
                else:
                    self.log_result(test_name, False, "Like response invalid", data)
                    return False
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_community_replies(self, post_id: str):
        """Test creating and getting replies"""
        test_name = "Community Replies"
        
        if not self.user_id:
            self.log_result(test_name, False, "No user_id available for replies")
            return False
        
        try:
            # Create a reply
            reply_data = {
                "post_id": post_id,
                "user_id": self.user_id,
                "user_name": TEST_NAME,
                "content": "You might have early blight. Try removing affected leaves and applying fungicide."
            }
            
            response = self.make_request("POST", "/community/replies", reply_data)
            
            if response.status_code == 200:
                reply = response.json()
                
                # Test getting replies
                response = self.make_request("GET", f"/community/replies/{post_id}")
                if response.status_code == 200:
                    replies = response.json()
                    if isinstance(replies, list):
                        self.log_result(test_name, True, f"Created reply and retrieved {len(replies)} replies")
                        return True
                    else:
                        self.log_result(test_name, False, "Invalid replies format", replies)
                        return False
                else:
                    self.log_result(test_name, False, f"Failed to get replies: {response.status_code}", response.text)
                    return False
            else:
                self.log_result(test_name, False, f"Failed to create reply: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_weather(self):
        """Test weather endpoint"""
        test_name = "Weather Data"
        
        try:
            response = self.make_request("GET", "/weather?location=test")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["location", "temperature", "humidity", "rainfall", "forecast"]
                if all(field in data for field in required_fields):
                    self.log_result(test_name, True, "Weather data retrieved successfully")
                    return True
                else:
                    self.log_result(test_name, False, "Weather data missing required fields", data)
                    return False
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_fertilizer_calculator(self):
        """Test fertilizer calculation"""
        test_name = "Fertilizer Calculator"
        
        try:
            calc_data = {
                "crop_name": "Tomato",
                "plot_size": 2.5,
                "soil_type": "loamy"
            }
            
            response = self.make_request("POST", "/fertilizer/calculate", calc_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["crop", "plot_size", "nitrogen_kg", "phosphorus_kg", "potassium_kg", "recommendations"]
                if all(field in data for field in required_fields):
                    self.log_result(test_name, True, "Fertilizer calculation completed successfully")
                    return True
                else:
                    self.log_result(test_name, False, "Fertilizer response missing required fields", data)
                    return False
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def test_disease_alerts(self):
        """Test disease alerts"""
        test_name = "Disease Alerts"
        
        try:
            response = self.make_request("GET", "/alerts")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result(test_name, True, f"Retrieved {len(data)} disease alerts")
                    return True
                else:
                    self.log_result(test_name, False, "Invalid alerts format", data)
                    return False
            else:
                self.log_result(test_name, False, f"Failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result(test_name, False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🧪 Starting Dr Crop Backend API Tests")
        print(f"🔗 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Test authentication first
        auth_success = False
        if self.test_auth_register():
            auth_success = True
        
        if not auth_success:
            if self.test_auth_login():
                auth_success = True
        
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with authenticated tests")
            return False
        
        # Test crops
        crops = self.test_get_crops()
        if crops and len(crops) > 0:
            self.test_get_single_crop(crops[0]["id"])
        
        # Test diseases
        self.test_get_diseases()
        self.test_get_diseases_by_crop()
        
        # Test AI diagnosis (core feature)
        self.test_ai_diagnosis()
        
        # Test community features
        post_id = self.test_community_posts()
        if post_id:
            self.test_post_like(post_id)
            self.test_community_replies(post_id)
        
        # Test additional features
        self.test_weather()
        self.test_fertilizer_calculator()
        self.test_disease_alerts()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r["success"])
        failed = len(self.test_results) - passed
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total: {len(self.test_results)}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)

def main():
    """Main test runner"""
    tester = DrCropAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())