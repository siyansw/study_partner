#!/bin/bash
# Study Partner Launcher

echo "🎓 Starting Study Partner..."

# Start MCP server in background
python mcp_server.py &
MCP_PID=$!

echo "📚 Study Partner MCP server started (PID: $MCP_PID)"
echo "💡 You can now use Gemini CLI with study-partner tools"
echo ""
echo "Example commands:"
echo "  gemini -p 'Import documents from my study folder'"
echo "  gemini -p 'Generate a quiz on blockchain topics'"
echo "  gemini -p 'Show my mistake report'"
echo ""
echo "Press Ctrl+C to stop the server"

# Wait for interrupt
trap "kill $MCP_PID; echo 'Study Partner stopped'; exit 0" INT
wait $MCP_PID