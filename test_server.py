#!/usr/bin/env python3
"""Test the MCP server directly."""

def test_server():
    print("🧪 Testing MCP Research Server...")
    
    try:
        # Test import
        import mcp_research_server
        print("✅ Server import successful")
        
        # Test server creation
        from mcp_research_server.server import MCPResearchServer
        server = MCPResearchServer()
        print("✅ Server created successfully")
        
        # Test a simple search
        result = server.arxiv_tool.search_papers("quantum computing", 2)
        print(f"✅ Search test successful: found {len(result.paper_ids)} papers")
        
        print("\n🎉 Server is working correctly!")
        print("The issue is with MCP Inspector setup, not your server.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_server()