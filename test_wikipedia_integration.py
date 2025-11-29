"""
Quick test script to verify Wikipedia Bot integration
Run this before starting the web app to ensure everything is set up correctly
"""

import os
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("🔍 Testing imports...")
    try:
        from agent.wikipedia_agent import get_wikipedia_response
        print("✅ Wikipedia agent imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nPlease run: pip install langchain langchain-google-genai langchain-community wikipedia")
        return False

def test_env_variables():
    """Test if required environment variables are set"""
    print("\n🔍 Testing environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY is set (length: {len(gemini_key)} characters)")
        return True
    else:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False

def test_wikipedia_agent():
    """Test the Wikipedia agent with a simple query"""
    print("\n🔍 Testing Wikipedia agent...")
    try:
        from agent.wikipedia_agent import get_wikipedia_response
        print("Sending test query: 'What is Python programming language?'")
        response = get_wikipedia_response("What is Python programming language?")
        
        if response and len(response) > 50:
            print(f"✅ Wikipedia agent works! Response length: {len(response)} characters")
            print(f"\nFirst 200 characters of response:")
            print(f"{response[:200]}...")
            return True
        else:
            print(f"⚠️ Response seems too short: {response}")
            return False
    except Exception as e:
        print(f"❌ Error testing Wikipedia agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_icon():
    """Check if Wikipedia icon exists"""
    print("\n🔍 Checking Wikipedia icon...")
    icon_path = "static/icons/wikipedia-logo.png"
    if os.path.exists(icon_path):
        print(f"✅ Wikipedia icon found at {icon_path}")
        return True
    else:
        print(f"⚠️ Wikipedia icon not found at {icon_path}")
        print("   Using text-based fallback (purple 'W')")
        print("   To add icon, see: static/icons/WIKIPEDIA_ICON_INFO.md")
        return True  # Not critical, we have fallback

def main():
    """Run all tests"""
    print("="*60)
    print("Wikipedia Bot Integration Test")
    print("="*60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Environment Variables", test_env_variables()))
    
    # Only test agent if imports and env are OK
    if all([r[1] for r in results]):
        results.append(("Wikipedia Agent", test_wikipedia_agent()))
    else:
        print("\n⚠️ Skipping agent test due to previous failures")
        results.append(("Wikipedia Agent", False))
    
    results.append(("Icon Check", check_icon()))
    
    print("\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all([r[1] for r in results[:3]])  # Ignore icon check for pass/fail
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All tests passed! Wikipedia Bot is ready to use.")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Open: http://localhost:5000")
        print("3. Click 'Wikipedia Bot' in the sidebar")
        print("4. Start asking questions!")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install packages: pip install -r requirements.txt")
        print("- Set GEMINI_API_KEY in .env file")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
