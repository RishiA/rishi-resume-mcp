# Resume as an MCP Server

I turned my resume into an API. Here's why that's interesting.

## The Problem

Resumes are terrible. They're PDFs that sit in ATS systems, parsed by regex that breaks on emdashes. Hiring managers spend 7 seconds scanning them. Those brave enough to read further play keyword bingo, hoping "ML experience" means something more than "I watched a YouTube video once."

Meanwhile, every interesting conversation about my background starts with "Tell me more about..." followed by 20 minutes of context that should have been discoverable in the first place.

## The Solution

Model Context Protocol (MCP) lets LLMs talk to external systems. I built a server that makes my resume queryable through natural language. Not a chatbot wrapper. Not a RAG tutorial. An actual protocol implementation with measurable retrieval accuracy.

```bash
git clone https://github.com/RishiA/rishi-resume-mcp.git
cd rishi-resume-mcp
python quickstart.py  # Working demo in 12 seconds
```

## What This Actually Does

Ask: **"What ML models has Rishi built?"**

Returns:
```
• Built ML-powered underwriting model with 92% accuracy [experience_justworks]
• Reduced manual underwriting workload by 85% [experience_justworks]
• Champion of AI adoption using Claude Code, Cursor [skills_ai_ml]
```

Notice the citations. Every claim traces back to a specific role. No hallucinations. No creative writing. Just structured data retrieval with provenance.

## The Engineering

**Evaluation Suite**: 25 hiring-manager questions with expected retrieval patterns. Not "does it feel right" but "does it retrieve the correct section in the top 3 results." Current performance:

- Retrieval@1: 84% (target: 90%)
- Retrieval@3: 96% (target: 98%)
- P50 latency: 47ms
- Zero network calls (local-only)

**Security**: Automated PII detection strips phone numbers. No SSNs. No accidents. Run `./scripts/verify_security.sh` for a 9-point security audit. This matters because one leaked phone number becomes 50 recruiting calls.

**Answer Format**: Bullets. Citations. 700 character limit. Why? Because hiring managers are busy people who appreciate density and verifiability.

## The Product Insight

Every PM talks about "data-driven decisions" and "metrics-oriented thinking." This demonstrates it. The evaluation harness alone shows more rigorous thinking about quality than most production systems.

More interesting: this pattern generalizes. Team pages. Documentation. Any structured information that people query repeatedly. The same architecture that powers my resume could power your company's knowledge base.

## Business Value

I shipped $XX M in revenue across three companies. Led 92% account migrations with zero downtime. Built systems handling 50-state compliance.

But you already knew that if you ran the query.

What you might not know: I approach product problems like this resume server. Identify the core issue (discoverability). Build something measurable (retrieval metrics). Ship it clean (no PII leaks). Then instrument everything.

## Try It Yourself

```python
# The interesting queries
"What's Rishi's experience with regulated industries?"
"Evidence of platform migrations at scale?"
"How does he measure success?"
```

Each returns structured data with citations. No fluff. No storytelling. Just facts with pointers to evidence.

## The Meta Point

This isn't really about my resume. It's about taking something broken (traditional CVs), applying engineering thinking (MCP + evaluation metrics), and shipping something better.

That's what I do for a living. This server is just the proof.

---

**Rishi Athanikar**
[LinkedIn](https://linkedin.com/in/rishiathanikar) | [Website](https://www.rishiathanikar.com)

*P.S. - Yes, this is overkill for a resume. That's the point. The best demonstration of product thinking is a product that demonstrates product thinking.*

*Confession: This README is deeply influenced by patio11's (Patrick McKenzie) writings.*