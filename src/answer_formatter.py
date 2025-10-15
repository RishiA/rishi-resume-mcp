#!/usr/bin/env python3
"""
Compact Answer Formatter with Citations
Implements the build plan's compact bullet format with line-level citations
"""

import json
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import re


class AnswerFormatter:
    """Format answers in compact bullets with citations"""

    def __init__(self, resume_data_path: str = None):
        if resume_data_path:
            with open(resume_data_path, "r") as f:
                self.resume_data = json.load(f)
        else:
            # Default path
            path = Path(__file__).parent.parent / "resume_data.json"
            with open(path, "r") as f:
                self.resume_data = json.load(f)

    def format_compact_answer(
        self,
        question: str,
        retrieved_data: Dict[str, Any],
        max_bullets: int = 6,
        max_chars: int = 700
    ) -> Dict[str, Any]:
        """
        Format answer as compact bullets with citations

        Returns:
        {
            "text": "• Bullet 1 [experience_justworks]\n• Bullet 2 [skills_ai_ml]",
            "citations": [
                {"section_id": "experience_justworks", "content": "Senior PM at Justworks"},
                {"section_id": "skills_ai_ml", "content": "ML-powered automation"}
            ],
            "metadata": {
                "bullet_count": 2,
                "char_count": 120,
                "has_evidence": true
            }
        }
        """
        bullets = []
        citations = []
        section_map = {}

        # Determine if we have evidence
        has_evidence = bool(retrieved_data)

        if not has_evidence:
            return {
                "text": "• Not evidenced in the resume",
                "citations": [],
                "metadata": {
                    "bullet_count": 1,
                    "char_count": 30,
                    "has_evidence": False
                }
            }

        # Extract key information based on question type
        if "ai" in question.lower() or "ml" in question.lower():
            bullets, citations = self._format_ai_ml_answer(retrieved_data)
        elif "revenue" in question.lower() or "impact" in question.lower():
            bullets, citations = self._format_impact_answer(retrieved_data)
        elif "experience" in question.lower() or "companies" in question.lower():
            bullets, citations = self._format_experience_answer(retrieved_data)
        elif "skill" in question.lower():
            bullets, citations = self._format_skills_answer(retrieved_data)
        else:
            bullets, citations = self._format_general_answer(retrieved_data)

        # Limit bullets and characters
        bullets = bullets[:max_bullets]
        text = "\n".join(bullets)

        if len(text) > max_chars:
            # Truncate to max_chars while keeping complete bullets
            truncated_bullets = []
            char_count = 0
            for bullet in bullets:
                if char_count + len(bullet) + 1 <= max_chars:
                    truncated_bullets.append(bullet)
                    char_count += len(bullet) + 1
                else:
                    break
            bullets = truncated_bullets
            text = "\n".join(bullets)

        return {
            "text": text,
            "citations": citations,
            "metadata": {
                "bullet_count": len(bullets),
                "char_count": len(text),
                "has_evidence": True
            }
        }

    def _format_ai_ml_answer(self, data: Dict) -> Tuple[List[str], List[Dict]]:
        """Format AI/ML specific answers"""
        bullets = []
        citations = []

        # From AI experience
        if "models_built" in data:
            for model in data["models_built"]:
                bullets.append(f"• Built {model} [experience_justworks]")
                citations.append({
                    "section_id": "experience_justworks",
                    "content": model
                })

        if "tools_used" in data:
            tools = ", ".join(data["tools_used"])
            bullets.append(f"• Uses {tools} for AI development [skills_ai_ml]")
            citations.append({
                "section_id": "skills_ai_ml",
                "content": tools
            })

        if "initiatives_led" in data:
            for initiative in data["initiatives_led"][:2]:
                bullets.append(f"• {initiative} [experience_justworks]")
                citations.append({
                    "section_id": "experience_justworks",
                    "content": initiative
                })

        return bullets, citations

    def _format_impact_answer(self, data: Dict) -> Tuple[List[str], List[Dict]]:
        """Format business impact answers"""
        bullets = []
        citations = []

        if "revenue_impact" in data:
            for impact in data["revenue_impact"][:3]:
                bullets.append(f"• Generated {impact} [key_metrics]")
                citations.append({
                    "section_id": "key_metrics",
                    "content": impact
                })

        if "efficiency_gains" in data:
            for gain in data["efficiency_gains"][:2]:
                bullets.append(f"• Achieved {gain} [key_metrics]")
                citations.append({
                    "section_id": "key_metrics",
                    "content": gain
                })

        return bullets, citations

    def _format_experience_answer(self, data: Dict) -> Tuple[List[str], List[Dict]]:
        """Format experience-based answers"""
        bullets = []
        citations = []

        if "matches" in data:
            for match in data["matches"][:4]:
                if "company" in match:
                    company = match["company"]
                    title = match.get("title", "Role")
                    section_id = f"experience_{company.lower().replace(' ', '_')}"
                    bullets.append(f"• {title} at {company} [{ section_id}]")
                    citations.append({
                        "section_id": section_id,
                        "content": f"{title} at {company}"
                    })

                if "achievement" in match:
                    achievement = match["achievement"][:80] + "..." if len(match["achievement"]) > 80 else match["achievement"]
                    bullets.append(f"• {achievement} [{section_id}]")
                    citations.append({
                        "section_id": section_id,
                        "content": achievement
                    })

        return bullets, citations

    def _format_skills_answer(self, data: Dict) -> Tuple[List[str], List[Dict]]:
        """Format skills-based answers"""
        bullets = []
        citations = []

        if "matches" in data:
            for match in data["matches"][:4]:
                if match.get("type") == "skill":
                    category = match["category"]
                    skill = match["skill"]
                    section_id = f"skills_{category}"
                    bullets.append(f"• {skill} [{section_id}]")
                    citations.append({
                        "section_id": section_id,
                        "content": skill
                    })

        return bullets, citations

    def _format_general_answer(self, data: Dict) -> Tuple[List[str], List[Dict]]:
        """Format general answers from any data structure"""
        bullets = []
        citations = []

        # Extract whatever information is available
        if isinstance(data, dict):
            for key, value in list(data.items())[:4]:
                if isinstance(value, list) and value:
                    item = str(value[0])[:100]
                    bullets.append(f"• {item} [resume]")
                    citations.append({
                        "section_id": "resume",
                        "content": item
                    })
                elif isinstance(value, str):
                    bullets.append(f"• {value[:100]} [resume]")
                    citations.append({
                        "section_id": "resume",
                        "content": value[:100]
                    })

        if not bullets:
            bullets.append("• Information available in resume [resume]")
            citations.append({
                "section_id": "resume",
                "content": "See full resume for details"
            })

        return bullets, citations

    def add_inline_citations(self, text: str, section_ids: List[str]) -> str:
        """Add inline citations to text"""
        if not section_ids:
            return text

        # Add citation at the end if not present
        if not re.search(r'\[[\w_]+\]', text):
            return f"{text} [{section_ids[0]}]"
        return text


