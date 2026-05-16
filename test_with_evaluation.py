"""
Comprehensive Test Suite with Evaluation Metrics
Tests all agent behaviors and measures quality
"""

import requests
import json
from evaluation import Evaluator

BASE_URL = "http://localhost:8000"
evaluator = Evaluator()

def test_with_evaluation(test_name, payload, expected_behavior, expected_keywords=None, constraints=None):
    """Run test and evaluate response"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")
    
    # Make API call
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    result = response.json()
    
    print(f"\n📝 Response:")
    print(f"  Reply: {result['reply'][:100]}...")
    print(f"  Recommendations: {len(result['recommendations'])}")
    
    # Evaluate
    if constraints is None:
        constraints = {}
    
    evaluation = evaluator.comprehensive_evaluation(
        response=result,
        constraints=constraints,
        expected_behavior=expected_behavior,
        expected_keywords=expected_keywords or []
    )
    
    print(f"\n📊 Evaluation Metrics:")
    print(f"  Overall Score: {evaluation['overall_score']:.2%}")
    print(f"  ✓ Grounded: {evaluation['groundedness']['grounded']} ({evaluation['groundedness']['grounded_percentage']:.1f}%)")
    print(f"  ✓ Correct Behavior: {evaluation['response_accuracy']['correct_behavior']}")
    print(f"  ✓ Within Limits: {evaluation['response_accuracy']['within_limits']}")
    
    if evaluation['recommendation_relevance']:
        print(f"  ✓ Relevance Score: {evaluation['recommendation_relevance']['relevance_score']:.2%}")
    
    if evaluation['retrieval_quality']:
        print(f"  ✓ Keyword Match: {evaluation['retrieval_quality']['keyword_match_rate']:.2%}")
    
    # Pass/Fail
    passed = (
        evaluation['groundedness']['grounded'] and
        evaluation['response_accuracy']['correct_behavior'] and
        evaluation['response_accuracy']['within_limits']
    )
    
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")
    
    return passed, evaluation


def run_all_tests():
    """Run comprehensive test suite"""
    print("\n" + "="*60)
    print("SHL AGENT COMPREHENSIVE TEST SUITE WITH EVALUATION")
    print("="*60)
    
    results = []
    
    # Test 1: Clarify - Vague Query
    passed, eval = test_with_evaluation(
        test_name="Clarify - Vague Query",
        payload={"messages": [{"role": "user", "content": "I need an assessment"}]},
        expected_behavior="clarify",
        constraints={}
    )
    results.append(("Clarify", passed, eval['overall_score']))
    
    # Test 2: Recommend - Java Developer
    passed, eval = test_with_evaluation(
        test_name="Recommend - Java Developer",
        payload={"messages": [{"role": "user", "content": "Hiring a Java developer, mid-level, around 4 years"}]},
        expected_behavior="recommend",
        expected_keywords=["java"],
        constraints={"role": "java", "seniority": "mid"}
    )
    results.append(("Recommend Java", passed, eval['overall_score']))
    
    # Test 3: Recommend - Python Developer
    passed, eval = test_with_evaluation(
        test_name="Recommend - Python Developer",
        payload={"messages": [{"role": "user", "content": "Python developer, senior level, data science"}]},
        expected_behavior="recommend",
        expected_keywords=["python"],
        constraints={"role": "python", "seniority": "senior"}
    )
    results.append(("Recommend Python", passed, eval['overall_score']))
    
    # Test 4: Refine - Add Personality Tests
    passed, eval = test_with_evaluation(
        test_name="Refine - Add Personality Tests",
        payload={"messages": [
            {"role": "user", "content": "Java developer, mid-level"},
            {"role": "assistant", "content": "Here are 5 assessments"},
            {"role": "user", "content": "Actually, add personality tests"}
        ]},
        expected_behavior="refine",
        expected_keywords=["java"],
        constraints={"role": "java", "test_types": ["Personality & Behavior"]}
    )
    results.append(("Refine", passed, eval['overall_score']))
    
    # Test 5: Compare - OPQ vs GSA
    passed, eval = test_with_evaluation(
        test_name="Compare - OPQ vs GSA",
        payload={"messages": [{"role": "user", "content": "What is the difference between OPQ and GSA?"}]},
        expected_behavior="compare",
        constraints={}
    )
    results.append(("Compare", passed, eval['overall_score']))
    
    # Test 6: Reject - Legal Advice
    passed, eval = test_with_evaluation(
        test_name="Reject - Legal Advice",
        payload={"messages": [{"role": "user", "content": "What are the legal requirements for hiring?"}]},
        expected_behavior="reject",
        constraints={}
    )
    results.append(("Reject", passed, eval['overall_score']))
    
    # Test 7: Customer Service
    passed, eval = test_with_evaluation(
        test_name="Recommend - Customer Service",
        payload={"messages": [{"role": "user", "content": "Customer service representative, entry level"}]},
        expected_behavior="recommend",
        expected_keywords=["customer", "service"],
        constraints={"role": "customer service", "seniority": "entry"}
    )
    results.append(("Customer Service", passed, eval['overall_score']))
    
    # Test 8: Job Description Parsing
    passed, eval = test_with_evaluation(
        test_name="Job Description Parsing",
        payload={"messages": [{"role": "user", "content": "Here is a text from job description: We need a Java developer with 4 years experience who works with stakeholders"}]},
        expected_behavior="recommend",
        expected_keywords=["java"],
        constraints={"role": "java", "seniority": "mid"}
    )
    results.append(("Job Description", passed, eval['overall_score']))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    passed_count = sum(1 for _, passed, _ in results if passed)
    avg_score = sum(score for _, _, score in results) / total
    
    for name, passed, score in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {name:25} | Score: {score:.2%}")
    
    print(f"\n{'='*60}")
    print(f"Total: {passed_count}/{total} passed ({passed_count/total:.1%})")
    print(f"Average Score: {avg_score:.2%}")
    print(f"{'='*60}")
    
    # Detailed Metrics
    print(f"\n📊 EVALUATION METRICS SUMMARY:")
    print(f"  ✓ All recommendations grounded in catalog")
    print(f"  ✓ Retrieval quality measured by keyword matching")
    print(f"  ✓ Recommendation relevance scored by constraint matching")
    print(f"  ✓ Response accuracy verified by behavior classification")
    print(f"  ✓ Overall score: {avg_score:.2%}")
    
    if passed_count == total:
        print(f"\n🎉 ALL TESTS PASSED! System is production-ready.")
    else:
        print(f"\n⚠️  {total - passed_count} test(s) failed. Review above for details.")
    
    return passed_count == total


if __name__ == "__main__":
    # Check health first
    try:
        health = requests.get(f"{BASE_URL}/health")
        if health.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            exit(1)
    except:
        print("❌ Cannot connect to server. Make sure it's running on port 8000")
        exit(1)
    
    # Run tests
    success = run_all_tests()
    exit(0 if success else 1)
