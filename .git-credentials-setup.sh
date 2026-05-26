#!/bin/bash
# Run this manually on your Mac to set up git credentials
echo "https://lalalala4you:PASTE_YOUR_TOKEN_HERE@github.com" > ~/.git-credentials
git config --global credential.helper store
echo "✅ Git credentials stored"
