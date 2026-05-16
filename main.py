import json
import os
from typing import List, Dict, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv
from evaluation import Evaluator

# Load environment variables
load_dotenv()

app = FastAPI()

# Load catalog
with open("shl_product_catalog.json", "r", encoding="utf-8") as f:
    CATALOG = json.load(f)

# Initialize models
embedder = SentenceTransformer('all-MiniLM-L6-v2')
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')
evaluator = Evaluator()

# Precompute embeddings
catalog_texts = [f"{item['name']} {item['description']} {' '.join(item.get('keys', []))}" for item in CATALOG]
catalog_embeddings = embedder.encode(catalog_texts)

# Request/Response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class Recommendation(BaseModel):
    name: str
    url: str
    test_type: str

class ChatResponse(BaseModel):
    reply: str
    recommendations: List[Recommendation]
    end_of_conversation: bool

def fallback_extract_constraints(messages: List[Message]) -> Dict:
    """Fallback: Simple keyword-based constraint extraction"""
    text = " ".join([m.content.lower() for m in messages])
    
    constraints = {
        "role": None,
        "skills": [],
        "seniority": None,
        "test_types": []
    }
    
    # Extract role - expanded list
    role_keywords = {
        "java": ["java"],
        "python": ["python"],
        "javascript": ["javascript", "js", "node"],
        "developer": ["developer", "programmer", "engineer"],
        "data scientist": ["data scientist", "data science"],
        "customer service": ["customer service", "customer support"],
        "sales": ["sales", "salesperson"],
        "manager": ["manager", "management"],
        "accountant": ["accountant", "accounting"],
        "hr": ["hr", "human resources"]
    }
    
    for role, keywords in role_keywords.items():
        if any(kw in text for kw in keywords):
            constraints["role"] = role
            break
    
    # Extract seniority
    if any(word in text for word in ["entry", "junior", "graduate", "entry-level"]):
        constraints["seniority"] = "entry"
    elif any(word in text for word in ["mid", "intermediate", "4 years", "3 years", "5 years"]):
        constraints["seniority"] = "mid"
    elif any(word in text for word in ["senior", "lead", "principal", "executive", "director"]):
        constraints["seniority"] = "senior"
    
    # Extract skills
    skill_keywords = ["coding", "programming", "communication", "leadership", "stakeholder", "technical"]
    constraints["skills"] = [skill for skill in skill_keywords if skill in text]
    
    # Extract test types
    if any(word in text for word in ["coding", "technical", "programming", "knowledge", "skills"]):
        constraints["test_types"].append("Knowledge & Skills")
    if any(word in text for word in ["personality", "behavior", "culture", "opq"]):
        constraints["test_types"].append("Personality & Behavior")
    if any(word in text for word in ["cognitive", "ability", "aptitude", "reasoning"]):
        constraints["test_types"].append("Ability & Aptitude")
    if any(word in text for word in ["simulation", "practical", "hands-on"]):
        constraints["test_types"].append("Simulations")
    
    print(f"Fallback extracted constraints: {constraints}")
    return constraints

def extract_constraints(messages: List[Message]) -> Dict:
    """Extract hiring constraints from conversation history using LLM"""
    conversation = "\n".join([f"{m.role}: {m.content}" for m in messages])
    
    prompt = f"""Extract hiring requirements from this conversation. Return ONLY valid JSON.

Conversation:
{conversation}

Extract:
- role: job title (e.g., "Java developer", "Customer service")
- skills: list of skills mentioned (e.g., ["coding", "communication"])
- seniority: level (e.g., "entry", "mid", "senior")
- test_types: types of assessments (e.g., ["Knowledge & Skills", "Personality & Behavior"])

Return ONLY this JSON format (no markdown, no explanation):
{{"role": "...", "skills": [...], "seniority": "...", "test_types": [...]}}

If something is not mentioned, use null."""

    try:
        response = model.generate_content(prompt)
        # Clean response - remove markdown code blocks if present
        content = response.text.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        constraints = json.loads(content)
        print(f"Extracted constraints: {constraints}")  # Debug log
        return constraints
    except Exception as e:
        print(f"Error extracting constraints: {e}")
        # Fallback: simple keyword extraction
        return fallback_extract_constraints(messages)

def classify_intent(messages: List[Message], constraints: Dict) -> str:
    """Classify user intent: clarify, recommend, refine, compare, reject"""
    last_msg = messages[-1].content.lower()
    
    print(f"Classifying intent. Last message: {last_msg[:100]}")  # Debug
    print(f"Constraints: {constraints}")  # Debug
    
    # Check for comparison
    if any(word in last_msg for word in ["difference", "compare", "vs", "versus"]):
        return "compare"
    
    # Check for refinement
    if len(messages) > 1 and any(word in last_msg for word in ["actually", "also", "add", "change", "instead"]):
        return "refine"
    
    # Check if enough info to recommend
    has_role = constraints.get("role") and constraints.get("role") != "null"
    has_skills = constraints.get("skills") and len(constraints.get("skills", [])) > 0
    
    if has_role or has_skills:
        print(f"Intent: recommend (has_role={has_role}, has_skills={has_skills})")  # Debug
        return "recommend"
    
    # Check for off-topic
    if any(word in last_msg for word in ["legal", "advice", "law", "compliance", "ignore", "system"]):
        return "reject"
    
    print("Intent: clarify")  # Debug
    return "clarify"

