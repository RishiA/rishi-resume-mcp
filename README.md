# 🚀 Rishi's Interactive Resume MCP Server

An innovative, AI-powered resume server built with the Model Context Protocol (MCP) - demonstrating technical depth and product thinking for AI PM roles.

## 🎯 Why This Approach?

As an AI Product Manager candidate, I built this to showcase:
- **Technical Understanding**: Hands-on implementation of cutting-edge AI infrastructure (MCP)
- **Product Thinking**: Interactive > static PDF, with analytics and evaluation metrics
- **AI/ML Expertise**: Practical demonstration of my experience building AI-powered systems
- **User-Centric Design**: Multiple deployment options for easy access by hiring managers

## 🔥 Key Features

### 📊 Interactive Querying
- Ask natural language questions about my experience
- Get specific details about AI/ML projects, revenue impact, and technical skills
- Search by company, skill, or achievement

### 🤖 AI/ML Highlights
- **92% accuracy ML-powered underwriting model** at Justworks
- Champion of AI adoption with Claude Code/Cursor implementation
- $29M+ in quantifiable revenue impact across roles

### 📈 Built-in Analytics
- Track which sections get queried most
- Response time metrics
- Usage patterns to understand what interests viewers

### ✅ Evaluation Suite
- 13 pre-built test cases with expected outcomes
- Performance metrics and scoring
- Validates server accuracy and completeness

## 🚀 Quick Start (30 Seconds!)

### Option 1: Docker (Recommended)
```bash
# Pull and run with one command
docker run -p 8000:8000 rishiathanikar/resume-mcp

# Or build locally
docker build -t rishi-resume .
docker run -p 8000:8000 rishi-resume
```

### Option 2: Python
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

### Option 3: Using UV (Fast Python package manager)
```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run directly
uv run server.py
```

## 💭 Sample Questions to Try

### AI/ML Experience
- "What AI models has Rishi built and deployed?"
- "Tell me about the underwriting model at Justworks"
- "How has Rishi championed AI adoption?"

### Business Impact
- "What's Rishi's track record for revenue generation?"
- "Show me examples of cost savings Rishi has delivered"
- "What operational efficiency improvements has Rishi made?"

### Product Leadership
- "What 0→1 products has Rishi launched?"
- "Tell me about Rishi's experience with platform migrations"
- "How many users have Rishi's products served?"

### Domain Expertise
- "What's Rishi's experience with regulated industries?"
- "Tell me about Rishi's fintech and insurance experience"
- "Has Rishi worked with compliance systems?"

## 📁 Project Structure

```
rishi-resume-mcp/
├── server.py              # Main MCP server with resume querying
├── resume_data.json       # Structured resume data
├── resume.md             # Markdown version for readability
├── evaluations.py        # Test suite with 13 test cases
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
├── demo/
│   ├── sample_questions.json   # Categorized questions
│   └── sample_questions.md     # Questions in markdown
└── config/
    └── claude_desktop_config.json  # Claude Desktop integration
```

## 🔧 Available Tools & Resources

### Resources (Data Access)
- `resume://summary` - Professional summary
- `resume://experience` - Complete work history
- `resume://skills/{category}` - Skills by category
- `resume://education` - Educational background
- `resume://contact` - Contact information

### Tools (Interactive Queries)
- `search_experience(query)` - Search work history
- `get_ai_ml_experience()` - All AI/ML related work
- `get_metrics_and_impact()` - Quantifiable achievements
- `search_by_skill(skill)` - Find experiences by skill
- `get_company_details(company)` - Detailed role information
- `calculate_total_experience()` - Career progression analysis

### Prompts (AI-Generated Responses)
- `why_great_fit_for_ai_pm()` - Compelling fit analysis
- `interview_question(topic)` - STAR format responses
- `compare_to_job_description(requirements)` - Role matching
- `generate_cover_letter_points(company, role)` - Tailored talking points

## 📊 Evaluation Metrics

Run the evaluation suite to see server performance:

```python
python evaluations.py
```

Expected performance:
- **Pass Rate**: >85% on all test cases
- **Response Time**: <100ms average
- **Category Coverage**: All resume sections queryable
- **Keyword Accuracy**: >70% match rate

## 🌐 Deployment Options

### For Sharing with Hiring Managers

1. **Replit**: One-click deployment with shareable link
2. **Railway/Render**: Always-on professional hosting
3. **GitHub Codespaces**: Run directly in browser
4. **Local Docker**: Simple container deployment

## 🎯 What Makes Me Unique for AI PM Roles

1. **Hands-on AI/ML Experience**: Built and deployed production ML models with measurable impact
2. **Regulated Industry Expertise**: 10+ years in fintech/insurance with compliance systems
3. **Proven Scale**: Products serving 300K+ MAU, $20M+ payment volume
4. **Technical Depth**: CS degree + hands-on coding with modern AI tools
5. **Business Impact**: $29M+ in revenue generation and optimization
6. **Innovation Leader**: 0→1 products, platform migrations, AI adoption champion

## 📬 Contact

**Rishi Athanikar**
- LinkedIn: [linkedin.com/in/rishiathanikar](https://linkedin.com/in/rishiathanikar)
- Website: [rishiathanikar.com](https://www.rishiathanikar.com)

## 🔒 Privacy Note

This server contains publicly available resume information. No sensitive data is included.

---

*Built with MCP (Model Context Protocol) - Demonstrating technical innovation for AI Product Management*