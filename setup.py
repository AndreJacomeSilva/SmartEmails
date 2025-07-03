#!/usr/bin/env python3
"""
Setup script for SmartGold-SmartCompose
This script helps install dependencies and validate configuration.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        print(f"Success: {description}")
        return True
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("Error: Python 3.9 or higher is required")
        return False
    print(f"Python version: {version.major}.{version.minor}.{version.micro} ✓")
    return True

def install_dependencies():
    """Install project dependencies."""
    print("\n=== Installing Dependencies ===")
    
    # Try poetry first, then pip
    if run_command("poetry --version", "Checking Poetry"):
        return run_command("poetry install", "Installing dependencies with Poetry")
    else:
        print("Poetry not found, using pip...")
        return run_command("pip install -r requirements.txt", "Installing dependencies with pip")

def setup_environment():
    """Setup environment file if it doesn't exist."""
    print("\n=== Setting up Environment ===")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("Copying .env.example to .env")
            try:
                with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                    dst.write(src.read())
                print("✓ .env file created")
                print("⚠️  Please edit .env and add your OpenAI API key")
                return True
            except Exception as e:
                print(f"Error creating .env file: {e}")
                return False
        else:
            print("Creating basic .env file")
            try:
                with open(env_file, 'w') as f:
                    f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                    f.write("DEFAULT_AI_MODEL=gpt-4o-mini\n")
                print("✓ .env file created")
                print("⚠️  Please edit .env and add your OpenAI API key")
                return True
            except Exception as e:
                print(f"Error creating .env file: {e}")
                return False
    else:
        print("✓ .env file already exists")
        return True

def validate_configuration():
    """Validate that the configuration is correct."""
    print("\n=== Validating Configuration ===")
    
    try:
        # Try to import the settings
        sys.path.insert(0, 'src')
        from settings import settings
        
        if settings.openai_api_key == "not_configured" or settings.openai_api_key == "your_openai_api_key_here":
            print("⚠️  OpenAI API key is not configured")
            print("   Please edit .env and set OPENAI_API_KEY")
            return False
        else:
            print("✓ OpenAI API key is configured")
            print(f"✓ Default model: {settings.default_ai_model}")
            return True
            
    except Exception as e:
        print(f"Error validating configuration: {e}")
        return False

def main():
    """Main setup function."""
    print("=== SmartGold-SmartCompose Setup ===\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("Failed to setup environment")
        sys.exit(1)
    
    # Validate configuration
    config_valid = validate_configuration()
    
    print("\n=== Setup Complete ===")
    if config_valid:
        print("✓ All checks passed! You can now run the application:")
        print("  python -m uvicorn src.main:app --reload")
    else:
        print("⚠️  Please configure your OpenAI API key in .env file")
        print("  Then run: python -m uvicorn src.main:app --reload")

if __name__ == "__main__":
    main()
