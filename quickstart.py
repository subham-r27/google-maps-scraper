#!/usr/bin/env python
"""
Quick Start Guide - Google Maps Business Lead Scraper

This script demonstrates how to use the scraper with various configurations.
Run different examples by uncommenting the desired configuration.
"""

import subprocess
import sys


def run_command(description, command):
    """Run a command and display it"""
    print("\n" + "="*70)
    print(f"Example: {description}")
    print("="*70)
    print(f"Command: {command}")
    print("-"*70)
    
    choice = input("Run this example? (y/n): ").strip().lower()
    
    if choice == 'y':
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
        except KeyboardInterrupt:
            print("\nInterrupted by user")
    else:
        print("Skipped.")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║        Google Maps Business Lead Scraper - Quick Start           ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

This guide will help you run different scraping examples.
""")
    
    examples = [
        {
            "description": "Basic Search - Cosmetic Manufacturers in Chennai (10 results)",
            "command": 'python main.py -k "cosmetic manufacturer" -l "Chennai" --max-results 10'
        },
        {
            "description": "Restaurant Search - Mumbai (visible browser, 20 results)",
            "command": 'python main.py -k "restaurants" -l "Mumbai" --max-results 20'
        },
        {
            "description": "Hotel Search - Delhi (headless mode, 30 results)",
            "command": 'python main.py -k "hotels" -l "Delhi" --headless --max-results 30'
        },
        {
            "description": "Cafe Search - Bangalore (with verbose logging)",
            "command": 'python main.py -k "cafes" -l "Bangalore" --max-results 15 --verbose'
        },
        {
            "description": "Gym Search - Pune (custom output directory)",
            "command": 'python main.py -k "gyms" -l "Pune" --max-results 25 --output-dir "gym_leads"'
        },
    ]
    
    print("Choose an example to run:\n")
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}")
    
    print(f"{len(examples) + 1}. Run custom command")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-6): ").strip()
    
    try:
        choice_num = int(choice)
        
        if choice_num == 0:
            print("Goodbye!")
            sys.exit(0)
        elif choice_num == len(examples) + 1:
            # Custom command
            keyword = input("Enter keyword (e.g., 'restaurants'): ").strip()
            location = input("Enter location (e.g., 'Chennai'): ").strip()
            max_results = input("Enter max results (default: 10): ").strip() or "10"
            headless = input("Run headless? (y/n, default: n): ").strip().lower()
            
            command = f'python main.py -k "{keyword}" -l "{location}" --max-results {max_results}'
            if headless == 'y':
                command += ' --headless'
            
            run_command("Custom Search", command)
        elif 1 <= choice_num <= len(examples):
            example = examples[choice_num - 1]
            run_command(example["description"], example["command"])
        else:
            print("Invalid choice!")
    except ValueError:
        print("Invalid input!")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")


if __name__ == '__main__':
    main()
