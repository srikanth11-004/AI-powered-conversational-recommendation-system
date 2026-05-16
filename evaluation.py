"""
Evaluation Module for SHL Assessment Recommender
Measures retrieval quality, recommendation relevance, groundedness, and accuracy
"""

import json
from typing import List, Dict, Set
from collections import defaultdict

class Evaluator:
    """Evaluates the quality of recommendations and responses"""
    
    def __init__(self, catalog_path: str = "shl_product_catalog.json"):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)
        self.catalog_urls = {item['link'] for item in self.catalog}
        self.catalog_names = {item['name'].lower() for item in self.catalog}
    
    def evaluate_groundedness(self, recommendations: List[Dict]) -> Dict:
        """
        Verify all recommendations come from catalog (no hallucinations)
        
        Returns:
            {
                "grounded": bool,
                "grounded_count": int,
                "total_count": int,
                "grounded_percentage": float,
                "invalid_urls": List[str]
            }
        """
        if not recommendations:
            return {
                "grounded": True,
                "grounded_count": 0,
                "total_count": 0,
                "grounded_percentage": 100.0,
                "invalid_urls": []
            }
        
        invalid_urls = []
        grounded_count = 0
        
        for rec in recommendations:
            url = rec.get('url', '')
            if url in self.catalog_urls:
                grounded_count += 1
            else:
                invalid_urls.append(url)
        
        total = len(recommendations)
        percentage = (grounded_count / total * 100) if total > 0 else 0
        
        return {
            "grounded": len(invalid_urls) == 0,
            "grounded_count": grounded_count,
            "total_count": total,
            "grounded_percentage": percentage,
            "invalid_urls": invalid_urls
        }
    
    def evaluate_retrieval_quality(self, 
                                   recommendations: List[Dict], 
                                   expected_keywords: List[str],
                                   expected_test_types: List[str] = None) -> Dict:
        """
        Measure retrieval quality using precision and relevance
        
        Args:
            recommendations: List of recommended assessments
            expected_keywords: Keywords that should appear (e.g., ["java", "coding"])
            expected_test_types: Expected test types (e.g., ["K", "P"])
        
        Returns:
            {
                "precision": float,
                "keyword_match_rate": float,
                "test_type_match_rate": float,
                "avg_relevance_score": float
            }
        """
        if not recommendations:
            return {
                "precision": 0.0,
                "keyword_match_rate": 0.0,
                "test_type_match_rate": 0.0,
                "avg_relevance_score": 0.0
            }
        
        keyword_matches = 0
        test_type_matches = 0
        relevance_scores = []
        
        for rec in recommendations:
            name = rec.get('name', '').lower()
            test_type = rec.get('test_type', '')
            
            # Check keyword matches
            keyword_score = sum(1 for kw in expected_keywords if kw.lower() in name)
            if keyword_score > 0:
                keyword_matches += 1
            
            # Check test type matches
            if expected_test_types and test_type in expected_test_types:
                test_type_matches += 1
            
            # Calculate relevance score (0-1)
            relevance = min(keyword_score / len(expected_keywords), 1.0) if expected_keywords else 0.5
            relevance_scores.append(relevance)
        
        total = len(recommendations)
        
        return {
            "precision": keyword_matches / total if total > 0 else 0.0,
            "keyword_match_rate": keyword_matches / total if total > 0 else 0.0,
            "test_type_match_rate": test_type_matches / total if total > 0 and expected_test_types else 1.0,
            "avg_relevance_score": sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        }
    
    def evaluate_recommendation_relevance(self, 
                                         recommendations: List[Dict],
                                         constraints: Dict) -> Dict:
        """
        Evaluate how well recommendations match user constraints
        
        Args:
            recommendations: List of recommended assessments
            constraints: User constraints (role, skills, seniority, test_types)
        
        Returns:
            {
                "relevance_score": float (0-1),
                "role_match": bool,
                "seniority_match": bool,
                "test_type_match": bool,
                "details": Dict
            }
        """
        if not recommendations:
            return {
                "relevance_score": 0.0,
                "role_match": False,
                "seniority_match": False,
                "test_type_match": False,
                "details": {}
            }
        
        role = constraints.get('role', '').lower()
        seniority = constraints.get('seniority', '').lower()
        test_types = constraints.get('test_types', [])
        
        role_matches = 0
        seniority_matches = 0
        test_type_matches = 0
        
        for rec in recommendations:
            name = rec.get('name', '').lower()
            
            # Check role match
            if role and role in name:
                role_matches += 1
            
            # Check test type match
            if test_types:
                rec_test_type = rec.get('test_type', '')
                test_type_map = {
                    'K': 'Knowledge & Skills',
                    'P': 'Personality & Behavior',
                    'A': 'Ability & Aptitude',
                    'S': 'Simulations',
                    'C': 'Competencies'
                }
                if any(tt in test_type_map.get(rec_test_type, '') for tt in test_types):
                    test_type_matches += 1
        
        total = len(recommendations)
        
        # Calculate overall relevance score
        scores = []
        if role:
            scores.append(role_matches / total)
        if test_types:
            scores.append(test_type_matches / total)
        
        relevance_score = sum(scores) / len(scores) if scores else 0.5
        
        return {
            "relevance_score": relevance_score,
            "role_match": role_matches > 0 if role else True,
            "seniority_match": True,  # Seniority is filtered during search
            "test_type_match": test_type_matches > 0 if test_types else True,
            "details": {
                "role_matches": role_matches,
                "test_type_matches": test_type_matches,
                "total_recommendations": total
            }
        }
    
    def evaluate_response_accuracy(self, 
                                   response: Dict,
                                   expected_behavior: str) -> Dict:
        """
        Evaluate if response matches expected behavior
        
        Args:
            response: API response
            expected_behavior: One of ["clarify", "recommend", "refine", "compare", "reject"]
        
        Returns:
            {
                "correct_behavior": bool,
                "has_recommendations": bool,
                "recommendation_count": int,
                "within_limits": bool (1-10 recommendations)
            }
        """
        recommendations = response.get('recommendations', [])
        reply = response.get('reply', '').lower()
        
        rec_count = len(recommendations)
        
        # Check if behavior matches expectation
        behavior_indicators = {
            "clarify": ["could you", "tell me more", "what", "which"],
            "recommend": ["here are", "assessments for", "recommendations"],
            "refine": ["updated", "here are"],
            "compare": ["comparing", "difference", "vs"],
            "reject": ["cannot", "only help with", "shl assessment"]
        }
        
        indicators = behavior_indicators.get(expected_behavior, [])
        correct_behavior = any(ind in reply for ind in indicators)
        
        # Check recommendation count
        if expected_behavior in ["clarify", "reject", "compare"]:
            expected_rec_count = 0
        else:  # recommend, refine
            expected_rec_count = "1-10"
        
        within_limits = (
            (expected_behavior in ["clarify", "reject", "compare"] and rec_count == 0) or
            (expected_behavior in ["recommend", "refine"] and 1 <= rec_count <= 10)
        )
        
        return {
            "correct_behavior": correct_behavior,
            "has_recommendations": rec_count > 0,
            "recommendation_count": rec_count,
            "within_limits": within_limits,
            "expected_behavior": expected_behavior
        }
    
    def comprehensive_evaluation(self,
                                response: Dict,
                                constraints: Dict,
                                expected_behavior: str,
                                expected_keywords: List[str] = None) -> Dict:
        """
        Run all evaluation metrics
        
        Returns comprehensive evaluation report
        """
        recommendations = response.get('recommendations', [])
        
        # 1. Groundedness
        groundedness = self.evaluate_groundedness(recommendations)
        
        # 2. Retrieval Quality
        retrieval_quality = {}
        if expected_keywords and recommendations:
            retrieval_quality = self.evaluate_retrieval_quality(
                recommendations, 
                expected_keywords
            )
        
        # 3. Recommendation Relevance
        relevance = {}
        if recommendations:
            relevance = self.evaluate_recommendation_relevance(
                recommendations,
                constraints
            )
        
        # 4. Response Accuracy
        accuracy = self.evaluate_response_accuracy(response, expected_behavior)
        
        # Calculate overall score
        scores = []
        if groundedness['grounded']:
            scores.append(1.0)
        else:
            scores.append(groundedness['grounded_percentage'] / 100)
        
        if retrieval_quality:
            scores.append(retrieval_quality['avg_relevance_score'])
        
        if relevance:
            scores.append(relevance['relevance_score'])
        
        if accuracy['correct_behavior'] and accuracy['within_limits']:
            scores.append(1.0)
        else:
            scores.append(0.5)
        
        overall_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "overall_score": overall_score,
            "groundedness": groundedness,
            "retrieval_quality": retrieval_quality,
            "recommendation_relevance": relevance,
            "response_accuracy": accuracy,
            "summary": {
                "grounded": groundedness['grounded'],
                "relevant": relevance.get('relevance_score', 0) > 0.5 if relevance else True,
                "accurate": accuracy['correct_behavior'],
                "within_limits": accuracy['within_limits']
            }
        }


# Example usage
if __name__ == "__main__":
    evaluator = Evaluator()
    
    # Test case 1: Java developer recommendation
    response = {
        "reply": "Here are 5 assessments for Java developer:",
        "recommendations": [
            {"name": "Java 8 (New)", "url": "https://www.shl.com/products/product-catalog/view/java-8-new/", "test_type": "K"},
            {"name": "Core Java (Advanced Level)", "url": "https://www.shl.com/products/product-catalog/view/core-java-advanced-level-new/", "test_type": "K"}
        ]
    }
    
    constraints = {
        "role": "java",
        "seniority": "mid",
        "test_types": ["Knowledge & Skills"]
    }
    
    evaluation = evaluator.comprehensive_evaluation(
        response=response,
        constraints=constraints,
        expected_behavior="recommend",
        expected_keywords=["java"]
    )
    
    print(json.dumps(evaluation, indent=2))
