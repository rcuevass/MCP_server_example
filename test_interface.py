#!/usr/bin/env python3
"""Simple web interface for testing MCP Research Server with auto-reload capability."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import traceback
import importlib
import sys


class MCPTestHandler(BaseHTTPRequestHandler):
    def reload_modules(self):
        """Reload MCP server modules to pick up changes."""
        try:
            # List of modules to reload
            modules_to_reload = [
                'mcp_research_server.server',
                'mcp_research_server.tools.arxiv_search',
                'mcp_research_server.tools.paper_info',
                'mcp_research_server.models',
                'mcp_research_server.config',
                'mcp_research_server.utils.file_handler',
                'mcp_research_server.utils.logger'
            ]

            # Reload each module if it's already imported
            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    print(f"🔄 Reloaded: {module_name}")

            return True
        except Exception as e:
            print(f"❌ Reload failed: {e}")
            return False

    def get_fresh_server(self):
        """Get a fresh server instance with reloaded modules."""
        try:
            # Reload modules first
            self.reload_modules()

            # Import fresh server
            from mcp_research_server.server import MCPResearchServer
            return MCPResearchServer()
        except Exception as e:
            print(f"❌ Failed to create fresh server: {e}")
            # Fall back to cached version
            from mcp_research_server.server import MCPResearchServer
            return MCPResearchServer()

    def get_base_html(self, results_content=""):
        """Get the complete HTML page with optional results."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCP Research Server Test Interface</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; text-align: center; }}
                .tool-section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; background: #fafafa; }}
                .tool-section h3 {{ margin-top: 0; color: #555; }}
                input, button {{ padding: 10px; margin: 5px; border: 1px solid #ccc; border-radius: 3px; }}
                button {{ background: #007cba; color: white; cursor: pointer; font-weight: bold; }}
                button:hover {{ background: #005a87; }}
                .result {{ margin: 20px 0; padding: 15px; background: #e8f4f8; border-left: 4px solid #007cba; border-radius: 3px; }}
                .error {{ background: #ffeaa7; border-left-color: #fdcb6e; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; max-height: 400px; overflow-y: auto; }}
                .status {{ text-align: center; padding: 10px; background: #d4edda; border-radius: 5px; margin-bottom: 20px; }}
                .use-id-btn {{ background: #28a745; margin-left: 10px; padding: 5px 10px; font-size: 12px; }}
                .use-id-btn:hover {{ background: #218838; }}
                .reload-btn {{ background: #ffc107; color: #212529; margin-left: 10px; }}
                .reload-btn:hover {{ background: #e0a800; }}
                .dev-section {{ background: #e3f2fd; border-left: 4px solid #2196f3; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔬 MCP Research Server Test Interface</h1>
                <div class="status">✅ Your MCP Server is running correctly!</div>

                <div class="tool-section dev-section">
                    <h3>🔄 Development Tools</h3>
                    <p>Auto-reload is enabled - code changes are automatically picked up!</p>
                    <form action="/reload" method="post" style="display: inline;">
                        <button type="submit" class="reload-btn">🔄 Manual Reload</button>
                    </form>
                    <small>💡 Use manual reload if you're experiencing caching issues</small>
                </div>

                <p style="text-align: center; color: #666;">Test your MCP server functionality - modules auto-reload on each request!</p>

                <div class="tool-section">
                    <h3>🔍 Search Papers</h3>
                    <p>Search for academic papers on ArXiv by topic</p>
                    <form action="/search" method="post">
                        <label>Topic: <input type="text" name="topic" value="machine learning" style="width: 300px;" placeholder="e.g., quantum computing, neural networks"></label><br><br>
                        <label>Max Results: <input type="number" name="max_results" value="5" min="1" max="20"></label><br><br>
                        <button type="submit">🔍 Search ArXiv Papers</button>
                    </form>
                </div>

                <div class="tool-section">
                    <h3>📄 Get Paper Information</h3>
                    <p>Get detailed information about a specific paper using its ID</p>
                    <form action="/info" method="post">
                        <label>Paper ID: <input type="text" name="paper_id" id="paper_id_input" placeholder="e.g., 2301.00001" style="width: 200px;"></label><br><br>
                        <button type="submit">📄 Get Paper Details</button>
                    </form>
                    <p><small>💡 Search for papers first, then click "Use This ID" buttons to auto-fill this field</small></p>
                </div>

                <div class="tool-section">
                    <h3>📊 Database Statistics</h3>
                    <p>View statistics about your stored papers database</p>
                    <form action="/stats" method="post">
                        <button type="submit">📊 Get Database Stats</button>
                    </form>
                </div>

                <div id="results">{results_content}</div>
            </div>

            <script>
            // Function to use a paper ID
            function usePaperId(paperId) {{
                console.log('Using paper ID:', paperId);
                const paperIdInput = document.getElementById('paper_id_input');
                if (paperIdInput) {{
                    paperIdInput.value = paperId;
                    paperIdInput.focus();
                    paperIdInput.scrollIntoView({{ behavior: 'smooth', block: 'center' }});

                    // Visual feedback
                    paperIdInput.style.backgroundColor = '#ffffcc';
                    setTimeout(() => {{
                        paperIdInput.style.backgroundColor = '';
                    }}, 1000);

                    alert('Paper ID "' + paperId + '" copied! Now click "Get Paper Details" button.');
                }} else {{
                    console.error('Could not find paper ID input field');
                    alert('Error: Could not find input field');
                }}
            }}

            // Auto-scroll to results when they appear
            function scrollToResults() {{
                const results = document.getElementById('results');
                if (results && results.innerHTML.trim() !== '') {{
                    results.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }}

            // Scroll to results on page load if they exist
            window.onload = function() {{
                scrollToResults();
            }};
            </script>
        </body>
        </html>
        """

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

            html = self.get_base_html()
            self.wfile.write(html.encode())

        elif self.path == '/status':
            self.send_json_response({"status": "MCP Research Server is running", "success": True})

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            # Get fresh server instance with reloaded modules
            server = self.get_fresh_server()

            if self.path == '/reload':
                # Manual reload endpoint
                success = self.reload_modules()
                if success:
                    results_html = """
                    <div class="result">
                        <h3>✅ Modules Reloaded Successfully</h3>
                        <p>All MCP server modules have been reloaded. Any code changes should now be active.</p>
                        <p><small>🔄 Auto-reload is always active, but manual reload can help with stubborn caching issues.</small></p>
                    </div>
                    """
                else:
                    results_html = """
                    <div class="result error">
                        <h3>❌ Reload Failed</h3>
                        <p>There was an error reloading modules. Check the console for details.</p>
                    </div>
                    """

                complete_html = self.get_base_html(results_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(complete_html.encode())
                return

            elif self.path == '/search':
                data = urllib.parse.parse_qs(post_data.decode())
                topic = data.get('topic', [''])[0]
                max_results = int(data.get('max_results', ['5'])[0])

                print(f"🔍 Searching for: '{topic}' (max: {max_results})")
                result = server.arxiv_tool.search_papers(topic, max_results)

                results_html = f"""
                <div class="result">
                    <h3>✅ Search Results for "{topic}"</h3>
                    <p><strong>Found {result.total_found} papers:</strong></p>
                    <ul>
                """

                for paper_id in result.paper_ids:
                    results_html += f'''<li>
                        <code>{paper_id}</code> 
                        <button class="use-id-btn" onclick="usePaperId('{paper_id}')">Use This ID</button>
                    </li>'''

                results_html += f"""
                    </ul>
                    <p><strong>📁 Results saved to:</strong> <code>{result.saved_to}</code></p>
                    <p><strong>🕐 Search completed at:</strong> {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><small>💡 Click "Use This ID" next to any paper to automatically fill the Paper ID field above</small></p>
                </div>
                """

                # Return complete page with results
                complete_html = self.get_base_html(results_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(complete_html.encode())

            elif self.path == '/info':
                data = urllib.parse.parse_qs(post_data.decode())
                paper_id = data.get('paper_id', [''])[0].strip()

                if not paper_id:
                    results_html = """
                    <div class="result error">
                        <h3>❌ No Paper ID Provided</h3>
                        <p>Please enter a paper ID first.</p>
                    </div>
                    """
                else:
                    print(f"📄 Getting info for paper: {paper_id}")
                    result = server.paper_info_tool.extract_info(paper_id)
                    result_data = json.loads(result)

                    if "error" not in result_data:
                        authors_list = result_data.get('authors', [])
                        authors_str = ', '.join(authors_list) if authors_list else 'N/A'

                        results_html = f"""
                        <div class="result">
                            <h3>📄 Paper Information</h3>
                            <h4>{result_data.get('title', 'N/A')}</h4>
                            <p><strong>Paper ID:</strong> <code>{result_data.get('paper_id', 'N/A')}</code></p>
                            <p><strong>Authors:</strong> {authors_str}</p>
                            <p><strong>Published:</strong> {result_data.get('published', 'N/A')}</p>
                            <p><strong>Category:</strong> {result_data.get('category', 'N/A')}</p>
                            <p><strong>PDF URL:</strong> <a href="{result_data.get('pdf_url', '#')}" target="_blank">{result_data.get('pdf_url', 'N/A')}</a></p>
                            <h4>Abstract:</h4>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 3px solid #007cba;">
                                <p>{result_data.get('summary', 'N/A')}</p>
                            </div>
                            <details style="margin-top: 20px;">
                                <summary style="cursor: pointer; font-weight: bold;">📋 View Raw JSON Data</summary>
                                <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; margin-top: 10px;">{json.dumps(result_data, indent=2)}</pre>
                            </details>
                        </div>
                        """
                    else:
                        results_html = f"""
                        <div class="result error">
                            <h3>❌ Paper Not Found</h3>
                            <p><strong>Error:</strong> {result_data.get('error', 'Unknown error')}</p>
                            <p><strong>Paper ID searched:</strong> <code>{paper_id}</code></p>
                            <p><strong>Error Type:</strong> {result_data.get('error_type', 'Unknown')}</p>
                            <p><small>💡 Make sure the paper ID is correct and that you've searched for papers first</small></p>
                        </div>
                        """

                # Return complete page with results
                complete_html = self.get_base_html(results_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(complete_html.encode())

            elif self.path == '/stats':
                print("📊 Getting database statistics")

                # Try the method first
                try:
                    result = server.paper_info_tool.get_database_stats()
                    stats_data = result
                    print("✅ Using get_database_stats method")
                except AttributeError:
                    print("⚠️ Method not found, using fallback implementation")
                    # Fallback implementation
                    topics = server.paper_info_tool.file_handler.list_all_topics()
                    total_papers = 0
                    topic_stats = []

                    for topic in topics:
                        stats = server.paper_info_tool.file_handler.get_topic_stats(topic)
                        topic_stats.append(stats)
                        total_papers += stats["paper_count"]

                    stats_data = {
                        "total_topics": len(topics),
                        "total_papers": total_papers,
                        "topics": topic_stats,
                        "generated_at": "fallback_implementation"
                    }

                results_html = f"""
                <div class="result">
                    <h3>📊 Database Statistics</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                        <div style="background: #e3f2fd; padding: 15px; border-radius: 5px;">
                            <h4 style="margin: 0; color: #1976d2;">Total Topics</h4>
                            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{stats_data.get('total_topics', 0)}</p>
                        </div>
                        <div style="background: #e8f5e8; padding: 15px; border-radius: 5px;">
                            <h4 style="margin: 0; color: #388e3c;">Total Papers</h4>
                            <p style="font-size: 24px; font-weight: bold; margin: 10px 0;">{stats_data.get('total_papers', 0)}</p>
                        </div>
                    </div>
                """

                if stats_data.get('topics'):
                    results_html += "<h4>📚 Topics Breakdown:</h4><ul>"
                    for topic in stats_data.get('topics', []):
                        results_html += f"""
                        <li style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px;">
                            <strong>{topic.get('topic', 'Unknown')}:</strong> {topic.get('paper_count', 0)} papers
                            <br><small>Last updated: {topic.get('last_updated', 'Unknown')}</small>
                        </li>
                        """
                    results_html += "</ul>"
                else:
                    results_html += "<p><em>No topics found. Search for some papers first!</em></p>"

                results_html += f"""
                    <details style="margin-top: 20px;">
                        <summary style="cursor: pointer; font-weight: bold;">📋 View Raw JSON Data</summary>
                        <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; margin-top: 10px;">{json.dumps(stats_data, indent=2)}</pre>
                    </details>
                </div>
                """

                # Return complete page with results
                complete_html = self.get_base_html(results_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(complete_html.encode())

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()

            error_html = f"""
            <div class="result error">
                <h3>❌ Server Error</h3>
                <p><strong>Error Message:</strong> {error_msg}</p>
                <p><strong>What happened:</strong> There was an error processing your request.</p>
                <details>
                    <summary style="cursor: pointer; font-weight: bold;">🔍 Technical Details</summary>
                    <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; margin-top: 10px;">{traceback.format_exc()}</pre>
                </details>
                <p><small>💡 Try the manual reload button or refresh the page and try again</small></p>
            </div>
            """

            # Return complete page with error
            complete_html = self.get_base_html(error_html)
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(complete_html.encode())

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def log_message(self, format, *args):
        # Suppress default HTTP server logging to keep console clean
        pass


def run_test_server(port=8000):
    """Run the MCP test server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPTestHandler)

    print("🌐 MCP Research Server Test Interface with Auto-Reload")
    print("=" * 60)
    print(f"🚀 Server running at: http://localhost:{port}")
    print(f"🔗 Open this URL in your browser to test your MCP server")
    print("🔄 Auto-reload enabled - code changes picked up automatically!")
    print("📊 Available features:")
    print("   • Search ArXiv papers by topic")
    print("   • Get detailed paper information")
    print("   • View database statistics")
    print("   • Auto-reload modules on each request")
    print("   • Manual reload button for stubborn cache issues")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Test server stopped")
        httpd.server_close()


if __name__ == "__main__":
    run_test_server()