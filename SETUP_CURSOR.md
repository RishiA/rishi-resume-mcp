# Using Resume MCP Server with Cursor IDE

## Overview

Cursor doesn't natively support MCP servers like Claude Desktop does, but you can integrate the resume server functionality in several ways.

## Option 1: Direct Python Integration (Recommended)

### Setup

1. Open your project in Cursor
2. Open the terminal in Cursor (Cmd+` or View → Terminal)
3. Install dependencies:
```bash
pip install "mcp[cli]"
```

### Usage in Cursor

Create a helper file `cursor_helper.py`:

```python
# cursor_helper.py
import sys
sys.path.append('/path/to/rishi-resume-mcp')

from server import (
    get_ai_ml_experience,
    search_experience,
    get_metrics_and_impact,
    get_company_details
)

# Now you can use these functions directly in Cursor's AI chat
# Example: "Using get_ai_ml_experience(), show me Rishi's AI work"
```

Then in Cursor's AI chat (Cmd+K), you can:
- Reference the functions: `@cursor_helper.py`
- Ask: "Run get_ai_ml_experience() and summarize the results"

## Option 2: Custom Cursor Commands

### Create Custom Commands

1. Create `.cursor/commands.json` in your project:

```json
{
  "commands": [
    {
      "name": "Resume: AI Experience",
      "command": "python -c \"from server import get_ai_ml_experience; import json; print(json.dumps(get_ai_ml_experience(), indent=2))\"",
      "cwd": "/path/to/rishi-resume-mcp"
    },
    {
      "name": "Resume: Search",
      "command": "python -c \"from server import search_experience; import json; import sys; query = ' '.join(sys.argv[1:]); print(json.dumps(search_experience(query), indent=2))\"",
      "cwd": "/path/to/rishi-resume-mcp",
      "args": true
    },
    {
      "name": "Resume: Metrics",
      "command": "python -c \"from server import get_metrics_and_impact; import json; print(json.dumps(get_metrics_and_impact(), indent=2))\"",
      "cwd": "/path/to/rishi-resume-mcp"
    }
  ]
}
```

2. Run via Command Palette (Cmd+Shift+P → "Run Custom Command")

## Option 3: Interactive Terminal Session

### Quick Access Script

Create `cursor_resume.py`:

```python
#!/usr/bin/env python3
"""
Cursor IDE Resume Query Interface
"""

import json
import sys
import os

# Add resume server to path
sys.path.insert(0, '/path/to/rishi-resume-mcp')

from server import *

def query(question):
    """Quick query function for Cursor terminal"""
    question_lower = question.lower()

    if 'ai' in question_lower or 'ml' in question_lower:
        return json.dumps(get_ai_ml_experience(), indent=2)
    elif 'metric' in question_lower or 'impact' in question_lower:
        return json.dumps(get_metrics_and_impact(), indent=2)
    elif 'compan' in question_lower:
        companies = ["Justworks", "Stash", "Casper", "Peet's"]
        results = {}
        for company in companies:
            results[company] = get_company_details(company)
        return json.dumps(results, indent=2)
    else:
        return json.dumps(search_experience(question), indent=2)

# If run directly, take command line argument
if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = query(" ".join(sys.argv[1:]))
        print(result)
    else:
        print("Usage: python cursor_resume.py <question>")
        print("Example: python cursor_resume.py 'AI experience'")
```

Then in Cursor's terminal:
```bash
python cursor_resume.py "What AI models has Rishi built?"
```

## Option 4: Cursor AI Context

### Add Resume Data as Context

1. Open `resume_data.json` in Cursor
2. In Cursor Chat (Cmd+K), reference it: `@resume_data.json`
3. Ask questions directly:
   - "Based on @resume_data.json, what ML models has Rishi built?"
   - "Analyze @resume_data.json and list revenue impact"

### Create Context Snippets

Create `.cursor/context/resume_queries.md`:

```markdown
# Resume Query Templates

## AI/ML Experience
Look in resume_data.json → ai_experience → models_built, tools_used, initiatives_led

## Revenue Impact
Look in resume_data.json → key_metrics → revenue_impact

## Company Experience
Look in resume_data.json → experience → filter by company name

## Skills
Look in resume_data.json → skills → [category]
```

Reference this in Cursor chat: `@resume_queries.md`

## Option 5: VSCode/Cursor Extension (Advanced)

Create a simple extension that wraps the MCP server:

1. Create extension structure:
```
resume-mcp-extension/
├── package.json
├── extension.js
└── README.md
```

2. `package.json`:
```json
{
  "name": "resume-mcp",
  "version": "0.1.0",
  "main": "./extension.js",
  "contributes": {
    "commands": [
      {
        "command": "resume.queryAI",
        "title": "Resume: Query AI Experience"
      },
      {
        "command": "resume.queryMetrics",
        "title": "Resume: Query Business Metrics"
      }
    ]
  }
}
```

3. `extension.js`:
```javascript
const vscode = require('vscode');
const { exec } = require('child_process');

function activate(context) {
    let queryAI = vscode.commands.registerCommand('resume.queryAI', () => {
        exec('python /path/to/rishi-resume-mcp/test_server.py', (err, stdout) => {
            vscode.window.showInformationMessage(stdout);
        });
    });

    context.subscriptions.push(queryAI);
}

module.exports = { activate };
```

## Best Practices for Cursor

1. **Use @-mentions**: Reference files directly in Cursor chat
   - `@server.py` - Reference the server code
   - `@resume_data.json` - Reference the data
   - `@test_server.py` - Reference test functions

2. **Create Snippets**: Save common queries as snippets
   ```python
   # .cursor/snippets/resume_ai.py
   from server import get_ai_ml_experience
   print(get_ai_ml_experience())
   ```

3. **Terminal Integration**: Keep a terminal tab open with:
   ```bash
   python test_server.py
   ```

4. **Cursor Composer**: Use Composer mode (Cmd+I) and reference:
   - "Using the functions in @server.py, analyze Rishi's AI experience"
   - "Run @test_server.py and show me revenue metrics"

## Example Cursor Workflow

1. Open Cursor in the resume-mcp directory
2. In Cursor Chat (Cmd+K):
   ```
   @server.py Can you run get_ai_ml_experience() and format the results?
   ```
3. Or in Composer (Cmd+I):
   ```
   Using @resume_data.json, create a summary of Rishi's platform migrations
   ```

## Debugging in Cursor

1. Set breakpoints in `server.py`
2. Run in debug mode:
   ```bash
   python -m debugpy --listen 5678 --wait-for-client test_server.py
   ```
3. Attach Cursor's debugger to port 5678

## Quick Test

In Cursor's terminal:
```bash
# Test that imports work
python -c "from server import get_ai_ml_experience; print('✅ Server loads correctly')"

# Run interactive test
python test_server.py
```

---

**Note**: While Cursor doesn't have native MCP support like Claude Desktop, these integration methods let you effectively query and work with the resume data within the IDE.