def semantic_search(query: str, constraints: Dict, top_k: int = 10) -> List[Dict]:
    """Search catalog using semantic similarity + filtering"""
    query_embedding = embedder.encode([query])[0]
    similarities = cosine_similarity([query_embedding], catalog_embeddings)[0]
    
    # Get top candidates
    top_indices = np.argsort(similarities)[::-1][:50]
    
    results = []
    for idx in top_indices:
        item = CATALOG[idx]
        score = similarities[idx]
        
        # Apply filters
        if constraints.get("test_types"):
            if not any(tt in item.get("keys", []) for tt in constraints["test_types"]):
                continue
        
        if constraints.get("seniority"):
            seniority_map = {
                "entry": ["Entry-Level", "Graduate"],
                "mid": ["Mid-Professional", "Professional Individual Contributor"],
                "senior": ["Manager", "Director", "Executive"]
            }
            seniority_key = next((k for k in seniority_map if k in constraints["seniority"].lower()), None)
            if seniority_key:
                if not any(level in item.get("job_levels", []) for level in seniority_map[seniority_key]):
                    continue
        
        results.append({"item": item, "score": score})
        if len(results) >= top_k:
            break
    
    return results

def compare_assessments(names: List[str]) -> str:
    """Compare specific assessments by name"""
    found = []
    for name in names:
        for item in CATALOG:
            if name.lower() in item["name"].lower():
                found.append(item)
                break
    
    if len(found) < 2:
        return "I couldn't find both assessments in the catalog. Please provide exact names."
    
    comparison = f"Comparing {found[0]['name']} and {found[1]['name']}:\n\n"
    comparison += f"**{found[0]['name']}**: {found[0]['description']}\n"
    comparison += f"Type: {', '.join(found[0].get('keys', []))}\n"
    comparison += f"Duration: {found[0].get('duration', 'N/A')}\n\n"
    comparison += f"**{found[1]['name']}**: {found[1]['description']}\n"
    comparison += f"Type: {', '.join(found[1].get('keys', []))}\n"
    comparison += f"Duration: {found[1].get('duration', 'N/A')}\n"
    
    return comparison

def generate_response(messages: List[Message], intent: str, constraints: Dict) -> ChatResponse:
    """Generate agent response based on intent"""
    
    if intent == "reject":
        return ChatResponse(
            reply="I can only help with SHL assessment selection. I cannot provide legal advice or general hiring guidance.",
            recommendations=[],
            end_of_conversation=False
        )
    
    if intent == "clarify":
        missing = []
        if not constraints.get("role") and not constraints.get("skills"):
            missing.append("role or skills")
        if not constraints.get("test_types"):
            missing.append("assessment type (technical, personality, cognitive, etc.)")
        
        return ChatResponse(
            reply=f"To recommend the right assessments, could you tell me more about: {', '.join(missing)}?",
            recommendations=[],
            end_of_conversation=False
        )
    
    if intent == "compare":
        # Extract assessment names from last message
        last_msg = messages[-1].content
        words = last_msg.split()
        # Simple heuristic: look for capitalized words or quoted terms
        names = [w.strip('",.:;') for w in words if len(w) > 2]
        comparison = compare_assessments(names[:2])
        
        return ChatResponse(
            reply=comparison,
            recommendations=[],
            end_of_conversation=False
        )
    
    # Recommend or refine
    query = f"{constraints.get('role', '')} {' '.join(constraints.get('skills', []))} {' '.join(constraints.get('test_types', []))}"
    results = semantic_search(query, constraints, top_k=10)
    
    if not results:
        return ChatResponse(
            reply="I couldn't find assessments matching your criteria. Could you provide more details?",
            recommendations=[],
            end_of_conversation=False
        )
    
    recommendations = []
    for r in results[:10]:
        item = r["item"]
        test_type = item.get("keys", [""])[0][:1] if item.get("keys") else "K"
        recommendations.append(Recommendation(
            name=item["name"],
            url=item["link"],
            test_type=test_type
        ))
    
    reply = f"Here are {len(recommendations)} SHL assessments for {constraints.get('role', 'your role')}:"
    
    return ChatResponse(
        reply=reply,
        recommendations=recommendations,
        end_of_conversation=False
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    messages = request.messages
    
    # Extract constraints from conversation
    constraints = extract_constraints(messages)
    
    # Classify intent
    intent = classify_intent(messages, constraints)
    
    # Generate response
    response = generate_response(messages, intent, constraints)
    
    return response

@app.post("/evaluate")
def evaluate(request: Dict) -> Dict:
    """
    Evaluate the quality of a response
    
    Request body:
    {
        "response": {"reply": "...", "recommendations": [...]},
        "constraints": {"role": "...", "seniority": "...", ...},
        "expected_behavior": "recommend",
        "expected_keywords": ["java"]
    }
    """
    response = request.get('response', {})
    constraints = request.get('constraints', {})
    expected_behavior = request.get('expected_behavior', 'recommend')
    expected_keywords = request.get('expected_keywords', [])
    
    evaluation = evaluator.comprehensive_evaluation(
        response=response,
        constraints=constraints,
        expected_behavior=expected_behavior,
        expected_keywords=expected_keywords
    )
    
    return evaluation
