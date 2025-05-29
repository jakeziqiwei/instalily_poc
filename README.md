# PartSelect Agent - AI-Powered Appliance Parts Assistant

An intelligent chatbot system for appliance parts search, troubleshooting, and order management, specializing in dishwashers and refrigerators. 

Frontend - ReactJS, MaterialUI
Backend - FastAPI, DeepSeek AI, VectorDB, Selenium, etc

## Design Decisions 

I  want to explain my design decisions here. 

- For the frontend, it was an easy decision to use materialUI since it provides a sleek ui for the interface 

- For the backend, I thought it was best to have two seperate databases. The first one is vectorDB via Weaviate which will store a lot of information on the items, blogs, and guides. Since we need to query with semantics, I thought it would be better to store these in the vectorDB. For orders/transactions, since its just a relational schema and most of the time, I will just be querying by the transactionID so I used a sqliteDB. In addition, for the future, I would implement a login system so I can even query by (transactionsID, UserID)

- I also wanted to try building my own agents so I can take this at least as a chance for learning something that I had no experiences in. I learned a lot, thank you for htis oppertunity.

- Also I read anthropic's paper on MCP and I wanted to try to implement it, but I didn't have time and knowledge. 




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


