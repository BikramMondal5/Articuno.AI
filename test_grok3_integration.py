"""
Test script to verify Grok-3 integration
Run this after starting the Flask server to test the integration
"""

import requests
import json

# Base URL of your Flask application
BASE_URL = "http://localhost:5000"

def test_grok3_integration():
    """Test the Grok-3 bot integration"""
    
    print("=" * 60)
    print("Testing Grok-3 Integration")
    print("=" * 60)
    
    # Test 1: Simple message
    print("\n[Test 1] Sending a simple test message...")
    test_data = {
        "message": "Hello Grok! Can you introduce yourself?",
        "bot": "Grok-3"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Response received successfully!")
            print(f"\nResponse (first 200 chars): {data.get('response', '')[:200]}...")
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error: Make sure Flask server is running on port 5000")
        print("  Start server with: python app.py")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    # Test 2: Technical question
    print("\n[Test 2] Asking a technical question...")
    test_data = {
        "message": "Explain quantum computing in simple terms",
        "bot": "Grok-3"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✓ Technical question handled successfully!")
        else:
            print(f"✗ Error: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)
    print("\nIf tests passed, Grok-3 is successfully integrated!")
    print("You can now use it through the web interface.")

if __name__ == "__main__":
    print("\n📝 Note: Make sure the Flask server is running before running this test")
    print("   Start server with: python app.py\n")
    
    input("Press Enter to start testing...")
    test_grok3_integration()
