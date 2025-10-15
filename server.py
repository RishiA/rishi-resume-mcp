#!/usr/bin/env python3
"""
Rishi's Resume MCP Server
Interactive resume server for AI PM role demonstration
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Rishi's Resume Server")

# Load resume data
RESUME_DATA_PATH = Path(__file__).parent / "resume_data.json"
with open(RESUME_DATA_PATH, "r") as f:
    RESUME_DATA = json.load(f)


# === RESOURCES ===

@mcp.resource("resume://summary")
def get_summary() -> str:
    """Get professional summary"""
    return RESUME_DATA["summary"]


@mcp.resource("resume://experience")
def get_experience() -> str:
    """Get complete work experience"""
    experiences = []
    for exp in RESUME_DATA["experience"]:
        exp_text = f"**{exp['title']}** at {exp['company']} ({exp['duration']})\n"
        exp_text += f"Location: {exp['location']}\n"
        if exp["achievements"]:
            exp_text += "Key Achievements:\n"
            for achievement in exp["achievements"]:
                exp_text += f"• {achievement['description']}\n"
                if achievement.get("metrics"):
                    exp_text += f"  Metrics: {', '.join(achievement['metrics'])}\n"
        experiences.append(exp_text)
    return "\n\n".join(experiences)


@mcp.resource("resume://skills/{category}")
def get_skills(category: str) -> str:
    """Get skills by category (product_strategy, ai_ml, technical, domain, analytics, leadership)"""
    skills = RESUME_DATA.get("skills", {})
    if category in skills:
        return f"**{category.replace('_', ' ').title()} Skills:**\n" + "\n".join(f"• {skill}" for skill in skills[category])
    return f"No skills found for category: {category}. Available categories: {', '.join(skills.keys())}"


@mcp.resource("resume://education")
def get_education() -> str:
    """Get education background"""
    edu_list = []
    for edu in RESUME_DATA["education"]:
        edu_list.append(f"• {edu['degree']} - {edu['institution']} ({edu['years']})")
    return "**Education:**\n" + "\n".join(edu_list)


@mcp.resource("resume://contact")
def get_contact() -> str:
    """Get contact information"""
    personal = RESUME_DATA["personal"]
    return f"""**Contact Information:**
Name: {personal['name']}
LinkedIn: {personal['linkedin']}
Website: {personal.get('website', '')}"""


# === TOOLS ===

@mcp.tool()
def search_experience(query: str) -> Dict[str, Any]:
    """Search through work experience for specific keywords or companies"""
    query_lower = query.lower()
    matches = []

    for exp in RESUME_DATA["experience"]:
        # Check company, title, and achievements
        if (query_lower in exp["company"].lower() or
            query_lower in exp["title"].lower()):
            matches.append({
                "company": exp["company"],
                "title": exp["title"],
                "duration": exp["duration"],
                "match_type": "role"
            })

        for achievement in exp.get("achievements", []):
            if query_lower in achievement["description"].lower():
                matches.append({
                    "company": exp["company"],
                    "title": exp["title"],
                    "achievement": achievement["description"],
                    "metrics": achievement.get("metrics", []),
                    "match_type": "achievement"
                })

    return {
        "query": query,
        "results_count": len(matches),
        "matches": matches
    }


@mcp.tool()
def get_ai_ml_experience() -> Dict[str, Any]:
    """Get all AI/ML related experience and projects"""
    ai_experience = RESUME_DATA.get("ai_experience", {})

    # Also search for AI/ML in achievements
    ai_achievements = []
    for exp in RESUME_DATA["experience"]:
        for achievement in exp.get("achievements", []):
            if any(tag in ["AI/ML", "AI", "automation", "ML"] for tag in achievement.get("tags", [])):
                ai_achievements.append({
                    "company": exp["company"],
                    "role": exp["title"],
                    "achievement": achievement["description"],
                    "metrics": achievement.get("metrics", [])
                })

    return {
        "models_built": ai_experience.get("models_built", []),
        "tools_used": ai_experience.get("tools_used", []),
        "initiatives_led": ai_experience.get("initiatives_led", []),
        "design_patterns": ai_experience.get("design_patterns", []),
        "related_achievements": ai_achievements
    }


@mcp.tool()
def get_metrics_and_impact() -> Dict[str, Any]:
    """Get quantifiable metrics and business impact"""
    return RESUME_DATA.get("key_metrics", {})


@mcp.tool()
def search_by_skill(skill: str) -> Dict[str, Any]:
    """Search for experiences related to a specific skill"""
    skill_lower = skill.lower()
    matches = []

    # Search in skills
    for category, skills_list in RESUME_DATA.get("skills", {}).items():
        for s in skills_list:
            if skill_lower in s.lower():
                matches.append({
                    "type": "skill",
                    "category": category,
                    "skill": s
                })

    # Search in experience tags
    for exp in RESUME_DATA["experience"]:
        for achievement in exp.get("achievements", []):
            if any(skill_lower in tag.lower() for tag in achievement.get("tags", [])):
                matches.append({
                    "type": "experience",
                    "company": exp["company"],
                    "achievement": achievement["description"],
                    "tags": achievement.get("tags", [])
                })

    return {
        "query": skill,
        "matches": matches,
        "count": len(matches)
    }


@mcp.tool()
def get_company_details(company: str) -> Dict[str, Any]:
    """Get detailed information about experience at a specific company"""
    company_lower = company.lower()

    for exp in RESUME_DATA["experience"]:
        if company_lower in exp["company"].lower():
            return {
                "company": exp["company"],
                "title": exp["title"],
                "location": exp["location"],
                "duration": exp["duration"],
                "achievements": exp.get("achievements", []),
                "total_achievements": len(exp.get("achievements", []))
            }

    return {"error": f"No experience found at company: {company}"}


@mcp.tool()
def calculate_total_experience() -> Dict[str, Any]:
    """Calculate total years of experience and career progression"""
    experiences = RESUME_DATA["experience"]

    # Parse dates from first and last experience
    if experiences:
        latest = experiences[0]["duration"]
        earliest = experiences[-1]["duration"]

        # Extract start year from earliest
        earliest_year = int(earliest.split("/")[-1].split(" ")[0])

        # Check if still current role
        if "present" in latest.lower():
            current_year = datetime.now().year
            total_years = current_year - earliest_year
        else:
            latest_year = int(latest.split(" - ")[1].split("/")[-1])
            total_years = latest_year - earliest_year

        return {
            "total_years": total_years,
            "companies_worked": len([exp for exp in experiences if exp["company"] != "Beander"]),
            "roles_held": len(experiences),
            "current_role": experiences[0]["title"],
            "current_company": experiences[0]["company"],
            "career_progression": [{"title": exp["title"], "company": exp["company"]} for exp in experiences]
        }

    return {"error": "Unable to calculate experience"}


# === PROMPTS ===

@mcp.prompt()
def why_great_fit_for_ai_pm() -> str:
    """Generate a compelling answer for why Rishi is a great fit for an AI PM role"""
    return """Based on Rishi's resume, explain why he would be an excellent fit for an AI Product Manager role.

