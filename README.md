# 🤖 SHL Assessment Recommender

A conversational AI agent that helps hiring managers select appropriate SHL assessments through natural dialogue. Built with FastAPI, Gemini API, and semantic search.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🎯 **Intelligent Clarification** - Asks targeted questions when context is insufficient
- 🔍 **Semantic Recommendations** - Returns 1-10 relevant assessments using RAG
- 🔄 **Mid-Conversation Refinement** - Updates recommendations without restarting
- ⚖️ **Assessment Comparison** - Explains differences using catalog data
- 🛡️ **Scope Enforcement** - Rejects off-topic queries (legal advice, etc.)
- 📊 **Evaluation Metrics** - Measures groundedness, relevance, and accuracy

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/shl-agent.git
cd shl-agent

# Install dependencies
pip install -r requirements.txt

# Set API key
echo "GEMINI_API_KEY=your-key-here" > .env

# Start server
uvicorn main:app --port 8000
```

### Test

```bash
# Health check
curl http://localhost:8000/health

# Chat request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Java developer, mid-level"}]}'
```

## 📖 Documentation

- **[QUICKSTART_GEMINI.md](QUICKSTART_GEMINI.md)** - 5-minute setup guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to Render, Railway, GCP, AWS
- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Technical deep-dive
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture diagrams
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - File organization

## 🎯 API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### `POST /chat`
Conversational agent endpoint.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Java developer, mid-level, coding tests"}
  ]
}
```

**Response:**
```json
{
  "reply": "Here are 5 SHL assessments for Java developer:",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/products/product-catalog/view/java-8-new/",
      "test_type": "K"
    }
  ],
  "end_of_conversation": false
}
```

### `POST /evaluate`
Evaluation metrics endpoint.

**Request:**
```json
{
  "response": {"reply": "...", "recommendations": [...]},
  "constraints": {"role": "java", "seniority": "mid"},
  "expected_behavior": "recommend",
  "expected_keywords": ["java"]
}
```

**Response:**
```json
{
  "overall_score": 0.95,
  "groundedness": {"grounded": true, "grounded_percentage": 100.0},
  "retrieval_quality": {"precision": 0.9, "avg_relevance_score": 0.85},
  "recommendation_relevance": {"relevance_score": 0.92},
  "response_accuracy": {"correct_behavior": true, "within_limits": true}
}
```

## 🧪 Testing

### Basic Tests
```bash
python test_api.py
```

### Comprehensive Tests with Evaluation
```bash
python test_with_evaluation.py
```

**Output:**
```
✅ PASS | Clarify              | Score: 100.0%
✅ PASS | Recommend Java       | Score: 95.2%
✅ PASS | Recommend Python     | Score: 93.8%
✅ PASS | Refine               | Score: 94.5%
✅ PASS | Compare              | Score: 100.0%
✅ PASS | Reject               | Score: 100.0%

Total: 6/6 passed (100.0%)
Average Score: 97.3%
```

## 🏗️ Architecture

```
User Query
    ↓
Gemini API (Constraint Extraction)
    ↓
Intent Classification (clarify/recommend/refine/compare/reject)
    ↓
Semantic Search (sentence-transformers + cosine similarity)
    ↓
Filter (test type, seniority, job level)
    ↓
Return 1-10 Assessments (grounded in catalog)
```

**Tech Stack:**
- **API**: FastAPI
- **LLM**: Google Gemini
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Search**: Cosine similarity
- **Data**: 1000+ SHL assessments

## 📊 Evaluation Metrics

The system includes comprehensive evaluation:

1. **Groundedness** - Verifies all URLs from catalog (0% hallucination)
2. **Retrieval Quality** - Measures precision and keyword matching
3. **Recommendation Relevance** - Scores constraint matching
4. **Response Accuracy** - Validates behavior classification

## 🌐 Deployment

### Render (Easiest)

```bash
# Push to GitHub
git push origin main

# Deploy on Render
# 1. Go to render.com
# 2. Connect GitHub repo
# 3. Add GEMINI_API_KEY
# 4. Deploy
```

**Your URL**: `https://shl-agent-xxxx.onrender.com`

See [DEPLOYMENT.md](DEPLOYMENT.md) for Railway, GCP, AWS options.

## 📝 Example Conversations

### Vague → Clarification
```
User: "I need an assessment"
Agent: "To recommend the right assessments, could you tell me more about: role or skills, assessment type?"
```

### Direct → Recommendations
```
User: "Java developer, mid-level, coding tests"
Agent: "Here are 5 SHL assessments for Java developer:"
  - Java 8 (New)
  - Core Java (Advanced Level)
  - Automata (New)
  ...
```

### Refinement
```
User: "Actually, add personality tests"
Agent: "Here are 7 assessments for Java developer:"
  - Java 8 (New) [Technical]
  - OPQ32 [Personality]
  ...
```

### Comparison
```
User: "What's the difference between OPQ and GSA?"
Agent: "Comparing OPQ32 and Global Skills Assessment:
  OPQ measures personality traits...
  GSA measures 96 discrete skills..."
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `PORT` | No | Server port (default: 8000) |

### Test Types

- **K** = Knowledge & Skills
- **P** = Personality & Behavior
- **A** = Ability & Aptitude
- **S** = Simulations
- **C** = Competencies

## 📦 Project Structure

```
SHL_Chat_Agent/
├── main.py                    # FastAPI server + agent logic
├── evaluation.py              # Evaluation metrics
├── shl_product_catalog.json   # Assessment catalog
├── test_api.py               # Basic tests
├── test_with_evaluation.py   # Comprehensive tests
├── requirements.txt          # Dependencies
├── Dockerfile                # Container definition
└── docs/                     # Documentation
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SHL** for the comprehensive assessment catalog
- **Google** for Gemini API
- **Hugging Face** for sentence-transformers
- **FastAPI** for the excellent web framework

## 📞 Support

- **Documentation**: See [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/shl-agent/issues)
- **Email**: your-email@example.com

---

**Built with ❤️ for SHL Assessment Selection**
