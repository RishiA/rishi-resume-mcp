# Setting up Resume MCP Server with Claude Desktop

## Prerequisites
- Claude Desktop app installed
- Python 3.8+ installed
- This repository cloned locally

## Step 1: Install Dependencies

```bash
cd /path/to/rishi-resume-mcp
pip install "mcp[cli]"
```

## Step 2: Configure Claude Desktop

1. Open Claude Desktop
2. Go to **Settings** → **Developer** → **MCP Servers**
3. Click **Edit Config** (or open the config file directly)

The config file location:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Step 3: Add Resume Server Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rishi-resume": {
      "command": "python",
      "args": ["/absolute/path/to/rishi-resume-mcp/server.py"],
      "env": {}
    }
  }
}
```

**Important**: Replace `/absolute/path/to/rishi-resume-mcp` with your actual path!

For example on macOS:
```json
{
  "mcpServers": {
    "rishi-resume": {
      "command": "python",
      "args": ["/Users/rishiathanikar/Documents/Github/rishi-resume-mcp/server.py"],
      "env": {}
    }
  }
}
```

## Step 4: Restart Claude Desktop

1. Completely quit Claude Desktop (Cmd+Q on Mac, Alt+F4 on Windows)
2. Start Claude Desktop again
3. Open a new conversation

## Step 5: Verify Connection

In a new Claude conversation, you should see a 🔌 icon indicating MCP servers are connected.

Try these queries:
- "Using the resume server, what AI/ML experience does Rishi have?"
- "Query the resume server for Rishi's revenue impact"
- "Search the resume server for experience with regulated industries"

## Troubleshooting

### Server Not Appearing
1. Check the config file syntax (valid JSON)
2. Ensure the path to server.py is absolute, not relative
3. Check Python is in your PATH: `which python` or `where python`

### Server Errors
1. Check the Claude Desktop logs:
   - **macOS**: `~/Library/Logs/Claude/`
   - **Windows**: `%LOCALAPPDATA%\Claude\logs\`

2. Test the server standalone:
   ```bash
   python /path/to/server.py
   # Should output: "Starting Rishi's Resume MCP Server..."
   ```

### Common Issues

**Issue**: "No module named 'mcp'"
**Fix**: Install the MCP package
```bash
pip install "mcp[cli]"
```

**Issue**: Server starts but doesn't respond
**Fix**: Ensure you're using the full MCP query format in Claude:
- ❌ "What's Rishi's experience?"
- ✅ "Using the resume server, what's Rishi's experience?"

## Example Queries for Claude Desktop

Once connected, try these:

```
1. "Query the resume server for Rishi's ML model achievements"

2. "Using the MCP resume server, search for platform migrations"

3. "Ask the resume server about revenue impact at Justworks"

4. "Get Rishi's total years of experience from the resume server"
```

## Advanced: Multiple Servers

You can run multiple MCP servers. Here's an example with both resume and another server:

```json
{
  "mcpServers": {
    "rishi-resume": {
      "command": "python",
      "args": ["/path/to/rishi-resume-mcp/server.py"],
      "env": {}
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "env": {}
    }
  }
}
```

## Development Tips

When developing/debugging:
1. Run `python test_server.py` first to ensure functions work
2. Check server starts: `python server.py`
3. Tail Claude logs while testing
4. Use explicit "resume server" mentions in queries