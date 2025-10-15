#!/usr/bin/env python3
"""
Interactive test client for the Resume MCP Server
Allows testing server functions directly without MCP protocol
"""

import json
from pathlib import Path

# Import server functions directly
from server import (
    get_summary,
    get_experience,
    get_skills,
    get_education,
    get_contact,
    search_experience,
    get_ai_ml_experience,
    get_metrics_and_impact,
    search_by_skill,
    get_company_details,
    calculate_total_experience,
    RESUME_DATA
)

def test_interactive():
    """Interactive testing of server functions"""
    print("🚀 Resume MCP Server - Interactive Test Mode")
    print("=" * 50)
    print("\nAvailable commands:")
    print("  1. summary          - Get professional summary")
    print("  2. experience       - Get all work experience")
    print("  3. ai              - Get AI/ML experience")
    print("  4. metrics         - Get business impact metrics")
    print("  5. search <query>  - Search experience")
    print("  6. skills <category> - Get skills by category")
    print("  7. company <name>  - Get company details")
    print("  8. total           - Calculate total experience")
    print("  9. quit            - Exit")
    print("\n" + "=" * 50)

    while True:
        try:
            query = input("\n❓ Enter command (or 'quit'): ").strip().lower()

            if query == 'quit' or query == 'q':
                print("Goodbye!")
                break

            elif query == 'summary' or query == '1':
                print("\n📋 SUMMARY:")
                print(get_summary())

            elif query == 'experience' or query == '2':
                print("\n💼 EXPERIENCE:")
                print(get_experience())

            elif query == 'ai' or query == '3':
                print("\n🤖 AI/ML EXPERIENCE:")
                result = get_ai_ml_experience()
                print(json.dumps(result, indent=2))

            elif query == 'metrics' or query == '4':
                print("\n📊 BUSINESS IMPACT:")
                result = get_metrics_and_impact()
                print(json.dumps(result, indent=2))

            elif query.startswith('search ') or query == '5':
                if query == '5':
                    search_term = input("Search for: ").strip()
                else:
                    search_term = query[7:].strip()
                print(f"\n🔍 SEARCHING FOR: {search_term}")
                result = search_experience(search_term)
                print(json.dumps(result, indent=2))

            elif query.startswith('skills ') or query == '6':
                if query == '6':
                    category = input("Category (ai_ml/technical/domain/analytics/leadership): ").strip()
                else:
                    category = query[7:].strip()
                print(f"\n🎯 SKILLS - {category.upper()}:")
                print(get_skills(category))

            elif query.startswith('company ') or query == '7':
                if query == '7':
                    company = input("Company name: ").strip()
                else:
                    company = query[8:].strip()
                print(f"\n🏢 COMPANY DETAILS - {company}:")
                result = get_company_details(company)
                print(json.dumps(result, indent=2))

            elif query == 'total' or query == '8':
                print("\n⏱️  TOTAL EXPERIENCE:")
                result = calculate_total_experience()
                print(json.dumps(result, indent=2))

            else:
                # Try it as a general search
                print(f"\n🔍 SEARCHING: {query}")
                result = search_experience(query)
                if result['results_count'] > 0:
                    print(json.dumps(result, indent=2))
                else:
                    print("No results found. Try commands 1-9 or 'quit'")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit.")
        except Exception as e:
            print(f"Error: {e}")

def test_common_questions():
    """Test common hiring manager questions"""
    print("\n" + "=" * 50)
    print("📝 TESTING COMMON QUESTIONS")
    print("=" * 50)

    questions = [
        ("What AI experience does Rishi have?", get_ai_ml_experience),
        ("What companies has Rishi worked at?", lambda: search_experience("company")),
        ("What's Rishi's business impact?", get_metrics_and_impact),
    ]

    for question, func in questions:
        print(f"\n❓ {question}")
        result = func()
        if isinstance(result, dict):
            # Pretty print first few items
            if 'matches' in result and result['matches']:
                print(f"Found {len(result['matches'])} matches:")
                for match in result['matches'][:3]:
                    print(f"  • {match}")
            elif 'revenue_impact' in result:
                print(f"Revenue Impact: {', '.join(result['revenue_impact'][:3])}")
            else:
                print(json.dumps(result, indent=2)[:500] + "...")
        else:
            print(result[:500] + "..." if len(result) > 500 else result)

if __name__ == "__main__":
    print("\nChoose test mode:")
    print("1. Interactive mode")
    print("2. Test common questions")
    print("3. Both")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == '2':
        test_common_questions()
    elif choice == '3':
        test_common_questions()
        test_interactive()
    else:
        test_interactive()