#!/usr/bin/env python
"""
Quick Fix Script for Selector Timeout Error
Run this to automatically apply the fix
"""
import os
import shutil
import sys

def main():
    print("\n" + "="*70)
    print("Google Maps Scraper - Quick Fix Tool")
    print("="*70)
    print("\nThis will fix the 'Timeout waiting for selector' error")
    print("\nThe fix includes:")
    print("  ✓ Multiple fallback selectors")
    print("  ✓ Better error handling")
    print("  ✓ Direct URL navigation fallback")
    print("  ✓ Improved timeout handling")
    print("="*70 + "\n")
    
    # Check if files exist
    if not os.path.exists('scraper_fixed.py'):
        print("❌ Error: scraper_fixed.py not found in current directory")
        print("\nMake sure you're running this from the project directory!")
        sys.exit(1)
    
    # Backup original
    if os.path.exists('scraper.py'):
        print("📦 Backing up original scraper.py to scraper_backup.py...")
        shutil.copy('scraper.py', 'scraper_backup.py')
        print("   ✓ Backup created")
    
    # Apply fix
    print("\n🔧 Applying fix...")
    shutil.copy('scraper_fixed.py', 'scraper.py')
    print("   ✓ Fix applied!")
    
    print("\n" + "="*70)
    print("✅ FIX APPLIED SUCCESSFULLY!")
    print("="*70)
    print("\nYou can now run the scraper:")
    print("  python main.py -k \"restaurants\" -l \"Mumbai\" --max-results 10")
    print("\nOr run the diagnostic tool to find correct selectors:")
    print("  python diagnose_selectors.py")
    print("\nIf you need to restore the original:")
    print("  cp scraper_backup.py scraper.py")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
