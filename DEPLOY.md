# 🚀 Quick Deployment Guide

## ✅ Clean Project Structure (16 files)

### Core (4 files)
- `main.py` - FastAPI server
- `evaluation.py` - Metrics
- `shl_product_catalog.json` - Catalog
- `requirements.txt` - Dependencies

### Documentation (3 files)
- `README.md` - Main documentation
- `DEPLOYMENT.md` - Deployment instructions
- `DOCUMENTATION.md` - Technical details
- `ARCHITECTURE.md` - System design

### Testing (2 files)
- `test_api.py` - Basic tests
- `test_with_evaluation.py` - Comprehensive tests

### Deployment (3 files)
- `Dockerfile`
- `docker-compose.yml`
- `start.bat`

### Config (3 files)
- `.gitignore`
- `.env.example`
- `.env` (not committed)

---

## 📤 Push to GitHub

```bash
# Initialize
git init
git add .
git commit -m "SHL Assessment Recommender"

# Push
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shl-agent.git
git push -u origin main
```

---

## 🌐 Deploy to Render

1. Go to https://render.com
2. New Web Service → Connect GitHub repo
3. Add environment variable: `GEMINI_API_KEY=your-key`
4. Deploy

**Your URL**: `https://shl-agent-xxxx.onrender.com`

---

## ✅ Assignment Submission

**Public URL**: `https://shl-agent-xxxx.onrender.com`

**Cold Start**: Yes, ~30-60 seconds on free tier

**Requirements Met**:
- ✅ LLM/RAG API (Gemini + semantic search)
- ✅ Evaluation metrics (groundedness, relevance, accuracy)
- ✅ All behaviors working (clarify, recommend, refine, compare)

---

**Done!** 🎉
