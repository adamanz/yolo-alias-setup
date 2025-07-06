#!/bin/bash

# Script to add 'yolo' alias for Claude with MCP servers
# Supports bash, zsh, and fish shells

# Detect the user's shell
USER_SHELL=$(basename "$SHELL")

# Define the alias
ALIAS_NAME="yolo"

# Function to add alias to a file
add_alias_to_file() {
    local file=$1
    
    # Check if alias already exists
    if grep -q "^alias $ALIAS_NAME=" "$file" 2>/dev/null || grep -q "^alias $ALIAS_NAME " "$file" 2>/dev/null; then
        echo "✓ Alias '$ALIAS_NAME' already exists in $file"
        echo "  Updating to latest version..."
        # Remove old alias
        sed -i.bak "/^alias $ALIAS_NAME=/d" "$file"
    fi
    
    # Add the new alias with proper escaping
    echo "alias $ALIAS_NAME='ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions --mcp-config \"{ \\\"mcpServers\\\": { \\\"messages\\\": { \\\"command\\\": \\\"uv\\\", \\\"args\\\": [\\\"run\\\", \\\"mac-messages-mcp\\\"] }, \\\"playwright\\\": { \\\"command\\\": \\\"npx\\\", \\\"args\\\": [\\\"-y\\\", \\\"@executeautomation/playwright-mcp-server\\\"] }, \\\"box\\\": { \\\"command\\\": \\\"uv\\\", \\\"args\\\": [\\\"--directory\\\", \\\"/Users/adamanzuoni/mcp-server-box\\\", \\\"run\\\", \\\"src/mcp_server_box.py\\\"] }, \\\"replicate\\\": { \\\"command\\\": \\\"npx\\\", \\\"args\\\": [\\\"-y\\\", \\\"replicate-mcp\\\"] } } }\"'" >> "$file"
    echo "✓ Added/Updated '$ALIAS_NAME' alias in $file"
}

# Function to add fish function
add_fish_function() {
    local fish_config="$HOME/.config/fish/config.fish"
    
    # Create fish config directory if it doesn't exist
    mkdir -p "$HOME/.config/fish"
    
    # Check if alias already exists
    if grep -q "^alias $ALIAS_NAME " "$fish_config" 2>/dev/null; then
        echo "✓ Alias '$ALIAS_NAME' already exists in $fish_config"
        echo "  Updating to latest version..."
        # Remove old alias
        sed -i.bak "/^alias $ALIAS_NAME /d" "$fish_config"
    fi
    
    # Add the new alias for fish
    echo "alias $ALIAS_NAME 'ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions --mcp-config \"{ \\\"mcpServers\\\": { \\\"messages\\\": { \\\"command\\\": \\\"uv\\\", \\\"args\\\": [\\\"run\\\", \\\"mac-messages-mcp\\\"] }, \\\"playwright\\\": { \\\"command\\\": \\\"npx\\\", \\\"args\\\": [\\\"-y\\\", \\\"@executeautomation/playwright-mcp-server\\\"] }, \\\"box\\\": { \\\"command\\\": \\\"uv\\\", \\\"args\\\": [\\\"--directory\\\", \\\"/Users/adamanzuoni/mcp-server-box\\\", \\\"run\\\", \\\"src/mcp_server_box.py\\\"] }, \\\"replicate\\\": { \\\"command\\\": \\\"npx\\\", \\\"args\\\": [\\\"-y\\\", \\\"replicate-mcp\\\"] } } }\"'" >> "$fish_config"
    echo "✓ Added/Updated '$ALIAS_NAME' alias in $fish_config"
}

echo "Setting up 'yolo' alias for Claude with MCP servers"
echo "Detected shell: $USER_SHELL"
echo ""
echo "This alias includes:"
echo "  - Background tasks enabled"
echo "  - Dangerous permissions skipped"
echo "  - MCP servers: messages, playwright, box, replicate"
echo ""
echo "Note: HTTP MCP servers (like deepwiki, context7) should be added separately via:"
echo "  claude mcp add -s user -t http deepwiki https://mcp.deepwiki.com/mcp"
echo "  claude mcp add -s user -t http context7 https://mcp.context7.com/mcp"
echo ""
echo "Note: For Replicate MCP server, set your API token as an environment variable:"
echo "  export REPLICATE_API_TOKEN='your-api-token-here'"
echo ""

case "$USER_SHELL" in
    bash)
        add_alias_to_file "$HOME/.bashrc"
        echo ""
        echo "To activate the alias in your current session, run:"
        echo "  source ~/.bashrc"
        ;;
    zsh)
        add_alias_to_file "$HOME/.zshrc"
        echo ""
        echo "To activate the alias in your current session, run:"
        echo "  source ~/.zshrc"
        ;;
    fish)
        add_fish_function
        echo ""
        echo "To activate the alias in your current session, run:"
        echo "  source ~/.config/fish/config.fish"
        ;;
    *)
        echo "⚠️  Unsupported shell: $USER_SHELL"
        echo ""
        echo "You can manually add the alias to your shell configuration file."
        exit 1
        ;;
esac

echo ""
echo "✅ Setup complete!"
echo ""
echo "✨ You can now use 'yolo' to run Claude with MCP servers enabled"
echo ""
echo "Example usage:"
echo "  yolo 'create a hello world script'"
echo "  yolo --resume"
echo "  yolo --no-tools 'explain quantum computing'"