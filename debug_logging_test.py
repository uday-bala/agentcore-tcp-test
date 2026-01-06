"""
Test script with detailed boto3 DEBUG logging to identify retry source
"""
import boto3
import json
import time
import logging
from botocore.config import Config

# Enable detailed boto3 DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable specific boto3 loggers
logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.DEBUG)
logging.getLogger('botocore.retryhandler').setLevel(logging.DEBUG)
logging.getLogger('botocore.endpoint').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.DEBUG)

def test_with_debug_logging():
    # Test configuration with NO retries to prove retries come from elsewhere
    config = Config(
        read_timeout=480,  # 5 minutes
        connect_timeout=60,
        retries={'max_attempts': 1},  # NO RETRIES - to prove they come from infrastructure
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    # Test payload
    payload = {
        'customer_name': 'DebugTest',
        'model_name': 'test',
        'temperature': '0.0',
        'large_data': 'x' * 50000  # 50KB
    }
    
    session_id = f'debug-test-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🚀 Starting DEBUG test with session ID: {session_id}')
    print('📊 Watch for boto3 retry logs in the output')
    print('🔍 Look for "Retry needed" or "Making request" messages')
    print('⚠️  NO CLIENT RETRIES ENABLED - Any duplicates are from infrastructure')
    print('')
    
    try:
        agent_arn = "arn:aws:bedrock-agentcore:us-west-2:426415991432:runtime/atomicIvory_Agent-hy21w68p1l"
        
        start_time = time.time()
        
        print("📡 Making invoke_agent_runtime call...")
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f'✅ Response received after {duration:.1f} seconds')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        print(f'⏱️  Failed after {time.time() - start_time:.1f} seconds')

if __name__ == "__main__":
    test_with_debug_logging()
