#!/usr/bin/env python3
"""
Evaluation Suite for Rishi's Resume MCP Server
Tests the server's ability to accurately answer questions about the resume
"""

import json
import time
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCase:
    """Represents a test case for the resume server"""
    query: str
    expected_keywords: List[str]
    category: str
    min_score: float = 0.7


class ResumeServerEvaluator:
    """Evaluator for testing the resume MCP server"""

    def __init__(self):
        self.test_cases = self._load_test_cases()
        self.results = []

    def _load_test_cases(self) -> List[TestCase]:
        """Load test cases for evaluation"""
        return [
            # AI/ML Experience Tests
            TestCase(
                query="What AI/ML experience does Rishi have?",
                expected_keywords=["92%", "ML-powered", "underwriting model", "Claude Code", "AI adoption"],
                category="ai_ml",
                min_score=0.8
            ),
            TestCase(
                query="Tell me about the underwriting model",
                expected_keywords=["92% accuracy", "automated risk assessment", "human-in-loop", "85% reduction"],
                category="ai_ml",
                min_score=0.75
            ),

            # Revenue Impact Tests
            TestCase(
                query="What revenue impact has Rishi delivered?",
                expected_keywords=["$5M", "$4M", "$20M", "$800K"],
                category="metrics",
                min_score=0.7
            ),
            TestCase(
                query="Show me Rishi's business impact",
                expected_keywords=["revenue", "85%", "90%", "60%", "conversion"],
                category="metrics",
                min_score=0.6
            ),

            # Experience Tests
            TestCase(
                query="What companies has Rishi worked at?",
                expected_keywords=["Justworks", "Stash", "Casper", "Peet's"],
                category="experience",
                min_score=0.8
            ),
            TestCase(
                query="Tell me about Rishi's experience at Justworks",
                expected_keywords=["Senior Product Manager", "AI-enabled", "compliance", "risk"],
                category="experience",
                min_score=0.7
            ),

            # Skills Tests
            TestCase(
                query="What technical skills does Rishi have?",
                expected_keywords=["SQL", "API", "platform", "architecture"],
                category="skills",
                min_score=0.6
            ),
            TestCase(
                query="Does Rishi have experience with regulated industries?",
                expected_keywords=["fintech", "insurance", "compliance", "regulatory"],
                category="domain",
                min_score=0.7
            ),

            # Leadership Tests
            TestCase(
                query="What leadership experience does Rishi have?",
                expected_keywords=["coaching", "cross-functional", "championing", "mentoring"],
                category="leadership",
                min_score=0.5
            ),

            # Specific Achievement Tests
            TestCase(
                query="Tell me about mobile app launches",
                expected_keywords=["iOS", "Android", "300K", "$20M", "loyalty"],
                category="experience",
                min_score=0.6
            ),
            TestCase(
                query="What migration projects has Rishi led?",
                expected_keywords=["92% accounts", "1.5M users", "zero disruption"],
                category="experience",
                min_score=0.5
            ),

            # Education Tests
            TestCase(
                query="What is Rishi's educational background?",
                expected_keywords=["Masters", "Information Systems", "Computer Science", "Cincinnati"],
                category="education",
                min_score=0.7
            ),

            # Fit for Role Tests
            TestCase(
                query="Why is Rishi a good fit for an AI PM role?",
                expected_keywords=["AI", "ML", "product", "technical", "regulated"],
                category="fit",
                min_score=0.6
            ),
        ]

    def calculate_score(self, response: str, test_case: TestCase) -> Tuple[float, List[str]]:
        """Calculate the score for a response based on expected keywords"""
        response_lower = response.lower()
        found_keywords = []

        for keyword in test_case.expected_keywords:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)

        score = len(found_keywords) / len(test_case.expected_keywords) if test_case.expected_keywords else 0
        return score, found_keywords

    def evaluate_response(self, test_case: TestCase, response: str, response_time_ms: int) -> Dict[str, Any]:
        """Evaluate a single response"""
        score, found_keywords = self.calculate_score(response, test_case)
        passed = score >= test_case.min_score

        return {
            "query": test_case.query,
            "category": test_case.category,
            "score": round(score, 2),
            "passed": passed,
            "expected_keywords": test_case.expected_keywords,
            "found_keywords": found_keywords,
            "missing_keywords": [k for k in test_case.expected_keywords if k not in found_keywords],
            "response_time_ms": response_time_ms,
            "min_score_required": test_case.min_score
        }

    def run_evaluation_suite(self, server_func) -> Dict[str, Any]:
        """Run the complete evaluation suite"""
        print("🧪 Running Resume Server Evaluation Suite...")
        print("=" * 50)

        results = []
        category_scores = {}

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n[{i}/{len(self.test_cases)}] Testing: {test_case.query}")

            # Measure response time
            start_time = time.time()
            try:
                response = server_func(test_case.query)
                response_time_ms = int((time.time() - start_time) * 1000)

                # Evaluate the response
                result = self.evaluate_response(test_case, response, response_time_ms)
                results.append(result)

                # Track category scores
                if test_case.category not in category_scores:
                    category_scores[test_case.category] = []
                category_scores[test_case.category].append(result["score"])

                # Print result
                status = "✅ PASS" if result["passed"] else "❌ FAIL"
                print(f"  {status} - Score: {result['score']:.0%} (Required: {test_case.min_score:.0%})")
                print(f"  Found: {', '.join(result['found_keywords'][:3])}...")
                if result["missing_keywords"]:
                    print(f"  Missing: {', '.join(result['missing_keywords'][:3])}...")

            except Exception as e:
                print(f"  ❌ ERROR: {str(e)}")
                results.append({
                    "query": test_case.query,
                    "error": str(e),
                    "passed": False,
                    "score": 0
                })

        # Calculate summary statistics
        total_passed = sum(1 for r in results if r.get("passed", False))
        total_tests = len(results)
        pass_rate = total_passed / total_tests if total_tests > 0 else 0

        avg_scores_by_category = {}
        for category, scores in category_scores.items():
            avg_scores_by_category[category] = round(sum(scores) / len(scores), 2) if scores else 0

        response_times = [r.get("response_time_ms", 0) for r in results if "response_time_ms" in r]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        summary = {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_tests - total_passed,
            "pass_rate": round(pass_rate, 2),
            "average_response_time_ms": round(avg_response_time),
            "category_scores": avg_scores_by_category,
            "detailed_results": results
        }

        # Print summary
        print("\n" + "=" * 50)
        print("📊 EVALUATION SUMMARY")
        print("=" * 50)
        print(f"Overall Pass Rate: {pass_rate:.0%} ({total_passed}/{total_tests})")
        print(f"Average Response Time: {avg_response_time:.0f}ms")
        print("\nCategory Performance:")
        for category, score in avg_scores_by_category.items():
            print(f"  • {category.title()}: {score:.0%}")

        return summary

    def save_results(self, results: Dict[str, Any], filepath: str = "evaluation_results.json"):
        """Save evaluation results to a file"""
        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {filepath}")


