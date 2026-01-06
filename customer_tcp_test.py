"""
Simple test for customer to confirm TCP connection drops in GitHub Actions
"""
import socket
import time
import os

def test_connection_stability():
    print("🔍 Testing TCP Connection Stability in GitHub Actions")
    print(f"Environment: {'GitHub Actions' if os.getenv('GITHUB_ACTIONS') else 'Local'}")
    print("=" * 60)
    
    try:
        # Test direct TCP connection to AgentCore
        print("📡 Connecting to bedrock-agentcore.us-west-2.amazonaws.com:443")
        sock = socket.create_connection(('bedrock-agentcore.us-west-2.amazonaws.com', 443), timeout=30)
        print("✅ TCP connection established")
        
        # Monitor connection for 10 minutes
        start_time = time.time()
        last_check = start_time
        
        while time.time() - start_time < 600:  # 10 minutes
            try:
                current_time = time.time()
                if current_time - last_check >= 30:  # Check every 30 seconds
                    # Test if connection is alive
                    sock.settimeout(5)
                    sock.send(b'')  # Send empty data to test connection
                    
                    elapsed = int(current_time - start_time)
                    minutes, seconds = divmod(elapsed, 60)
                    print(f"   ✅ Connection alive at {minutes}m {seconds}s")
                    last_check = current_time
                
                time.sleep(1)
                
            except socket.timeout:
                elapsed = int(time.time() - start_time)
                print(f"❌ Connection timeout after {elapsed}s")
                break
            except socket.error as e:
                elapsed = int(time.time() - start_time)
                print(f"❌ Connection dropped after {elapsed}s: {e}")
                break
            except Exception as e:
                elapsed = int(time.time() - start_time)
                print(f"❌ Connection error after {elapsed}s: {e}")
                break
        
        sock.close()
        total_time = int(time.time() - start_time)
        print(f"🏁 Test completed after {total_time}s")
        
        # Verdict
        if total_time >= 480:  # 8+ minutes
            print("✅ Connection stable for 8+ minutes")
        else:
            print("❌ Connection dropped before 8 minutes - likely runner issue")
            
    except Exception as e:
        print(f"❌ Initial connection failed: {e}")

if __name__ == "__main__":
    test_connection_stability()
