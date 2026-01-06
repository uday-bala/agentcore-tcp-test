"""
Simple test for customer to confirm TCP connection drops in GitHub Actions
"""
import socket
import time
import os
import logging

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_connection_stability():
    logging.info("🔍 Testing TCP Connection Stability in GitHub Actions")
    logging.info(f"Environment: {'GitHub Actions' if os.getenv('GITHUB_ACTIONS') else 'Local'}")
    logging.info("=" * 60)
    
    try:
        # Test direct TCP connection to AgentCore
        logging.info("📡 Connecting to bedrock-agentcore.us-west-2.amazonaws.com:443")
        logging.debug("Creating socket connection with 30s timeout")
        sock = socket.create_connection(('bedrock-agentcore.us-west-2.amazonaws.com', 443), timeout=30)
        logging.info("✅ TCP connection established")
        logging.debug(f"Socket details: {sock.getsockname()} -> {sock.getpeername()}")
        
        # Monitor connection for 10 minutes
        start_time = time.time()
        last_check = start_time
        logging.debug(f"Starting connection monitoring at {start_time}")
        
        while time.time() - start_time < 600:  # 10 minutes
            try:
                current_time = time.time()
                if current_time - last_check >= 30:  # Check every 30 seconds
                    # Test if connection is alive
                    logging.debug("Setting 5s timeout for alive check")
                    sock.settimeout(5)
                    logging.debug("Sending empty data to test connection")
                    sock.send(b'')  # Send empty data to test connection
                    
                    elapsed = int(current_time - start_time)
                    minutes, seconds = divmod(elapsed, 60)
                    logging.info(f"   ✅ Connection alive at {minutes}m {seconds}s")
                    logging.debug(f"Elapsed time: {elapsed}s")
                    last_check = current_time
                
                time.sleep(1)
                
            except socket.timeout:
                elapsed = int(time.time() - start_time)
                logging.error(f"❌ Connection timeout after {elapsed}s")
                logging.debug("Socket timeout exception caught")
                break
            except socket.error as e:
                elapsed = int(time.time() - start_time)
                logging.error(f"❌ Connection dropped after {elapsed}s: {e}")
                logging.debug(f"Socket error details: {type(e).__name__}: {e}")
                break
            except Exception as e:
                elapsed = int(time.time() - start_time)
                logging.error(f"❌ Connection error after {elapsed}s: {e}")
                logging.debug(f"Unexpected error: {type(e).__name__}: {e}")
                break
        
        logging.debug("Closing socket connection")
        sock.close()
        total_time = int(time.time() - start_time)
        logging.info(f"🏁 Test completed after {total_time}s")
        
        # Verdict
        if total_time >= 480:  # 8+ minutes
            logging.info("✅ Connection stable for 8+ minutes")
        else:
            logging.warning("❌ Connection dropped before 8 minutes - likely runner issue")
            
    except Exception as e:
        logging.error(f"❌ Initial connection failed: {e}")
        logging.debug(f"Connection failure details: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_connection_stability()
