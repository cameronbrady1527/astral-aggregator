#!/usr/bin/env python3
"""
Test script to verify analytics improvements
"""

import json
import requests
import time

def test_analytics_endpoint():
    """Test the analytics endpoint to see if it's working correctly"""
    
    print("Testing analytics endpoint...")
    
    try:
        # Test analytics endpoint
        response = requests.get('http://localhost:8000/api/listeners/analytics', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics endpoint working!")
            print(f"Status: {data.get('status')}")
            
            if 'analytics' in data and 'overview' in data['analytics']:
                overview = data['analytics']['overview']
                print(f"Total sites: {overview.get('total_sites')}")
                print(f"Active sites: {overview.get('active_sites')}")
                print(f"Total URLs monitored: {overview.get('total_urls_monitored')}")
                print(f"Total changes detected: {overview.get('total_changes_detected')}")
            
            if 'analytics' in data and 'sites' in data['analytics']:
                sites = data['analytics']['sites']
                print(f"\nSite details:")
                for site in sites:
                    print(f"  - {site.get('site_name')}: {site.get('total_urls')} URLs, {site.get('total_changes')} changes")
            
            return True
        else:
            print(f"❌ Analytics endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing analytics: {e}")
        return False

def test_realtime_endpoint():
    """Test the realtime endpoint"""
    
    print("\nTesting realtime endpoint...")
    
    try:
        response = requests.get('http://localhost:8000/api/listeners/realtime', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Realtime endpoint working!")
            print(f"Status: {data.get('status')}")
            
            if 'sites' in data:
                sites = data['sites']
                print(f"Found {len(sites)} sites:")
                for site in sites:
                    print(f"  - {site.get('site_name')}: {site.get('current_urls')} URLs")
            
            return True
        else:
            print(f"❌ Realtime endpoint failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing realtime: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Astral Analytics Improvements")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    analytics_ok = test_analytics_endpoint()
    realtime_ok = test_realtime_endpoint()
    
    print("\n" + "=" * 50)
    if analytics_ok and realtime_ok:
        print("✅ All tests passed! Analytics improvements are working.")
    else:
        print("❌ Some tests failed. Check the server logs.") 