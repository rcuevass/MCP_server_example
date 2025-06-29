#!/usr/bin/env python3
"""
Standalone usage examples for MCP Research Server
Use your research tools directly without external dependencies!
"""

from mcp_research_server.server import MCPResearchServer
import json
from datetime import datetime


def demo_basic_usage():
    """Basic research workflow demonstration."""
    print("🔬 MCP Research Server - Standalone Demo")
    print("=" * 50)

    # Initialize server
    server = MCPResearchServer()
    print("✅ Server initialized successfully")

    # Example 1: Search for papers
    print("\n🔍 Searching for papers on 'quantum computing'...")
    search_result = server.arxiv_tool.search_papers("quantum computing", 3)

    print(f"✅ Found {len(search_result.paper_ids)} papers:")
    for i, paper_id in enumerate(search_result.paper_ids, 1):
        print(f"   {i}. {paper_id}")

    # Example 2: Get paper details
    if search_result.paper_ids:
        first_paper = search_result.paper_ids[0]
        print(f"\n📄 Getting details for paper: {first_paper}")

        paper_info = server.paper_info_tool.extract_info(first_paper)
        paper_data = json.loads(paper_info)

        if "error" not in paper_data:
            print(f"   Title: {paper_data.get('title', 'N/A')}")
            print(f"   Authors: {', '.join(paper_data.get('authors', []))}")
            print(f"   Published: {paper_data.get('published', 'N/A')}")
            print(f"   PDF: {paper_data.get('pdf_url', 'N/A')}")
        else:
            print(f"   ⚠️ {paper_data.get('error', 'Unknown error')}")

    # Example 3: Database stats
    print(f"\n📊 Database Statistics:")
    stats = server.paper_info_tool.get_database_stats()
    print(f"   Total topics: {stats.get('total_topics', 0)}")
    print(f"   Total papers: {stats.get('total_papers', 0)}")

    print(f"\n🎉 Demo completed! Papers saved to: {search_result.saved_to}")


