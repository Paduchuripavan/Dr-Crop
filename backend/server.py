from fastapi import FastAPI, APIRouter, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent
import jwt
import base64
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============ MODELS ============

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    location: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Crop(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    scientific_name: str
    description: str
    icon: str  # emoji or icon name
    growing_tips: str

class Disease(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    crop_name: str
    symptoms: str
    causes: str
    treatment: str
    prevention: str
    severity: str  # low, medium, high
    image_url: Optional[str] = None

class DiagnosisRequest(BaseModel):
    user_id: str
    crop_name: Optional[str] = None
    image_base64: str
    location: Optional[str] = None

class Diagnosis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    crop_name: Optional[str] = None
    image_base64: str
    diagnosis_text: str
    disease_name: Optional[str] = None
    confidence: Optional[str] = None
    treatment: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CommunityPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    title: str
    content: str
    crop_type: Optional[str] = None
    images: List[str] = []
    likes: int = 0
    replies_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityPostCreate(BaseModel):
    user_id: str
    user_name: str
    title: str
    content: str
    crop_type: Optional[str] = None
    images: List[str] = []

class Reply(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    user_name: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReplyCreate(BaseModel):
    post_id: str
    user_id: str
    user_name: str
    content: str

class DiseaseAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    disease_name: str
    crop_name: str
    location: str
    severity: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FertilizerCalculation(BaseModel):
    crop_name: str
    plot_size: float  # in acres
    soil_type: str

# ============ HELPER FUNCTIONS ============

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def analyze_plant_image(image_base64: str, crop_name: Optional[str] = None) -> dict:
    """Analyze plant image using Gemini Vision API"""
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment")
        
        # Create chat instance
        chat = LlmChat(
            api_key=api_key,
            session_id=str(uuid.uuid4()),
            system_message="""You are an expert agricultural pathologist specializing in plant disease diagnosis. 
            Analyze the provided plant image and identify any diseases, pests, or nutrient deficiencies.
            Provide your response in the following format:
            
            DISEASE: [Name of disease/pest/deficiency or "Healthy" if no issues]
            CONFIDENCE: [High/Medium/Low]
            CROP: [Type of crop if identifiable]
            SYMPTOMS: [Detailed description of visible symptoms]
            CAUSES: [What causes this condition]
            TREATMENT: [Recommended treatment steps, be specific and practical]
            PREVENTION: [How to prevent this in future]
            SEVERITY: [Low/Medium/High]
            
            Be thorough, accurate, and provide actionable advice for farmers."""
        ).with_model("gemini", "gemini-2.5-pro")
        
        # Create image content
        image_content = ImageContent(image_base64=image_base64)
        
        # Create message
        crop_context = f" The farmer says this is a {crop_name} plant." if crop_name else ""
        message = UserMessage(
            text=f"Please analyze this plant image for any diseases, pests, or problems.{crop_context}",
            file_contents=[image_content]
        )
        
        # Get response
        response = await chat.send_message(message)
        
        # Parse response
        lines = response.strip().split('\n')
        result = {
            'disease_name': 'Unknown',
            'confidence': 'Medium',
            'crop': crop_name or 'Unknown',
            'symptoms': '',
            'causes': '',
            'treatment': '',
            'prevention': '',
            'severity': 'Medium',
            'full_response': response
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('DISEASE:'):
                result['disease_name'] = line.replace('DISEASE:', '').strip()
            elif line.startswith('CONFIDENCE:'):
                result['confidence'] = line.replace('CONFIDENCE:', '').strip()
            elif line.startswith('CROP:'):
                result['crop'] = line.replace('CROP:', '').strip()
            elif line.startswith('SYMPTOMS:'):
                result['symptoms'] = line.replace('SYMPTOMS:', '').strip()
            elif line.startswith('CAUSES:'):
                result['causes'] = line.replace('CAUSES:', '').strip()
            elif line.startswith('TREATMENT:'):
                result['treatment'] = line.replace('TREATMENT:', '').strip()
            elif line.startswith('PREVENTION:'):
                result['prevention'] = line.replace('PREVENTION:', '').strip()
            elif line.startswith('SEVERITY:'):
                result['severity'] = line.replace('SEVERITY:', '').strip()
        
        return result
        
    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing image: {str(e)}")

# ============ SEED DATA ============

async def seed_crops():
    """Seed initial crop data"""
    count = await db.crops.count_documents({})
    if count > 0:
        return
    
    crops_data = [
        {"name": "Tomato", "scientific_name": "Solanum lycopersicum", "icon": "🍅", 
         "description": "Popular vegetable crop rich in vitamins", 
         "growing_tips": "Requires well-drained soil, regular watering, and full sunlight. Plant after last frost."},
        {"name": "Potato", "scientific_name": "Solanum tuberosum", "icon": "🥔",
         "description": "Starchy tuber crop widely cultivated worldwide",
         "growing_tips": "Grows best in cool weather, loose soil. Hill soil around plants as they grow."},
        {"name": "Wheat", "scientific_name": "Triticum aestivum", "icon": "🌾",
         "description": "Major cereal grain crop",
         "growing_tips": "Sow in well-prepared seedbed. Requires moderate water and fertilizer."},
        {"name": "Rice", "scientific_name": "Oryza sativa", "icon": "🌾",
         "description": "Staple food crop for half the world",
         "growing_tips": "Requires flooded conditions during growth. Transplant seedlings in rows."},
        {"name": "Corn", "scientific_name": "Zea mays", "icon": "🌽",
         "description": "Versatile grain crop",
         "growing_tips": "Plant in blocks for better pollination. Needs full sun and rich soil."},
        {"name": "Cotton", "scientific_name": "Gossypium", "icon": "☁️",
         "description": "Major fiber crop",
         "growing_tips": "Requires warm climate, well-drained soil, and pest management."},
        {"name": "Pepper", "scientific_name": "Capsicum annuum", "icon": "🌶️",
         "description": "Spicy vegetable crop",
         "growing_tips": "Needs warm soil, full sun. Water regularly but don't overwater."},
        {"name": "Grape", "scientific_name": "Vitis vinifera", "icon": "🍇",
         "description": "Fruit crop for wine and fresh consumption",
         "growing_tips": "Requires trellising, pruning, and good air circulation."},
    ]
    
    for crop_data in crops_data:
        crop = Crop(id=str(uuid.uuid4()), **crop_data)
        await db.crops.insert_one(crop.dict())

async def seed_diseases():
    """Seed common plant diseases"""
    count = await db.diseases.count_documents({})
    if count > 0:
        return
    
    diseases_data = [
        {
            "name": "Early Blight",
            "crop_name": "Tomato",
            "symptoms": "Dark brown spots with concentric rings on older leaves, yellowing around spots",
            "causes": "Fungus Alternaria solani, warm humid weather, poor air circulation",
            "treatment": "Remove infected leaves, apply fungicide (copper-based or chlorothalonil), improve air circulation",
            "prevention": "Crop rotation, mulching, avoid overhead watering, resistant varieties",
            "severity": "Medium"
        },
        {
            "name": "Late Blight",
            "crop_name": "Potato",
            "symptoms": "Water-soaked spots on leaves, white fungal growth on undersides, rapid plant death",
            "causes": "Phytophthora infestans fungus, cool wet weather",
            "treatment": "Apply fungicides immediately (metalaxyl, mancozeb), destroy infected plants",
            "prevention": "Use certified disease-free seeds, good drainage, fungicide protection in wet weather",
            "severity": "High"
        },
        {
            "name": "Powdery Mildew",
            "crop_name": "Grape",
            "symptoms": "White powdery coating on leaves and fruits, stunted growth",
            "causes": "Various fungal species, high humidity, poor air flow",
            "treatment": "Sulfur-based fungicides, neem oil, potassium bicarbonate spray",
            "prevention": "Prune for air circulation, avoid overhead watering, resistant varieties",
            "severity": "Medium"
        },
        {
            "name": "Bacterial Leaf Spot",
            "crop_name": "Pepper",
            "symptoms": "Small brown spots with yellow halos on leaves, leaf drop",
            "causes": "Xanthomonas bacteria, wet conditions, plant wounds",
            "treatment": "Copper-based bactericides, remove infected plants, improve drainage",
            "prevention": "Use disease-free seeds, avoid working with wet plants, crop rotation",
            "severity": "Medium"
        },
        {
            "name": "Stem Rust",
            "crop_name": "Wheat",
            "symptoms": "Reddish-brown pustules on stems and leaves, weakened stalks",
            "causes": "Puccinia graminis fungus, moderate temperatures, moisture",
            "treatment": "Fungicide application (triazoles), plant resistant varieties",
            "prevention": "Use resistant varieties, timely planting, remove volunteer plants",
            "severity": "High"
        },
    ]
    
    for disease_data in diseases_data:
        disease = Disease(id=str(uuid.uuid4()), **disease_data)
        await db.diseases.insert_one(disease.dict())

# ============ AUTH ROUTES ============

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        location=user_data.location
    )
    user_dict = user.dict()
    user_dict['password'] = get_password_hash(user_data.password)
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token({"sub": user.email, "user_id": user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.dict()
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user.get('password', '')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": user['email'], "user_id": user['id']})
    
    user_obj = User(**{k: v for k, v in user.items() if k != 'password'})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_obj.dict()
    }

# ============ CROP ROUTES ============

@api_router.get("/crops", response_model=List[Crop])
async def get_crops():
    crops = await db.crops.find().to_list(1000)
    return [Crop(**crop) for crop in crops]

@api_router.get("/crops/{crop_id}", response_model=Crop)
async def get_crop(crop_id: str):
    crop = await db.crops.find_one({"id": crop_id})
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    return Crop(**crop)

# ============ DISEASE ROUTES ============

@api_router.get("/diseases", response_model=List[Disease])
async def get_diseases(crop_name: Optional[str] = None):
    query = {}
    if crop_name:
        query["crop_name"] = crop_name
    diseases = await db.diseases.find(query).to_list(1000)
    return [Disease(**disease) for disease in diseases]

@api_router.get("/diseases/{disease_id}", response_model=Disease)
async def get_disease(disease_id: str):
    disease = await db.diseases.find_one({"id": disease_id})
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return Disease(**disease)

# ============ DIAGNOSIS ROUTES ============

@api_router.post("/diagnose", response_model=Diagnosis)
async def diagnose_plant(request: DiagnosisRequest):
    try:
        # Analyze image using AI
        analysis = await analyze_plant_image(request.image_base64, request.crop_name)
        
        # Create diagnosis record
        diagnosis = Diagnosis(
            user_id=request.user_id,
            crop_name=analysis['crop'],
            image_base64=request.image_base64,
            diagnosis_text=analysis['full_response'],
            disease_name=analysis['disease_name'],
            confidence=analysis['confidence'],
            treatment=analysis['treatment']
        )
        
        await db.diagnoses.insert_one(diagnosis.dict())
        
        return diagnosis
    except Exception as e:
        logging.error(f"Diagnosis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/diagnoses/{user_id}", response_model=List[Diagnosis])
async def get_user_diagnoses(user_id: str):
    diagnoses = await db.diagnoses.find({"user_id": user_id}).sort("timestamp", -1).to_list(100)
    # Don't return full image in list
    for d in diagnoses:
        if 'image_base64' in d and len(d['image_base64']) > 100:
            d['image_base64'] = d['image_base64'][:100] + "..."
    return [Diagnosis(**d) for d in diagnoses]

@api_router.get("/diagnosis/{diagnosis_id}", response_model=Diagnosis)
async def get_diagnosis(diagnosis_id: str):
    diagnosis = await db.diagnoses.find_one({"id": diagnosis_id})
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")
    return Diagnosis(**diagnosis)

# ============ COMMUNITY ROUTES ============

@api_router.post("/community/posts", response_model=CommunityPost)
async def create_post(post: CommunityPostCreate):
    community_post = CommunityPost(**post.dict())
    await db.community_posts.insert_one(community_post.dict())
    return community_post

@api_router.get("/community/posts", response_model=List[CommunityPost])
async def get_posts(crop_type: Optional[str] = None, limit: int = 50):
    query = {}
    if crop_type:
        query["crop_type"] = crop_type
    posts = await db.community_posts.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    return [CommunityPost(**post) for post in posts]

@api_router.post("/community/posts/{post_id}/like")
async def like_post(post_id: str):
    result = await db.community_posts.update_one(
        {"id": post_id},
        {"$inc": {"likes": 1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"success": True}

@api_router.post("/community/replies", response_model=Reply)
async def create_reply(reply: ReplyCreate):
    reply_obj = Reply(**reply.dict())
    await db.replies.insert_one(reply_obj.dict())
    
    # Increment reply count
    await db.community_posts.update_one(
        {"id": reply.post_id},
        {"$inc": {"replies_count": 1}}
    )
    
    return reply_obj

@api_router.get("/community/replies/{post_id}", response_model=List[Reply])
async def get_replies(post_id: str):
    replies = await db.replies.find({"post_id": post_id}).sort("created_at", 1).to_list(1000)
    return [Reply(**reply) for reply in replies]

# ============ DISEASE ALERTS ============

@api_router.get("/alerts", response_model=List[DiseaseAlert])
async def get_alerts(location: Optional[str] = None):
    query = {}
    if location:
        query["location"] = location
    alerts = await db.disease_alerts.find(query).sort("created_at", -1).limit(20).to_list(20)
    return [DiseaseAlert(**alert) for alert in alerts]

# ============ FERTILIZER CALCULATOR ============

@api_router.post("/fertilizer/calculate")
async def calculate_fertilizer(calc: FertilizerCalculation):
    # Simple fertilizer calculation based on crop and plot size
    fertilizer_rates = {
        "Tomato": {"N": 120, "P": 60, "K": 60},
        "Potato": {"N": 100, "P": 50, "K": 100},
        "Wheat": {"N": 120, "P": 60, "K": 40},
        "Rice": {"N": 100, "P": 50, "K": 50},
        "Corn": {"N": 150, "P": 60, "K": 60},
        "Cotton": {"N": 120, "P": 60, "K": 60},
        "Pepper": {"N": 100, "P": 50, "K": 50},
        "Grape": {"N": 80, "P": 40, "K": 80},
    }
    
    rates = fertilizer_rates.get(calc.crop_name, {"N": 100, "P": 50, "K": 50})
    
    # Calculate per acre, then multiply by plot size
    nitrogen = rates["N"] * calc.plot_size
    phosphorus = rates["P"] * calc.plot_size
    potassium = rates["K"] * calc.plot_size
    
    return {
        "crop": calc.crop_name,
        "plot_size": calc.plot_size,
        "nitrogen_kg": round(nitrogen, 2),
        "phosphorus_kg": round(phosphorus, 2),
        "potassium_kg": round(potassium, 2),
        "recommendations": f"For {calc.plot_size} acres of {calc.crop_name}, apply {nitrogen}kg Nitrogen, {phosphorus}kg Phosphorus, and {potassium}kg Potassium. Split application: 50% at planting, 25% at vegetative stage, 25% at flowering."
    }

# ============ WEATHER (Mock) ============

@api_router.get("/weather")
async def get_weather(location: str = "default"):
    # Mock weather data
    return {
        "location": location,
        "temperature": random.randint(20, 35),
        "humidity": random.randint(40, 80),
        "rainfall": random.randint(0, 10),
        "forecast": "Partly cloudy",
        "best_for_spraying": random.choice([True, False]),
        "best_for_harvesting": random.choice([True, False])
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await seed_crops()
    await seed_diseases()
    logger.info("Database seeded successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
