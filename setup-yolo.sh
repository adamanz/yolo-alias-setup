#!/bin/bash

# Script to add 'yolo' alias for ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions
# Supports bash, zsh, and fish shells

# Detect the user's shell
USER_SHELL=$(basename "$SHELL")

# Define the alias
ALIAS_NAME="yolo"
ALIAS_COMMAND="ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions"

# Function to add alias to a file
add_alias_to_file() {
    local file=$1
    local alias_line=$2
    
    # Check if alias already exists
    if grep -q "^alias $ALIAS_NAME=" "$file" 2>/dev/null || grep -q "^alias $ALIAS_NAME " "$file" 2>/dev/null; then
        echo "✓ Alias '$ALIAS_NAME' already exists in $file"
    else
        echo "$alias_line" >> "$file"
        echo "✓ Added '$ALIAS_NAME' alias to $file"
    fi
}

# Function to add fish function
add_fish_function() {
    local fish_config="$HOME/.config/fish/config.fish"
    local fish_function="alias $ALIAS_NAME '$ALIAS_COMMAND'"
    
    # Create fish config directory if it doesn't exist
    mkdir -p "$HOME/.config/fish"
    
    # Check if alias already exists
    if grep -q "^alias $ALIAS_NAME " "$fish_config" 2>/dev/null; then
        echo "✓ Alias '$ALIAS_NAME' already exists in $fish_config"
    else
        echo "$fish_function" >> "$fish_config"
        echo "✓ Added '$ALIAS_NAME' alias to $fish_config"
    fi
}

echo "Setting up 'yolo' alias for: $ALIAS_COMMAND"
echo "Detected shell: $USER_SHELL"
echo ""

case "$USER_SHELL" in
    bash)
        add_alias_to_file "$HOME/.bashrc" "alias $ALIAS_NAME='$ALIAS_COMMAND'"
        echo ""
        echo "To activate the alias in your current session, run:"
        echo "  source ~/.bashrc"
        ;;
    zsh)
        add_alias_to_file "$HOME/.zshrc" "alias $ALIAS_NAME='$ALIAS_COMMAND'"
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
        echo "You can manually add the alias:"
        echo "  For bash: echo \"alias $ALIAS_NAME='$ALIAS_COMMAND'\" >> ~/.bashrc"
        echo "  For zsh:  echo \"alias $ALIAS_NAME='$ALIAS_COMMAND'\" >> ~/.zshrc"
        echo "  For fish: echo \"alias $ALIAS_NAME '$ALIAS_COMMAND'\" >> ~/.config/fish/config.fish"
        exit 1
        ;;
esac

echo ""
echo "✅ Setup complete!"
echo ""
echo "✨ You can now use 'yolo' instead of 'ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions'"
echo ""
echo "Example usage:"
echo "  yolo 'create a hello world script'"
echo "  yolo --resume"
echo "  yolo --no-tools 'explain quantum computing'"