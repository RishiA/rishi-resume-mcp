#!/usr/bin/env python3
"""
Advanced Evaluation Harness for Resume MCP Server
Implements retrieval@k metrics, latency benchmarks, and comprehensive scoring
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import statistics

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import server functions directly for evaluation
from server import (
    search_experience,
    get_ai_ml_experience,
    get_metrics_and_impact,
    search_by_skill,
    get_company_details,
    RESUME_DATA
)


@dataclass
class EvalResult:
    """Result of evaluating a single question"""
    question_id: str
    question: str
    category: str
    expected_sections: List[str]
    retrieved_sections: List[str]
    rank_of_first_match: Optional[int]
    all_ranks: List[int]
    latency_ms: float
    score: float
    passed: bool
    has_citations: bool
    response_preview: str


@dataclass
class EvalMetrics:
    """Aggregate evaluation metrics"""
    total_questions: int = 0
    retrieval_at_1: float = 0.0
    retrieval_at_3: float = 0.0
    retrieval_at_5: float = 0.0
    mean_reciprocal_rank: float = 0.0
    p50_latency_ms: float = 0.0
    p90_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    passed_questions: int = 0
    pass_rate: float = 0.0


class ResumeEvaluator:
    """Advanced evaluator for resume MCP server"""

    def __init__(self):
        self.questions_path = Path(__file__).parent / "hiring_manager_questions.json"
        self.load_questions()
        self.results: List[EvalResult] = []

    def load_questions(self):
        """Load evaluation questions and criteria"""
        with open(self.questions_path, "r") as f:
            data = json.load(f)
            self.questions = data["questions"]
            self.criteria = data["evaluation_criteria"]
            self.categories = data["categories"]

    def map_section_ids(self, response: Any) -> List[str]:
        """Extract section identifiers from various response types"""
        sections = []

        # Handle different response structures
        if isinstance(response, dict):
            # Check for explicit sections
            if "matches" in response:
                for match in response.get("matches", []):
                    if "company" in match:
                        company = match["company"].lower().replace(" ", "_")
                        sections.append(f"experience_{company}")
                    if "category" in match:
                        sections.append(f"skills_{match['category']}")

            # Check for AI experience response
            if "related_achievements" in response:
                for achievement in response["related_achievements"]:
                    if "company" in achievement:
                        company = achievement["company"].lower().replace(" ", "_")
                        sections.append(f"experience_{company}")

            # Check for metrics response
            if "revenue_impact" in response:
                sections.append("key_metrics")
            if "efficiency_gains" in response:
                sections.append("key_metrics")

            # Check for company-specific responses
            if "company" in response and "title" in response:
                company = response["company"].lower().replace(" ", "_")
                sections.append(f"experience_{company}")

        # Deduplicate while preserving order
        seen = set()
        unique_sections = []
        for s in sections:
            if s not in seen:
                seen.add(s)
                unique_sections.append(s)

        return unique_sections

    def retrieve_for_question(self, question: str) -> Tuple[List[str], float]:
        """
        Retrieve relevant sections for a question
        Returns: (section_ids, latency_ms)
        """
        start_time = time.time()
        all_sections = []

        # Try multiple retrieval strategies
        strategies = [
            ("search_experience", lambda: search_experience(question)),
            ("get_ai_ml", lambda: get_ai_ml_experience() if "ai" in question.lower() or "ml" in question.lower() else None),
            ("get_metrics", lambda: get_metrics_and_impact() if "metric" in question.lower() or "impact" in question.lower() or "revenue" in question.lower() else None),
            ("search_skill", lambda: search_by_skill(question.split()[-1]) if len(question.split()) > 0 else None),
        ]

        for strategy_name, strategy_func in strategies:
            try:
                result = strategy_func()
                if result:
                    sections = self.map_section_ids(result)
                    all_sections.extend(sections)
            except Exception as e:
                # Log but continue with other strategies
                pass

        latency_ms = (time.time() - start_time) * 1000

        # Deduplicate and rank by frequency
        section_counts = defaultdict(int)
        for s in all_sections:
            section_counts[s] += 1

        ranked_sections = sorted(section_counts.keys(), key=lambda x: section_counts[x], reverse=True)

        return ranked_sections[:10], latency_ms  # Return top 10

    def calculate_retrieval_metrics(self, expected: List[str], retrieved: List[str]) -> Dict[str, Any]:
        """Calculate retrieval@k and other metrics"""
        metrics = {
            "rank_of_first_match": None,
            "all_ranks": [],
            "retrieval_at_1": False,
            "retrieval_at_3": False,
            "retrieval_at_5": False,
            "reciprocal_rank": 0.0
        }

        # Find ranks of all expected sections in retrieved list
        for expected_section in expected:
            # Handle flexible matching (e.g., "experience_justworks" matches "experience_justworks")
            for i, retrieved_section in enumerate(retrieved, 1):
                if expected_section in retrieved_section or retrieved_section in expected_section:
                    metrics["all_ranks"].append(i)
                    if metrics["rank_of_first_match"] is None:
                        metrics["rank_of_first_match"] = i
                    break

        # Calculate retrieval@k
        if metrics["rank_of_first_match"]:
            metrics["retrieval_at_1"] = metrics["rank_of_first_match"] <= 1
            metrics["retrieval_at_3"] = metrics["rank_of_first_match"] <= 3
            metrics["retrieval_at_5"] = metrics["rank_of_first_match"] <= 5
            metrics["reciprocal_rank"] = 1.0 / metrics["rank_of_first_match"]

        return metrics

    def evaluate_question(self, question_data: Dict) -> EvalResult:
        """Evaluate a single question"""
        question = question_data["question"]

        # Retrieve sections
        retrieved_sections, latency_ms = self.retrieve_for_question(question)

        # Calculate metrics
        metrics = self.calculate_retrieval_metrics(
            question_data["expected_sections"],
            retrieved_sections
        )

        # Check if expected keywords are in response (if we had the actual response text)
        # For now, we'll check if we retrieved the right sections
        score = metrics["reciprocal_rank"]
        passed = metrics["retrieval_at_3"]  # Pass if found in top 3

        return EvalResult(
            question_id=question_data["id"],
            question=question,
            category=question_data["category"],
            expected_sections=question_data["expected_sections"],
            retrieved_sections=retrieved_sections[:5],  # Top 5 for display
            rank_of_first_match=metrics["rank_of_first_match"],
            all_ranks=metrics["all_ranks"],
            latency_ms=latency_ms,
            score=score,
            passed=passed,
            has_citations=len(retrieved_sections) > 0,
            response_preview=f"Retrieved {len(retrieved_sections)} sections"
        )

    def run_evaluation(self, verbose: bool = True) -> EvalMetrics:
        """Run full evaluation suite"""
        if verbose:
            print("🧪 Running Advanced Resume Evaluation Suite")
            print("=" * 60)
            print(f"Questions: {len(self.questions)}")
            print(f"Target Retrieval@1: {self.criteria['retrieval_at_1']:.0%}")
            print(f"Target Retrieval@3: {self.criteria['retrieval_at_3']:.0%}")
            print(f"Target P50 Latency: {self.criteria['p50_latency_ms']}ms")
            print("=" * 60 + "\n")

        # Run all evaluations
        for i, question_data in enumerate(self.questions, 1):
            if verbose:
                print(f"[{i}/{len(self.questions)}] {question_data['question'][:50]}...")

            result = self.evaluate_question(question_data)
            self.results.append(result)

            if verbose:
                status = "✅" if result.passed else "❌"
                rank_str = f"Rank {result.rank_of_first_match}" if result.rank_of_first_match else "Not found"
                print(f"  {status} {rank_str} | {result.latency_ms:.0f}ms | Score: {result.score:.2f}")

        # Calculate aggregate metrics
        metrics = self.calculate_aggregate_metrics()

        if verbose:
            self.print_summary(metrics)

        return metrics

    def calculate_aggregate_metrics(self) -> EvalMetrics:
        """Calculate aggregate metrics from results"""
        metrics = EvalMetrics()
        metrics.total_questions = len(self.results)

        # Retrieval metrics
        retrieval_at_1 = sum(1 for r in self.results if r.rank_of_first_match and r.rank_of_first_match <= 1)
        retrieval_at_3 = sum(1 for r in self.results if r.rank_of_first_match and r.rank_of_first_match <= 3)
        retrieval_at_5 = sum(1 for r in self.results if r.rank_of_first_match and r.rank_of_first_match <= 5)

        metrics.retrieval_at_1 = retrieval_at_1 / len(self.results) if self.results else 0
        metrics.retrieval_at_3 = retrieval_at_3 / len(self.results) if self.results else 0
        metrics.retrieval_at_5 = retrieval_at_5 / len(self.results) if self.results else 0

        # MRR
        reciprocal_ranks = [r.score for r in self.results]
        metrics.mean_reciprocal_rank = statistics.mean(reciprocal_ranks) if reciprocal_ranks else 0

        # Latency percentiles
        latencies = [r.latency_ms for r in self.results]
        if latencies:
            sorted_latencies = sorted(latencies)
            metrics.p50_latency_ms = sorted_latencies[len(sorted_latencies) // 2]
            metrics.p90_latency_ms = sorted_latencies[int(len(sorted_latencies) * 0.9)]
            metrics.p99_latency_ms = sorted_latencies[int(len(sorted_latencies) * 0.99)]

        # Category scores
        category_results = defaultdict(list)
        for r in self.results:
            category_results[r.category].append(r.score)

        for category, scores in category_results.items():
            metrics.category_scores[category] = statistics.mean(scores)

        # Pass rate
        metrics.passed_questions = sum(1 for r in self.results if r.passed)
        metrics.pass_rate = metrics.passed_questions / len(self.results) if self.results else 0

        return metrics

    def print_summary(self, metrics: EvalMetrics):
        """Print evaluation summary"""
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)

        # Overall performance
        print(f"\n✅ Passed: {metrics.passed_questions}/{metrics.total_questions} ({metrics.pass_rate:.0%})")

        # Retrieval metrics
        print(f"\n📍 Retrieval Metrics:")
        target_r1 = self.criteria['retrieval_at_1']
        target_r3 = self.criteria['retrieval_at_3']
        r1_pass = "✅" if metrics.retrieval_at_1 >= target_r1 else "❌"
        r3_pass = "✅" if metrics.retrieval_at_3 >= target_r3 else "❌"
        print(f"  Retrieval@1: {metrics.retrieval_at_1:.0%} {r1_pass} (target: {target_r1:.0%})")
        print(f"  Retrieval@3: {metrics.retrieval_at_3:.0%} {r3_pass} (target: {target_r3:.0%})")
        print(f"  Retrieval@5: {metrics.retrieval_at_5:.0%}")
        print(f"  MRR: {metrics.mean_reciprocal_rank:.3f}")

        # Latency metrics
        print(f"\n⏱️  Latency Metrics:")
        target_p50 = self.criteria['p50_latency_ms']
        p50_pass = "✅" if metrics.p50_latency_ms <= target_p50 else "❌"
        print(f"  P50: {metrics.p50_latency_ms:.0f}ms {p50_pass} (target: <{target_p50}ms)")
        print(f"  P90: {metrics.p90_latency_ms:.0f}ms")
        print(f"  P99: {metrics.p99_latency_ms:.0f}ms")

        # Category breakdown
        print(f"\n📂 Category Performance:")
        sorted_categories = sorted(metrics.category_scores.items(), key=lambda x: x[1], reverse=True)
        for category, score in sorted_categories[:5]:
            cat_name = self.categories.get(category, category)
            print(f"  {category}: {score:.2f} - {cat_name}")

        # Failed questions
        failed = [r for r in self.results if not r.passed]
        if failed:
            print(f"\n❌ Failed Questions ({len(failed)}):")
            for r in failed[:5]:
                print(f"  - {r.question[:60]}...")
                print(f"    Expected: {r.expected_sections}")
                print(f"    Retrieved: {r.retrieved_sections[:3]}")

        # Final verdict
        print("\n" + "=" * 60)
        all_pass = (
            metrics.retrieval_at_1 >= target_r1 and
            metrics.retrieval_at_3 >= target_r3 and
            metrics.p50_latency_ms <= target_p50
        )
        if all_pass:
            print("🎉 ALL EVALUATION CRITERIA MET!")
        else:
            print("⚠️  Some criteria not met. See details above.")

    def save_results(self, filepath: str = "eval_results.json"):
        """Save detailed results to JSON"""
        output = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": {
                "retrieval_at_1": self.calculate_aggregate_metrics().retrieval_at_1,
                "retrieval_at_3": self.calculate_aggregate_metrics().retrieval_at_3,
                "retrieval_at_5": self.calculate_aggregate_metrics().retrieval_at_5,
                "mrr": self.calculate_aggregate_metrics().mean_reciprocal_rank,
                "p50_latency_ms": self.calculate_aggregate_metrics().p50_latency_ms,
                "pass_rate": self.calculate_aggregate_metrics().pass_rate
            },
            "detailed_results": [
                {
                    "question_id": r.question_id,
                    "question": r.question,
                    "passed": r.passed,
                    "rank": r.rank_of_first_match,
                    "latency_ms": r.latency_ms,
                    "score": r.score
                }
                for r in self.results
            ]
        }

        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\n💾 Detailed results saved to {filepath}")


if __name__ == "__main__":
    evaluator = ResumeEvaluator()
    metrics = evaluator.run_evaluation(verbose=True)
    evaluator.save_results()