Focus on:
1. His hands-on AI/ML experience (92% accuracy underwriting model at Justworks)
2. Proven track record in regulated industries (fintech, insurance)
3. Experience scaling products from 0→1 and optimizing existing platforms
4. Leadership in AI adoption and training other PMs
5. Strong quantifiable business impact ($29M+ in revenue)
6. Technical depth (CS degree, technical PM background, coding experience)

Make the response compelling, specific, and backed by concrete examples from his experience."""


@mcp.prompt()
def interview_question(topic: str) -> str:
    """Generate an interview response based on Rishi's experience"""
    return f"""Using Rishi's resume, craft a strong interview response about: {topic}

Guidelines:
- Use specific examples from his experience
- Include quantifiable metrics where relevant
- Follow the STAR format (Situation, Task, Action, Result)
- Keep it concise but impactful
- Highlight relevant skills and achievements"""


@mcp.prompt()
def compare_to_job_description(job_requirements: str) -> str:
    """Compare Rishi's qualifications to specific job requirements"""
    return f"""Compare Rishi's qualifications to these job requirements:

{job_requirements}

For each requirement:
1. Indicate if Rishi meets it (Yes/Partial/No)
2. Provide specific evidence from his resume
3. Highlight any exceptional qualifications that exceed the requirements"""


@mcp.prompt()
def generate_cover_letter_points(company: str, role: str) -> str:
    """Generate key points for a cover letter"""
    return f"""Generate 3-5 compelling cover letter points for Rishi applying to {role} at {company}.

Each point should:
- Connect his specific experience to the role
- Include quantifiable achievements
- Demonstrate understanding of the company's needs
- Show his unique value proposition"""


# === ANALYTICS ===

# Track queries for analytics (in production, this would be stored in a database)
query_log = []

@mcp.tool()
def log_query(query: str, response_time_ms: Optional[int] = None) -> Dict[str, Any]:
    """Log a query for analytics purposes"""
    query_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "response_time_ms": response_time_ms
    }
    query_log.append(query_entry)

    return {
        "logged": True,
        "total_queries": len(query_log),
        "message": "Query logged for analytics"
    }


@mcp.tool()
def get_analytics_summary() -> Dict[str, Any]:
    """Get analytics summary of queries made to the resume server"""
    if not query_log:
        return {"message": "No queries logged yet"}

    # Analyze query patterns
    query_topics = {
        "ai_ml": 0,
        "experience": 0,
        "skills": 0,
        "metrics": 0,
        "contact": 0,
        "other": 0
    }

    for entry in query_log:
        query_lower = entry["query"].lower()
        if any(term in query_lower for term in ["ai", "ml", "machine learning", "model"]):
            query_topics["ai_ml"] += 1
        elif any(term in query_lower for term in ["experience", "work", "role", "company"]):
            query_topics["experience"] += 1
        elif "skill" in query_lower:
            query_topics["skills"] += 1
        elif any(term in query_lower for term in ["metric", "impact", "revenue", "number"]):
            query_topics["metrics"] += 1
        elif "contact" in query_lower:
            query_topics["contact"] += 1
        else:
            query_topics["other"] += 1

    # Calculate average response time
    response_times = [q["response_time_ms"] for q in query_log if q.get("response_time_ms")]
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    return {
        "total_queries": len(query_log),
        "query_topics": query_topics,
        "average_response_time_ms": avg_response_time,
        "first_query": query_log[0]["timestamp"] if query_log else None,
        "last_query": query_log[-1]["timestamp"] if query_log else None
    }


if __name__ == "__main__":
    # Run the server
    print("Starting Rishi's Resume MCP Server...")
    print("Server ready to answer questions about Rishi's qualifications for AI PM roles!")

    # FastMCP handles the async setup internally
    mcp.run()