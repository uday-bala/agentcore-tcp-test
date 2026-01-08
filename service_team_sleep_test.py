"""
Service Team Sleep Agent test - single configurable duration for GitHub Actions
"""
import boto3
import json
import time
import logging
import os
import socket
from botocore.config import Config

# Configure aggressive TCP keep-alive to prevent GitHub Actions timeouts
def enable_socket_keepalive():
    """Enable aggressive TCP keep-alive probes"""
    original_socket = socket.socket
    
    def socket_with_keepalive(*args, **kwargs):
        sock = original_socket(*args, **kwargs)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        
        # Start probes after 60 seconds of inactivity
        if hasattr(socket, 'TCP_KEEPIDLE'):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
        
        # Send probe every 30 seconds
        if hasattr(socket, 'TCP_KEEPINTVL'):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 30)
        
        # Give up after 3 failed probes
        if hasattr(socket, 'TCP_KEEPCNT'):
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
        
        return sock
    
    socket.socket = socket_with_keepalive

# Enable keep-alive before any network operations
enable_socket_keepalive()

# Enable debug logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_sleep_agent():
    """Test sleep agent with configurable duration from environment"""
    
    duration_seconds = int(os.getenv('DURATION_SECONDS', '300'))
    
    config = Config(
        read_timeout=900,  # 15 minutes
        connect_timeout=60,
        retries={'max_attempts': 1},
        # Force TCP keep-alive settings
        tcp_keepalive=True
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    payload = {
        'duration_seconds': duration_seconds,
        'test_type': 'github_sleep_test',
        'message': f'Testing {duration_seconds}s sleep duration with TCP keep-alive'
    }
    
    session_id = f'github-sleep-test-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🚀 SERVICE TEAM SLEEP AGENT TEST: {duration_seconds}s duration')
    print(f'🎯 Session ID: {session_id}')
    print(f'⏱️  Expected: {duration_seconds} second sleep')
    print(f'🔧 TCP Keep-Alive: ENABLED')
    print('')
    
    try:
        account_id = os.getenv('AWS_ACCOUNT_ID')
        if not account_id:
            raise ValueError("Set AWS_ACCOUNT_ID environment variable")
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/echoLime_Agent-NO4rb4DyPq"
        
        start_time = time.time()
        print(f"📡 Starting invoke at {time.strftime('%H:%M:%S')}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        # Read the streaming response body
        response_body = response['response'].read().decode('utf-8')
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f'✅ SUCCESS: Response received after {duration:.1f} seconds')
        print(f'📄 Agent Response: {response_body}')
        print(f'⏰ Completed at {time.strftime("%H:%M:%S")}')
        
        # Verify duration
        if abs(duration - duration_seconds) <= 5:  # Within 5 seconds tolerance
            print(f'🎉 Duration verification: PASSED ({duration:.1f}s ≈ {duration_seconds}s)')
            print(f'✅ TCP Keep-Alive successfully maintained connection!')
        else:
            print(f'⚠️  Duration verification: Expected {duration_seconds}s, got {duration:.1f}s')
            
    except Exception as e:
        duration = time.time() - start_time
        print(f'❌ FAILURE after {duration:.1f} seconds: {e}')
        print(f'🔍 Check if TCP keep-alive settings need adjustment')

if __name__ == "__main__":
    test_sleep_agent()
