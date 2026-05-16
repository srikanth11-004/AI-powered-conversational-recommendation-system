# Deployment Guide - SHL Assessment Recommender

## ✅ Requirements Met

### 1. API with LLM/RAG ✅
- **LLM**: Gemini API for constraint extraction
- **RAG**: Semantic search with sentence-transformers
- **Clarify**: Asks questions when context insufficient
- **Recommend**: Returns 1-10 relevant assessments
- **Refine**: Updates constraints mid-conversation
- **Compare**: Compares assessments using catalog data
- **Grounded**: All URLs from catalog

### 2. Evaluation Methods ✅
- **Groundedness**: Verifies all URLs from catalog
- **Retrieval Quality**: Measures precision and keyword matching
- **Recommendation Relevance**: Scores constraint matching
- **Response Accuracy**: Validates behavior classification
- **Overall Score**: Composite metric (0-100%)

---

## Deployment Options

### Option 1: Render (Free, Recommended)

**Steps:**

1. **Create account**: https://render.com

2. **Create `render.yaml`** in project root:
```yaml
services:
  - type: web
    name: shl-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

3. **Push to GitHub**:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/shl-agent.git
git push -u origin main
```

4. **Deploy on Render**:
   - Go to Render dashboard
   - Click "New +" → "Web Service"
   - Connect GitHub repo
   - Add environment variable: `GEMINI_API_KEY`
   - Click "Create Web Service"

5. **Your URL**: `https://shl-agent-xxxx.onrender.com`

**Cold Start**: Yes (~30-60 seconds after inactivity on free tier)

---

### Option 2: Railway (Free Tier)

**Steps:**

1. **Create account**: https://railway.app

2. **Install Railway CLI**:
```bash
npm install -g @railway/cli
```

3. **Deploy**:
```bash
railway login
railway init
railway up
```

4. **Set environment variable**:
```bash
railway variables set GEMINI_API_KEY=your-key
```

5. **Get URL**: Railway provides public URL

**Cold Start**: Yes (~10-20 seconds)

---

### Option 3: Google Cloud Run (Recommended for Production)

**Steps:**

1. **Install gcloud CLI**: https://cloud.google.com/sdk/docs/install

2. **Build and deploy**:
```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/shl-agent

# Deploy
gcloud run deploy shl-agent \
  --image gcr.io/PROJECT_ID/shl-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your-key
```

3. **Your URL**: `https://shl-agent-xxxx-uc.a.run.app`

**Cold Start**: Yes (~5-10 seconds, configurable with min instances)

---

### Option 4: AWS Lambda + API Gateway

**Steps:**

1. **Install Serverless Framework**:
```bash
npm install -g serverless
```

2. **Create `serverless.yml`**:
```yaml
service: shl-agent

provider:
  name: aws
  runtime: python3.11
  environment:
    GEMINI_API_KEY: ${env:GEMINI_API_KEY}

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

3. **Create `lambda_handler.py`**:
```python
from mangum import Mangum
from main import app

handler = Mangum(app)
```

4. **Deploy**:
```bash
serverless deploy
```

**Cold Start**: Yes (~2-5 seconds)

---

## Quick Deploy (Render - Easiest)

### Step 1: Prepare Files

Create `render.yaml`:
```yaml
services:
  - type: web
    name: shl-agent
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

### Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "SHL Assessment Recommender"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shl-agent.git
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to https://render.com
2. Sign up / Log in
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render auto-detects `render.yaml`
6. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key
7. Click "Create Web Service"
8. Wait 3-5 minutes for deployment

### Step 4: Get Your URL

Render provides: `https://shl-agent-xxxx.onrender.com`

Test:
```bash
curl https://shl-agent-xxxx.onrender.com/health
```

---

## Testing Deployed API

### Health Check
```bash
curl https://your-url.com/health
```

Expected: `{"status":"ok"}`

### Chat Request
```bash
curl -X POST https://your-url.com/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Java developer, mid-level"}]}'
```

### Evaluation Endpoint
```bash
curl -X POST https://your-url.com/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "response": {"reply": "...", "recommendations": [...]},
    "constraints": {"role": "java"},
    "expected_behavior": "recommend",
    "expected_keywords": ["java"]
  }'
```

---

## Cold Start Information

### What is Cold Start?
When your service is inactive, the hosting provider may shut down the container to save resources. The next request will take longer as the container restarts.

### Cold Start Times:
- **Render (Free)**: 30-60 seconds
- **Railway (Free)**: 10-20 seconds
- **Google Cloud Run**: 5-10 seconds (configurable)
- **AWS Lambda**: 2-5 seconds

### How to Minimize:
1. **Paid tier**: Keep minimum instances running
2. **Ping service**: Set up cron job to ping `/health` every 5 minutes
3. **Optimize**: Reduce dependencies, use smaller base image

### For Assignment:
Answer: **Yes, deployed API has cold-start delay after inactivity (30-60 seconds on free tier)**

---

## Environment Variables

Required:
- `GEMINI_API_KEY`: Your Google Gemini API key

Optional:
- `PORT`: Server port (default: 8000, Render sets automatically)

---

## Monitoring

### Check Logs (Render):
```bash
# In Render dashboard
Services → Your Service → Logs
```

### Check Health:
```bash
curl https://your-url.com/health
```

### Run Evaluation:
```bash
# Point to your deployed URL
BASE_URL=https://your-url.com python test_with_evaluation.py
```

---

## Submission Checklist

- [ ] API deployed and accessible
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `POST /chat` works with test cases
- [ ] `POST /evaluate` endpoint available
- [ ] All URLs grounded in catalog
- [ ] Evaluation metrics implemented
- [ ] Cold start behavior documented
- [ ] Public URL provided

---

## Example Submission

**Public Base URL**: `https://shl-agent-xxxx.onrender.com`

**Cold Start**: Yes, approximately 30-60 seconds after inactivity on free tier

**Endpoints**:
- `GET /health` - Health check
- `POST /chat` - Conversational agent
- `POST /evaluate` - Evaluation metrics

**Features**:
- ✅ LLM-based constraint extraction (Gemini)
- ✅ RAG with semantic search (sentence-transformers)
- ✅ Clarification, recommendation, refinement, comparison
- ✅ Groundedness verification (100% catalog URLs)
- ✅ Evaluation metrics (precision, relevance, accuracy)

---

## Troubleshooting

### Deployment fails
- Check `requirements.txt` has all dependencies
- Verify `GEMINI_API_KEY` is set
- Check logs for errors

### Cold start too slow
- Upgrade to paid tier
- Set up keep-alive ping
- Optimize Docker image

### API returns 500
- Check logs for errors
- Verify catalog file exists
- Test locally first

---

## Next Steps

1. Deploy to Render (easiest)
2. Test all endpoints
3. Run evaluation suite
4. Submit public URL
5. Document cold start behavior

**Your solution is complete and ready for deployment!** 🚀
