#!/usr/bin/env python3
"""
Configuration setup helper for Kindle Bookmarks script
"""

import json
import os
import sys
from pathlib import Path

def get_input(prompt, default=None, required=True):
    """Get user input with optional default value"""
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    
    value = input(prompt).strip()
    
    if not value and default:
        return default
    elif not value and required:
        print("This field is required!")
        return get_input(prompt.replace(f" [{default}]", "").replace(": ", ""), default, required)
    
    return value

def main():
    print("=== Kindle Bookmarks Configuration Setup ===\n")
    
    config = {
        "karakeep": {},
        "kindle": {},
        "output": {}
    }
    
    # Karakeep settings
    print("1. Karakeep Settings")
    config["karakeep"]["api_url"] = get_input(
        "Karakeep API URL", 
        "https://bookmarks.damianogiorgi.it/api/v1"
    )
    config["karakeep"]["api_key"] = get_input("Karakeep API Key")
    
    print("\n2. Kindle Settings")
    config["kindle"]["email"] = get_input("Your Kindle email address (ends with @kindle.com)")
    
    print("\n3. Email Settings (for sending to Kindle)")
    config["kindle"]["smtp_server"] = get_input("SMTP Server", "smtp.gmail.com")
    config["kindle"]["smtp_port"] = int(get_input("SMTP Port", "587"))
    config["kindle"]["smtp_user"] = get_input("Your email address")
    
    print("\nFor Gmail users:")
    print("- Enable 2-factor authentication")
    print("- Generate an app-specific password")
    print("- Use the app password here, not your regular password")
    config["kindle"]["smtp_password"] = get_input("Email password (or app password)")
    
    print("\n4. Output Settings")
    format_choice = get_input("Output format (pdf/epub)", "pdf").lower()
    if format_choice not in ["pdf", "epub"]:
        format_choice = "pdf"
    config["output"]["format"] = format_choice
    config["output"]["output_dir"] = get_input("Output directory", "./output")
    
    # Save configuration
    config_file = "config.json"
    
    if os.path.exists(config_file):
        overwrite = get_input(f"\n{config_file} already exists. Overwrite? (y/n)", "n", False)
        if overwrite.lower() != 'y':
            print("Configuration not saved.")
            return
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration saved to {config_file}")
        print("\nNext steps:")
        print("1. Make sure your Kindle email is added to your approved sender list in Amazon")
        print("2. Test the configuration with: python kindle_bookmarks.py --dry-run")
        print("3. Run the script: python kindle_bookmarks.py")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)