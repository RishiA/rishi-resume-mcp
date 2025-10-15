#!/usr/bin/env python3
"""
Quick Start Demo for Rishi's Resume Server
Run this to see example interactions with the resume
"""

import json
import time
from pathlib import Path

# Load resume data
with open("resume_data.json", "r") as f:
    resume_data = json.load(f)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def simulate_query(question, response_generator):
    """Simulate a query with timing"""
    print(f"❓ Question: {question}")
    start = time.time()
    response = response_generator()
    elapsed = (time.time() - start) * 1000
    print(f"💬 Response: {response}")
    print(f"⏱️  Response time: {elapsed:.0f}ms\n")
    return response

def demo_ai_experience():
    """Demo AI/ML experience queries"""
    print_section("🤖 AI/ML EXPERIENCE")

    # Query 1: AI Models
    simulate_query(
        "What AI models has Rishi built?",
        lambda: f"Rishi built an ML-powered underwriting model at Justworks achieving {resume_data['ai_experience']['models_built'][0]}. "
                f"He's also championed AI adoption using tools like {', '.join(resume_data['ai_experience']['tools_used'])}."
    )

    # Query 2: AI Leadership
    simulate_query(
        "How has Rishi championed AI adoption?",
        lambda: "Rishi has led AI adoption through: " + ", ".join(resume_data['ai_experience']['initiatives_led'][:2])
    )

def demo_business_impact():
    """Demo business impact queries"""
    print_section("💰 BUSINESS IMPACT")

    # Revenue Impact
    simulate_query(
        "What revenue has Rishi generated?",
        lambda: f"Key revenue impacts: {', '.join(resume_data['key_metrics']['revenue_impact'])}"
    )

    # Efficiency Gains
    simulate_query(
        "What efficiency improvements has Rishi delivered?",
        lambda: f"Major efficiency gains: {', '.join(resume_data['key_metrics']['efficiency_gains'][:3])}"
    )

def demo_experience_search():
    """Demo experience searching"""
    print_section("🏢 EXPERIENCE SEARCH")

    # Company search
    company = "Justworks"
    exp = next((e for e in resume_data['experience'] if company in e['company']), None)
    if exp:
        simulate_query(
            f"Tell me about Rishi's role at {company}",
            lambda: f"{exp['title']} at {exp['company']} ({exp['duration']}). "
                    f"Key achievement: {exp['achievements'][0]['description'] if exp['achievements'] else 'Multiple achievements'}"
        )

def demo_fit_for_role():
    """Demo fit for AI PM role"""
    print_section("🎯 FIT FOR AI PM ROLE")

    simulate_query(
        "Why is Rishi a great fit for an AI PM role?",
        lambda: "Top reasons: " + " | ".join(resume_data['unique_value_props']['for_ai_pm_role'][:3])
    )

def show_analytics():
    """Show analytics summary"""
    print_section("📊 ANALYTICS SUMMARY")

    print("Query Categories Demonstrated:")
    print("  • AI/ML Experience: 2 queries")
    print("  • Business Impact: 2 queries")
    print("  • Company Experience: 1 query")
    print("  • Role Fit: 1 query")
    print(f"\nTotal Queries: 6")
    print(f"Average Response Time: <100ms")
    print(f"Coverage: All major resume sections")

def main():
    """Run the complete demo"""
    print("\n" + "="*60)
    print("  🚀 RISHI'S RESUME MCP SERVER - QUICK START DEMO")
    print("="*60)
    print("\nThis demo shows example interactions with Rishi's resume.")
    print("The actual MCP server provides many more query capabilities!\n")

    input("Press Enter to start the demo...")

    # Run demos
    demo_ai_experience()
    demo_business_impact()
    demo_experience_search()
    demo_fit_for_role()
    show_analytics()

    print_section("✅ DEMO COMPLETE")
    print("To run the full MCP server:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run server: python server.py")
    print("\nOr use Docker: docker run -p 8000:8000 rishi-resume-mcp")
    print("\n🎯 Ready to explore Rishi's qualifications for your AI PM role!")

if __name__ == "__main__":
    main()