def interactive_research_tool():
    """Interactive command-line research tool."""
    print("🔬 Interactive Research Tool")
    print("=" * 40)
    print("Commands:")
    print("  search <topic> [max_results] - Search for papers")
    print("  info <paper_id>              - Get paper details")
    print("  stats                        - Show database stats")
    print("  topics                       - List all topics")
    print("  export <paper_id> <format>   - Export paper (json/bibtex/plain)")
    print("  quit                         - Exit")
    print("=" * 40)

    server = MCPResearchServer()

    while True:
        try:
            command = input("\n📝 Enter command: ").strip().split()

            if not command:
                continue

            cmd = command[0].lower()

            if cmd == "quit":
                print("👋 Goodbye!")
                break

            elif cmd == "search":
                if len(command) < 2:
                    print("❌ Usage: search <topic> [max_results]")
                    continue

                topic = " ".join(command[1:-1]) if len(command) > 2 and command[-1].isdigit() else " ".join(command[1:])
                max_results = int(command[-1]) if len(command) > 2 and command[-1].isdigit() else 5

                print(f"🔍 Searching for '{topic}' (max: {max_results})...")
                result = server.arxiv_tool.search_papers(topic, max_results)

                print(f"✅ Found {len(result.paper_ids)} papers:")
                for i, paper_id in enumerate(result.paper_ids, 1):
                    print(f"   {i}. {paper_id}")

            elif cmd == "info":
                if len(command) != 2:
                    print("❌ Usage: info <paper_id>")
                    continue

                paper_id = command[1]
                print(f"📄 Getting info for: {paper_id}")

                info_result = server.paper_info_tool.extract_info(paper_id)
                data = json.loads(info_result)

                if "error" not in data:
                    print(f"   📋 Title: {data.get('title', 'N/A')}")
                    print(f"   👥 Authors: {', '.join(data.get('authors', []))}")
                    print(f"   📅 Published: {data.get('published', 'N/A')}")
                    print(f"   🏷️  Category: {data.get('category', 'N/A')}")
                    print(f"   🔗 PDF: {data.get('pdf_url', 'N/A')}")
                    print(f"   📝 Abstract: {data.get('summary', 'N/A')[:200]}...")
                else:
                    print(f"   ❌ {data.get('error', 'Unknown error')}")

            elif cmd == "stats":
                print("📊 Database Statistics:")
                stats = server.paper_info_tool.get_database_stats()
                print(f"   📁 Total topics: {stats.get('total_topics', 0)}")
                print(f"   📄 Total papers: {stats.get('total_papers', 0)}")

                for topic in stats.get('topics', []):
                    print(f"   📚 {topic.get('topic', 'Unknown')}: {topic.get('paper_count', 0)} papers")

            elif cmd == "topics":
                topics = server.paper_info_tool.file_handler.list_all_topics()
                if topics:
                    print("📁 Available topics:")
                    for topic in topics:
                        print(f"   📚 {topic}")
                else:
                    print("📁 No topics found. Search for papers first!")

            elif cmd == "export":
                if len(command) != 3:
                    print("❌ Usage: export <paper_id> <format>")
                    print("   Formats: json, bibtex, plain")
                    continue

                paper_id, format_type = command[1], command[2]

                if format_type not in ["json", "bibtex", "plain"]:
                    print("❌ Format must be: json, bibtex, or plain")
                    continue

                print(f"📤 Exporting {paper_id} as {format_type}...")
                result = server.paper_info_tool.export_paper_data(paper_id, format_type)

                if result:
                    print("✅ Export result:")
                    print("-" * 40)
                    print(result)
                    print("-" * 40)
                else:
                    print(f"❌ Paper {paper_id} not found")

            else:
                print(f"❌ Unknown command: {cmd}")
                print("   Type 'quit' to exit or try: search, info, stats, topics, export")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def batch_research_example():
    """Example of batch research workflow."""
    print("🔬 Batch Research Example")
    print("=" * 40)

    server = MCPResearchServer()

    # Research multiple topics
    topics = ["machine learning", "quantum computing", "neural networks"]
    all_papers = {}

    print("🔍 Searching multiple topics...")
    for topic in topics:
        print(f"   Searching: {topic}")
        result = server.arxiv_tool.search_papers(topic, 3)
        all_papers[topic] = result.paper_ids
        print(f"   Found: {len(result.paper_ids)} papers")

    # Get details for first paper from each topic
    print(f"\n📄 Getting details for first paper from each topic...")
    for topic, papers in all_papers.items():
        if papers:
            print(f"\n📚 Topic: {topic}")
            paper_info = server.paper_info_tool.extract_info(papers[0])
            data = json.loads(paper_info)

            if "error" not in data:
                print(f"   📋 {data.get('title', 'N/A')}")
                print(f"   👥 {', '.join(data.get('authors', [])[:2])}...")
                print(f"   📅 {data.get('published', 'N/A')}")
            else:
                print(f"   ❌ {data.get('error', 'Paper not found')}")

    # Final stats
    print(f"\n📊 Research Summary:")
    stats = server.paper_info_tool.get_database_stats()
    print(f"   📁 Total topics in database: {stats.get('total_topics', 0)}")
    print(f"   📄 Total papers collected: {stats.get('total_papers', 0)}")


def create_research_report():
    """Generate a simple research report."""
    print("📊 Generating Research Report")
    print("=" * 40)

    server = MCPResearchServer()
    stats = server.paper_info_tool.get_database_stats()

    report = f"""
RESEARCH DATABASE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
={'=' * 50}

OVERVIEW
--------
Total Topics: {stats.get('total_topics', 0)}
Total Papers: {stats.get('total_papers', 0)}

TOPIC BREAKDOWN
---------------
"""

    for topic in stats.get('topics', []):
        report += f"• {topic.get('topic', 'Unknown')}: {topic.get('paper_count', 0)} papers\n"

    if not stats.get('topics'):
        report += "No topics found. Start by searching for papers!\n"

    report += f"\n{'=' * 50}\nReport generated by MCP Research Server\n"

    print(report)

    # Save report to file
    with open("research_report.txt", "w") as f:
        f.write(report)

    print("💾 Report saved to: research_report.txt")


if __name__ == "__main__":
    print("🔬 MCP Research Server - Standalone Usage Options")
    print("=" * 60)
    print("Choose an option:")
    print("1. Basic demo")
    print("2. Interactive research tool")
    print("3. Batch research example")
    print("4. Generate research report")
    print("5. Run web interface")

    choice = input("\nEnter choice (1-5): ").strip()

    if choice == "1":
        demo_basic_usage()
    elif choice == "2":
        interactive_research_tool()
    elif choice == "3":
        batch_research_example()
    elif choice == "4":
        create_research_report()
    elif choice == "5":
        print("\n🌐 Starting web interface...")
        print("Run: python test_interface.py")
        print("Then open: http://localhost:8000")
    else:
        print("❌ Invalid choice. Please run again and choose 1-5.")