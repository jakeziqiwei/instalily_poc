# PartSelect Agent - AI-Powered Appliance Parts Assistant

An intelligent chatbot system for appliance parts search, troubleshooting, and order management, specializing in dishwashers and refrigerators. 

Frontend - ReactJS, MaterialUI
Backend - FastAPI, DeepSeek AI, VectorDB, Selenium, etc

## Features

### **Intelligent Search**
- able to find parts by description, symptoms or natural languages in addition to part numbers
- includes parts, repair guides, and articles 
- also checks if anypart is compatible with each other


### **Advanced Troubleshooting**
- troubleshooting by combing knowledge from repairs, parts, and knowledge base 
- can give step by step guide
- gives videos and resource guide 

### **Order Management**
- supports cancel, return, and place orders
- also gives policies for the company


### Quick Setup

1. **Clone and Setup Environment**
```bash
git clone <repository-url>
cd instaslily_demo

# Set environment variables
export WEAVIATE_URL="your_weaviate_cluster_url"
export WEAVIATE_API_KEY="your_weaviate_api_key" 
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

2. **Start Backend**
```bash
cd backend
pip install -r requirements.txt
fastapi dev main.py
```
Backend runs at [http://localhost:8000](http://localhost:8000)

3. **Start Frontend**
```bash
cd case-study
npm install
npm start
```
Frontend opens at [http://localhost:3000](http://localhost:3000)


