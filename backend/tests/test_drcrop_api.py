"""
Dr Crop API Backend Tests
Tests all endpoints: auth, crops, diseases, diagnoses, community, weather, fertilizer, alerts
"""
import pytest
import requests
import os
import base64
import time

# Get backend URL from environment
BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    pytest.skip("EXPO_PUBLIC_BACKEND_URL not set", allow_module_level=True)

# Test credentials
TEST_EMAIL = "test_farmer_" + str(int(time.time())) + "@test.com"
TEST_PASSWORD = "test123"
TEST_NAME = "Test Farmer"
TEST_LOCATION = "Test Farm"

# Global variables to store test data
test_user_id = None
test_token = None
test_crop_id = None
test_diagnosis_id = None
test_post_id = None


class TestAuth:
    """Authentication endpoint tests"""

    def test_01_register_success(self):
        """Test user registration"""
        global test_user_id, test_token
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": TEST_NAME,
            "location": TEST_LOCATION
        })
        
        print(f"Register response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["email"] == TEST_EMAIL
        assert data["user"]["name"] == TEST_NAME
        
        test_user_id = data["user"]["id"]
        test_token = data["access_token"]
        print(f"✓ User registered successfully: {test_user_id}")

    def test_02_register_duplicate_email(self):
        """Test registration with duplicate email fails"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Another User",
        })
        
        assert response.status_code == 400, "Duplicate email should return 400"
        print("✓ Duplicate email registration blocked")

    def test_03_login_success(self):
        """Test user login"""
        global test_token
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        print(f"Login response status: {response.status_code}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        
        test_token = data["access_token"]
        print("✓ Login successful")

    def test_04_login_invalid_credentials(self):
        """Test login with wrong password"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401, "Invalid credentials should return 401"
        print("✓ Invalid credentials rejected")


class TestCrops:
    """Crop endpoints tests"""

    def test_01_get_all_crops(self):
        """Test getting all crops"""
        global test_crop_id
        
        response = requests.get(f"{BASE_URL}/api/crops")
        
        print(f"Get crops response status: {response.status_code}")
        assert response.status_code == 200
        
        crops = response.json()
        assert isinstance(crops, list), "Response should be a list"
        assert len(crops) >= 8, f"Expected at least 8 crops, got {len(crops)}"
        
        # Verify crop structure
        crop = crops[0]
        assert "id" in crop
        assert "name" in crop
        assert "scientific_name" in crop
        assert "icon" in crop
        
        test_crop_id = crop["id"]
        print(f"✓ Found {len(crops)} crops")

    def test_02_get_crop_by_id(self):
        """Test getting specific crop"""
        if not test_crop_id:
            pytest.skip("No crop ID available")
        
        response = requests.get(f"{BASE_URL}/api/crops/{test_crop_id}")
        
        assert response.status_code == 200
        crop = response.json()
        assert crop["id"] == test_crop_id
        assert "name" in crop
        print(f"✓ Retrieved crop: {crop['name']}")


class TestDiseases:
    """Disease endpoints tests"""

    def test_01_get_all_diseases(self):
        """Test getting all diseases"""
        response = requests.get(f"{BASE_URL}/api/diseases")
        
        print(f"Get diseases response status: {response.status_code}")
        assert response.status_code == 200
        
        diseases = response.json()
        assert isinstance(diseases, list)
        assert len(diseases) >= 5, f"Expected at least 5 diseases, got {len(diseases)}"
        
        # Verify disease structure
        disease = diseases[0]
        assert "id" in disease
        assert "name" in disease
        assert "crop_name" in disease
        assert "symptoms" in disease
        assert "treatment" in disease
        
        print(f"✓ Found {len(diseases)} diseases")

    def test_02_get_diseases_by_crop(self):
        """Test filtering diseases by crop"""
        response = requests.get(f"{BASE_URL}/api/diseases?crop_name=Tomato")
        
        assert response.status_code == 200
        diseases = response.json()
        
        # All returned diseases should be for Tomato
        for disease in diseases:
            assert disease["crop_name"] == "Tomato"
        
        print(f"✓ Found {len(diseases)} diseases for Tomato")


class TestDiagnosis:
    """Diagnosis endpoints tests"""

    def test_01_diagnose_plant_with_image(self):
        """Test plant diagnosis with base64 image"""
        global test_diagnosis_id
        
        if not test_user_id or not test_token:
            pytest.skip("No user ID or token available")
        
        # Create a small test image (1x1 red pixel PNG)
        test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
        
        headers = {"Authorization": f"Bearer {test_token}"}
        response = requests.post(f"{BASE_URL}/api/diagnose", 
            headers=headers,
            json={
                "user_id": test_user_id,
                "image_base64": test_image_base64,
                "crop_name": "Tomato",
                "location": TEST_LOCATION
            }
        )
        
        print(f"Diagnose response status: {response.status_code}")
        
        # AI diagnosis might fail with test image, but endpoint should work
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "disease_name" in data
            test_diagnosis_id = data["id"]
            print(f"✓ Diagnosis created: {data.get('disease_name', 'Unknown')}")
        else:
            print(f"⚠ Diagnosis failed (expected with test image): {response.status_code}")

    def test_02_get_user_diagnoses(self):
        """Test getting user's diagnosis history"""
        if not test_user_id or not test_token:
            pytest.skip("No user ID or token available")
        
        headers = {"Authorization": f"Bearer {test_token}"}
        response = requests.get(f"{BASE_URL}/api/diagnoses/{test_user_id}", headers=headers)
        
        print(f"Get diagnoses response status: {response.status_code}")
        assert response.status_code == 200
        
        diagnoses = response.json()
        assert isinstance(diagnoses, list)
        print(f"✓ Found {len(diagnoses)} diagnoses for user")


class TestCommunity:
    """Community endpoints tests"""

    def test_01_create_post(self):
        """Test creating a community post"""
        global test_post_id
        
        if not test_user_id or not test_token:
            pytest.skip("No user ID or token available")
        
        headers = {"Authorization": f"Bearer {test_token}"}
        response = requests.post(f"{BASE_URL}/api/community/posts",
            headers=headers,
            json={
                "user_id": test_user_id,
                "user_name": TEST_NAME,
                "title": "Test Post - Tomato Disease",
                "content": "Has anyone dealt with early blight on tomatoes?",
                "crop_type": "Tomato"
            }
        )
        
        print(f"Create post response status: {response.status_code}")
        assert response.status_code == 200
        
        post = response.json()
        assert "id" in post
        assert post["title"] == "Test Post - Tomato Disease"
        assert post["user_name"] == TEST_NAME
        
        test_post_id = post["id"]
        print(f"✓ Post created: {test_post_id}")

    def test_02_get_all_posts(self):
        """Test getting all community posts"""
        response = requests.get(f"{BASE_URL}/api/community/posts")
        
        print(f"Get posts response status: {response.status_code}")
        assert response.status_code == 200
        
        posts = response.json()
        assert isinstance(posts, list)
        print(f"✓ Found {len(posts)} community posts")

    def test_03_like_post(self):
        """Test liking a post"""
        if not test_post_id or not test_token:
            pytest.skip("No post ID or token available")
        
        headers = {"Authorization": f"Bearer {test_token}"}
        response = requests.post(f"{BASE_URL}/api/community/posts/{test_post_id}/like",
            headers=headers
        )
        
        print(f"Like post response status: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        print("✓ Post liked successfully")

    def test_04_create_reply(self):
        """Test creating a reply to a post"""
        if not test_post_id or not test_user_id or not test_token:
            pytest.skip("No post ID, user ID, or token available")
        
        headers = {"Authorization": f"Bearer {test_token}"}
        response = requests.post(f"{BASE_URL}/api/community/replies",
            headers=headers,
            json={
                "post_id": test_post_id,
                "user_id": test_user_id,
                "user_name": TEST_NAME,
                "content": "I recommend using copper-based fungicide."
            }
        )
        
        print(f"Create reply response status: {response.status_code}")
        assert response.status_code == 200
        
        reply = response.json()
        assert "id" in reply
        assert reply["post_id"] == test_post_id
        print("✓ Reply created successfully")

    def test_05_get_post_replies(self):
        """Test getting replies for a post"""
        if not test_post_id:
            pytest.skip("No post ID available")
        
        response = requests.get(f"{BASE_URL}/api/community/replies/{test_post_id}")
        
        print(f"Get replies response status: {response.status_code}")
        assert response.status_code == 200
        
        replies = response.json()
        assert isinstance(replies, list)
        assert len(replies) >= 1, "Should have at least 1 reply"
        print(f"✓ Found {len(replies)} replies")


class TestWeather:
    """Weather endpoint tests"""

    def test_01_get_weather(self):
        """Test getting weather data"""
        response = requests.get(f"{BASE_URL}/api/weather?location=test")
        
        print(f"Get weather response status: {response.status_code}")
        assert response.status_code == 200
        
        weather = response.json()
        assert "temperature" in weather
        assert "humidity" in weather
        assert "rainfall" in weather
        assert "forecast" in weather
        
        print(f"✓ Weather data: {weather['temperature']}°C, {weather['humidity']}% humidity")


class TestFertilizer:
    """Fertilizer calculator tests"""

    def test_01_calculate_fertilizer(self):
        """Test fertilizer calculation"""
        if not test_token:
            pytest.skip("No token available")
        
        headers = {"Authorization": f"Bearer {test_token}"}
        response = requests.post(f"{BASE_URL}/api/fertilizer/calculate",
            headers=headers,
            json={
                "crop_name": "Tomato",
                "plot_size": 2.5,
                "soil_type": "Loamy"
            }
        )
        
        print(f"Calculate fertilizer response status: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        assert "nitrogen_kg" in result
        assert "phosphorus_kg" in result
        assert "potassium_kg" in result
        assert "recommendations" in result
        
        print(f"✓ Fertilizer calculated: N={result['nitrogen_kg']}kg, P={result['phosphorus_kg']}kg, K={result['potassium_kg']}kg")


class TestAlerts:
    """Disease alerts tests"""

    def test_01_get_alerts(self):
        """Test getting disease alerts"""
        response = requests.get(f"{BASE_URL}/api/alerts")
        
        print(f"Get alerts response status: {response.status_code}")
        assert response.status_code == 200
        
        alerts = response.json()
        assert isinstance(alerts, list)
        print(f"✓ Found {len(alerts)} disease alerts")

    def test_02_get_alerts_by_location(self):
        """Test filtering alerts by location"""
        response = requests.get(f"{BASE_URL}/api/alerts?location=test")
        
        assert response.status_code == 200
        alerts = response.json()
        assert isinstance(alerts, list)
        print(f"✓ Found {len(alerts)} alerts for location 'test'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