def generate_sample_questions() -> List[Dict[str, str]]:
    """Generate sample questions for the hiring manager to ask"""
    return [
        {
            "category": "AI/ML Experience",
            "questions": [
                "What AI models has Rishi built and deployed?",
                "Tell me about Rishi's experience with ML in production",
                "How has Rishi championed AI adoption?",
                "What's Rishi's experience with Claude and LLMs?"
            ]
        },
        {
            "category": "Business Impact",
            "questions": [
                "What's Rishi's track record for revenue generation?",
                "How has Rishi improved operational efficiency?",
                "Show me examples of cost savings Rishi has delivered"
            ]
        },
        {
            "category": "Product Leadership",
            "questions": [
                "What 0→1 products has Rishi launched?",
                "How does Rishi approach product strategy?",
                "Tell me about Rishi's experience with migrations and platform transitions"
            ]
        },
        {
            "category": "Domain Expertise",
            "questions": [
                "What's Rishi's experience with regulated industries?",
                "Has Rishi worked with compliance and risk management?",
                "Tell me about Rishi's fintech experience"
            ]
        },
        {
            "category": "Technical Skills",
            "questions": [
                "What technical skills does Rishi bring to a PM role?",
                "Can Rishi work with engineering teams effectively?",
                "What's Rishi's experience with data and analytics?"
            ]
        },
        {
            "category": "Fit for Role",
            "questions": [
                "Why is Rishi a great fit for an AI PM role?",
                "What unique value does Rishi bring compared to other PMs?",
                "How does Rishi's background prepare him for leading AI products?"
            ]
        }
    ]


def save_sample_questions():
    """Save sample questions to a file for the demo"""
    questions = generate_sample_questions()

    with open("demo/sample_questions.json", "w") as f:
        json.dump(questions, f, indent=2)

    # Also create a markdown version
    md_content = "# Sample Questions for Rishi's Resume\n\n"
    md_content += "Try asking these questions to explore Rishi's qualifications:\n\n"

    for category in questions:
        md_content += f"## {category['category']}\n\n"
        for question in category['questions']:
            md_content += f"- {question}\n"
        md_content += "\n"

    with open("demo/sample_questions.md", "w") as f:
        f.write(md_content)

    print("📝 Sample questions saved to demo/sample_questions.json and demo/sample_questions.md")


if __name__ == "__main__":
    # Example of how to run evaluations
    print("Resume Server Evaluation Suite")
    print("This module contains test cases for evaluating the resume MCP server")
    print("\nTo run evaluations, integrate with your MCP server implementation")

    # Save sample questions for the demo
    import os
    os.makedirs("demo", exist_ok=True)
    save_sample_questions()

    # Show example test case
    evaluator = ResumeServerEvaluator()
    print(f"\nLoaded {len(evaluator.test_cases)} test cases")
    print("\nExample test case:")
    example = evaluator.test_cases[0]
    print(f"  Query: {example.query}")
    print(f"  Expected keywords: {', '.join(example.expected_keywords)}")
    print(f"  Category: {example.category}")
    print(f"  Min score: {example.min_score:.0%}")