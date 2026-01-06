"""
GitHub Actions test for 4m40s agent - should timeout at 5 minutes
"""
import boto3
import json
import time
import logging
import os
from botocore.config import Config

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.DEBUG)

def test_github_4m40s():
    """Test 4m40s agent from GitHub Actions - expect timeout at 5 minutes"""
    
    # 5+ minute timeout to see GitHub Actions connection drop
    config = Config(
        read_timeout=360,  # 6+ minutes 
        connect_timeout=30,
        retries={'max_attempts': 1}
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    payload = {
        'test_type': '4m40s_github_test',
        'message': 'Testing 4m40s response from GitHub Actions',
        'expected': 'Should timeout at 5 minutes due to GitHub runner limits'
    }
    
    session_id = f'github-4m40s-test-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🚀 GITHUB TEST: 4m40s agent')
    print(f'🎯 Session ID: {session_id}')
    print('⏱️  Expected: Connection drop at ~5 minutes')
    print('🔧 Running from GITHUB ACTIONS (connection limit)')
    print('')
    
    try:
        account_id = os.getenv('AWS_ACCOUNT_ID')
        if not account_id:
            raise ValueError("Set AWS_ACCOUNT_ID environment variable")
        
        # Your astroCyan agent
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/astroCyan_Agent-LDkBsqEKQO"
        
        start_time = time.time()
        print(f"📡 Starting invoke at {time.strftime('%H:%M:%S')}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f'✅ UNEXPECTED SUCCESS: Response received after {duration:.1f} seconds')
        print(f'📋 Status: {response.get("ResponseMetadata", {}).get("HTTPStatusCode")}')
        print(f'⏰ Completed at {time.strftime("%H:%M:%S")}')
        
        if duration >= 280:  # 4m40s
            print('🎉 GitHub Actions handled full 4m40s - connection limit may have changed!')
        else:
            print('⚠️  Response came back faster than expected')
            
    except Exception as e:
        duration = time.time() - start_time
        print(f'❌ EXPECTED FAILURE after {duration:.1f} seconds: {e}')
        
        if duration >= 280 and duration < 320:  # Between 4m40s and 5m20s
            print('✅ CONFIRMED: GitHub Actions dropped connection around 5 minutes')
            print('🔍 This proves the issue is GitHub Actions runner limits')
        else:
            print(f'🔍 Connection dropped at {duration:.1f}s - investigate timing')

if __name__ == "__main__":
    test_github_4m40s()
