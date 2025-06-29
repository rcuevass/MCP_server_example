# MCP Research Server

A near production-ready Model Context Protocol (MCP) server for ArXiv paper research.

This repo is motivated by, and heavily dependent on the
[MCP: Build Rich-Context AI Apps with Anthropic](https://www.deeplearning.ai/short-courses/mcp-build-rich-context-ai-apps-with-anthropic/) 
short DeepLearning.AI course. It is an attempt to have a modularized version of the chatbot and with production-ready
code.

## Quick Start

1. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   cp .env.example .env
   ```

2. **Run the Server**:
   ```bash
   python -m mcp_research_server
   ```

3. **Test with MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector python -m mcp_research_server
   ```

## Available Tools

- **search_papers**: Search ArXiv for papers on a topic
- **extract_info**: Get detailed information about a specific paper
- **get_database_stats**: View database statistics

## Example Usage

```python
# Search for papers
search_papers(topic="machine learning", max_results=10)

# Get paper details
extract_info(paper_id="2301.00001")

# View database statistics
get_database_stats()
```

## Configuration

Edit `.env` file to customize:
- `MCP_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_ARXIV_MAX_RESULTS`: Default number of search results
- `MCP_SERVER_NAME`: Server name for MCP

## Integration with Claude Desktop

Add to Claude Desktop configuration:

```json
{
  "mcpServers": {
    "research": {
      "command": "python",
      "args": ["-m", "mcp_research_server"],
      "cwd": "/path/to/mcp_research_server"
    }
  }
}
```

For more details, see the complete documentation in the project files.
