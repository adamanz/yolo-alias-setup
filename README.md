# Yolo Alias Setup

A simple script to set up the `yolo` alias for running Claude with background tasks enabled and permissions skipped.

## ⚠️ Security Notice

This alias uses `--dangerously-skip-permissions` which bypasses Claude's permission prompts. Only use this if you understand and accept the security implications. Claude will execute commands without asking for confirmation.

## What it does

This script adds an alias to your shell configuration:
```bash
yolo → ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions
```

## Installation

### Option 1: Clone and run
```bash
git clone https://github.com/adamanz/yolo-alias-setup.git
cd yolo-alias-setup
./setup-yolo.sh
```

### Option 2: One-liner
```bash
curl -sSL https://raw.githubusercontent.com/adamanz/yolo-alias-setup/master/setup-yolo.sh | bash
```

## Supported Shells
- Bash (~/.bashrc)
- Zsh (~/.zshrc)
- Fish (~/.config/fish/config.fish)

## Usage

After installation, you can use:
```bash
yolo 'create a hello world script'
yolo --resume
yolo --no-tools 'explain quantum computing'
```

Instead of:
```bash
ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions 'create a hello world script'
```

## Manual Setup

If the script doesn't work for your shell, add this line to your shell config:

**Bash/Zsh:**
```bash
alias yolo='ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions'
```

**Fish:**
```fish
alias yolo 'ENABLE_BACKGROUND_TASKS=1 claude --dangerously-skip-permissions'
```