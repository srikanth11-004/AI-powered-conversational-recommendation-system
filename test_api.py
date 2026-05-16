import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health check:", response.json())
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_clarify():
    payload = {
        "messages": [
            {"role": "user", "content": "I need an assessment"}
        ]
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    print("\n=== Clarify Test ===")
    print("Reply:", result["reply"])
    print("Recommendations:", len(result["recommendations"]))
    assert len(result["recommendations"]) == 0

def test_recommend():
    payload = {
        "messages": [
            {"role": "user", "content": "I'm hiring a Java developer"},
            {"role": "assistant", "content": "What seniority level?"},
            {"role": "user", "content": "Mid-level, around 4 years"}
        ]
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    print("\n=== Recommend Test ===")
    print("Reply:", result["reply"])
    print("Recommendations:", len(result["recommendations"]))
    for rec in result["recommendations"][:3]:
        print(f"  - {rec['name']} ({rec['test_type']})")
    assert len(result["recommendations"]) > 0

def test_refine():
    payload = {
        "messages": [
            {"role": "user", "content": "Java developer, mid-level"},
            {"role": "assistant", "content": "Here are 5 assessments..."},
            {"role": "user", "content": "Actually, add personality tests"}
        ]
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    print("\n=== Refine Test ===")
    print("Reply:", result["reply"])
    print("Recommendations:", len(result["recommendations"]))
    assert len(result["recommendations"]) > 0

def test_reject():
    payload = {
        "messages": [
            {"role": "user", "content": "What are the legal requirements for hiring?"}
        ]
    }
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    print("\n=== Reject Test ===")
    print("Reply:", result["reply"])
    assert "cannot" in result["reply"].lower() or "only" in result["reply"].lower()

if __name__ == "__main__":
    print("Testing SHL Agent API...")
    test_health()
    test_clarify()
    test_recommend()
    test_refine()
    test_reject()
    print("\n✅ All tests passed!")
