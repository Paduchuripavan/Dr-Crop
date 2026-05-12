# Dr Crop - Product Requirements Document

## Overview
Dr Crop is an AI-powered plant disease detection mobile application (similar to Plantix) that helps farmers diagnose crop diseases, get treatment recommendations, and access agricultural knowledge.

## Tech Stack
- **Frontend**: Expo (React Native) with file-based routing (expo-router)
- **Backend**: FastAPI with Python
- **Database**: MongoDB
- **AI**: Google Gemini 2.5 Pro via Emergent LLM Key for plant disease detection

## Core Features

### 1. User Authentication
- Email/password registration and login
- JWT-based authentication
- User profile with location tracking

### 2. AI-Powered Disease Detection
- Camera capture or gallery image selection
- Gemini Vision AI analyzes plant images
- Returns: disease name, confidence, symptoms, causes, treatment, prevention, severity
- Diagnosis history stored per user

### 3. Crop Library
- 8 major crops: Tomato, Potato, Wheat, Rice, Corn, Cotton, Pepper, Grape
- Scientific names, descriptions, and growing tips
- Expandable to 30+ crops

### 4. Disease Database
- 5 seeded diseases: Early Blight, Late Blight, Powdery Mildew, Bacterial Leaf Spot, Stem Rust
- Symptoms, causes, treatment, prevention, severity levels

### 5. Farmer Community Forum
- Create posts with crop types
- Like and reply to posts
- Expert community support

### 6. Weather & Farming Conditions
- Temperature, humidity, rainfall data (MOCKED)
- Spraying and harvesting recommendations

### 7. Fertilizer Calculator
- NPK calculation based on crop type and plot size
- Soil type consideration
- Application guide recommendations

### 8. Disease Alerts
- Alert system for disease outbreaks by location

### 9. User Profile
- Scan history and statistics
- Account management
- Logout functionality

## Navigation Structure
- **Home** - Dashboard with quick actions, weather, alerts
- **Detect** - Camera/gallery → AI analysis → results
- **Community** - Forum with posts and replies
- **Crops** - Crop library with details
- **Profile** - User stats, history, settings

## API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/crops` - List all crops
- `GET /api/crops/:id` - Get crop details
- `GET /api/diseases` - List diseases (filter by crop)
- `POST /api/diagnose` - AI plant diagnosis
- `GET /api/diagnoses/:userId` - User diagnosis history
- `POST /api/community/posts` - Create community post
- `GET /api/community/posts` - List community posts
- `POST /api/community/posts/:id/like` - Like a post
- `POST /api/community/replies` - Add reply
- `GET /api/community/replies/:postId` - Get replies
- `GET /api/weather` - Weather data (MOCKED)
- `POST /api/fertilizer/calculate` - Fertilizer calculation
- `GET /api/alerts` - Disease alerts

### 10. Multi-Language Support
- 3 languages: English, Hindi (हिन्दी), Telugu (తెలుగు)
- Language selector on login screen (🌐 button) and profile settings
- All UI labels, buttons, headers translated
- Language preference persisted in AsyncStorage
- LanguageContext provides `t()` function for translations

## Notes
- Weather API is MOCKED with random data
- AI diagnosis uses Emergent LLM Key for Gemini 2.5 Pro
- Images are handled as base64 for mobile compatibility
