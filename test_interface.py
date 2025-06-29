#!/usr/bin/env python3
"""Simple web interface for testing MCP Research Server (emoji-free version)."""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import traceback
from mcp_research_server.server import MCPResearchServer


class MCPTestHandler(BaseHTTPRequestHandler):
    def get_base_html(self, results_content=""):
        """Get the complete HTML page with optional results."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>[RESEARCH] MCP Research Server Test Interface</h1>
                <div class="status">[OK] Your MCP Server is running correctly!</div>
                <p style="text-align: center; color: #666;">Test your MCP server functionality without the MCP Inspector</p>

                <div class="tool-section">
                    <h3>[SEARCH] Search Papers</h3>
                    <p>Search for academic papers on ArXiv by topic</p>
                    <form action="/search" method="post">
                        <label>Topic: <input type="text" name="topic" value="machine learning" style="width: 300px;" placeholder="e.g., quantum computing, neural networks"></label><br><br>
                        <label>Max Results: <input type="number" name="max_results" value="5" min="1" max="20"></label><br><br>
                        <button type="submit">[SEARCH] Search ArXiv Papers</button>
                    </form>
                </div>

                <div class="tool-section">
                    <h3>[INFO] Get Paper Information</h3>
                    <p>Get detailed information about a specific paper using its ID</p>
                    <form action="/info" method="post">
                        <label>Paper ID: <input type="text" name="paper_id" id="paper_id_input" placeholder="e.g., 2301.00001" style="width: 200px;"></label><br><br>
                        <button type="submit">[INFO] Get Paper Details</button>
                    </form>
                    <p><small>[TIP] Search for papers first, then click "Use This ID" buttons to auto-fill this field</small></p>
                </div>

                <div class="tool-section">
                    <h3>[STATS] Database Statistics</h3>
                    <p>View statistics about your stored papers database</p>
                    <form action="/stats" method="post">
                        <button type="submit">[STATS] Get Database Stats</button>
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
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

            html = self.get_base_html()
            self.wfile.write(html.encode('utf-8'))

        elif self.path == '/status':
            self.send_json_response({"status": "MCP Research Server is running", "success": True})

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            server = MCPResearchServer()

            if self.path == '/search':
                data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                topic = data.get('topic', [''])[0]
                max_results = int(data.get('max_results', ['5'])[0])

                print(f"[SEARCH] Searching for: '{topic}' (max: {max_results})")
                result = server.arxiv_tool.search_papers(topic, max_results)

                results_html = f"""
                <div class="result">
                    <h3>[SUCCESS] Search Results for "{topic}"</h3>
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
                    <p><strong>[SAVED] Results saved to:</strong> <code>{result.saved_to}</code></p>
                    <p><strong>[TIME] Search completed at:</strong> {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><small>[TIP] Click "Use This ID" next to any paper to automatically fill the Paper ID field above</small></p>
                </div>
                """

                # Return complete page with results
                complete_html = self.get_base_html(results_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(complete_html.encode('utf-8'))

            elif self.path == '/info':
                data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                paper_id = data.get('paper_id', [''])[0].strip()

                if not paper_id:
                    results_html = """
                    <div class="result error">
                        <h3>[ERROR] No Paper ID Provided</h3>
                        <p>Please enter a paper ID first.</p>
                    </div>
                    """
                else:
                    print(f"[INFO] Getting info for paper: {paper_id}")
                    result = server.paper_info_tool.extract_info(paper_id)
                    result_data = json.loads(result)

                    if "error" not in result_data:
                        authors_list = result_data.get('authors', [])
                        authors_str = ', '.join(authors_list) if authors_list else 'N/A'

                        results_html = f"""
                        <div class="result">
                            <h3>[PAPER] Paper Information</h3>
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
                                <summary style="cursor: pointer; font-weight: bold;">[DATA] View Raw JSON Data</summary>
                                <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; margin-top: 10px;">{json.dumps(result_data, indent=2)}</pre>
                            </details>
                        </div>
                        """
                    else:
                        results_html = f"""
                        <div class="result error">
                            <h3>[ERROR] Paper Not Found</h3>
                            <p><strong>Error:</strong> {result_data.get('error', 'Unknown error')}</p>
                            <p><strong>Paper ID searched:</strong> <code>{paper_id}</code></p>
                            <p><strong>Error Type:</strong> {result_data.get('error_type', 'Unknown')}</p>
                            <p><small>[TIP] Make sure the paper ID is correct and that you've searched for papers first</small></p>
                        </div>
                        """

                # Return complete page with results
                complete_html = self.get_base_html(results_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(complete_html.encode('utf-8'))

            elif self.path == '/stats':
                print("[STATS] Getting database statistics")

                # Try the method first
                try:
                    result = server.paper_info_tool.get_database_stats()
                    stats_data = result
                    print("[SUCCESS] Using get_database_stats method")
                except AttributeError:
                    print("[FALLBACK] Method not found, using fallback implementation")
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
                    <h3>[STATS] Database Statistics</h3>
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
                    results_html += "<h4>[TOPICS] Topics Breakdown:</h4><ul>"
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
                        <summary style="cursor: pointer; font-weight: bold;">[DATA] View Raw JSON Data</summary>
                        <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; margin-top: 10px;">{json.dumps(stats_data, indent=2)}</pre>
                    </details>
                </div>
                """

                # Return complete page with results
                complete_html = self.get_base_html(results_html)
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(complete_html.encode('utf-8'))

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            traceback.print_exc()

            error_html = f"""
            <div class="result error">
                <h3>[ERROR] Server Error</h3>
                <p><strong>Error Message:</strong> {error_msg}</p>
                <p><strong>What happened:</strong> There was an error processing your request.</p>
                <details>
                    <summary style="cursor: pointer; font-weight: bold;">[DEBUG] Technical Details</summary>
                    <pre style="background: #f1f3f4; padding: 15px; border-radius: 5px; margin-top: 10px;">{traceback.format_exc()}</pre>
                </details>
                <p><small>[TIP] Try refreshing the page and trying again</small></p>
            </div>
            """

            # Return complete page with error
            complete_html = self.get_base_html(error_html)
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(complete_html.encode('utf-8'))

    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def log_message(self, format, *args):
        # Suppress default HTTP server logging to keep console clean
        pass


def run_test_server(port=8000):
    """Run the MCP test server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPTestHandler)

    print("[SERVER] MCP Research Server Test Interface (Simple Version)")
    print("=" * 70)
    print(f"[URL] Server running at: http://localhost:{port}")
    print(f"[INFO] Open this URL in your browser to test your MCP server")
    print("[FEATURES] Available features:")
    print("   * Search ArXiv papers by topic")
    print("   * Get detailed paper information")
    print("   * View database statistics")
    print("   * No special characters - should display correctly on all systems")
    print("[STOP] Press Ctrl+C to stop the server")
    print("=" * 70)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Test server stopped")
        httpd.server_close()


if __name__ == "__main__":
    run_test_server()