# Standalone function for easy integration
def format_answer(question: str, data: Dict, max_bullets: int = 6) -> Dict[str, Any]:
    """
    Convenience function to format answers

    Usage:
        from answer_formatter import format_answer
        result = format_answer("What are Rishi's AI skills?", ai_experience_data)
    """
    formatter = AnswerFormatter()
    return formatter.format_compact_answer(question, data, max_bullets)


if __name__ == "__main__":
    # Test the formatter
    formatter = AnswerFormatter()

    # Test AI/ML answer
    test_data = {
        "models_built": ["ML-powered underwriting model with 92% accuracy"],
        "tools_used": ["Claude Code", "Cursor", "No-code AI tools"],
        "initiatives_led": ["AI adoption champion at Justworks", "Training PMs on AI-assisted coding"]
    }

    result = formatter.format_compact_answer("What are Rishi's AI skills?", test_data)
    print("AI/ML Answer:")
    print(result["text"])
    print(f"\nCitations: {len(result['citations'])}")
    print(f"Characters: {result['metadata']['char_count']}")
    print("-" * 40)

    # Test impact answer
    test_data = {
        "revenue_impact": ["$5M new revenue", "$4M incremental retail", "$20M mobile payments"],
        "efficiency_gains": ["85% workload reduction", "90% overhead reduction"]
    }

    result = formatter.format_compact_answer("What's Rishi's business impact?", test_data)
    print("\nBusiness Impact Answer:")
    print(result["text"])
    print(f"\nCitations: {len(result['citations'])}")
    print(f"Characters: {result['metadata']['char_count']}")
    print("-" * 40)

    # Test no evidence case
    result = formatter.format_compact_answer("Does Rishi have patents?", {})
    print("\nNo Evidence Answer:")
    print(result["text"])
    print(f"Has evidence: {result['metadata']['has_evidence']}")