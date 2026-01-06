"""
Async invoke test using proper AgentCore async patterns
"""
import boto3
import json
import time
import logging
import os
from botocore.config import Config

# Enable detailed boto3 DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.DEBUG)

def test_agentcore_async_pattern():
    """Test AgentCore async pattern with proper task management"""
    
    config = Config(
        read_timeout=60,  # Longer for initial response but not full task completion
        connect_timeout=10,
        retries={'max_attempts': 1}
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    # Payload requesting async task (same size as sync test)
    payload = {
        'customer_name': 'AsyncAgentCoreTest',
        'task_type': 'async_background_task',
        'duration': 600,  # 10 minutes of background work
        'async_mode': True,
        'message': 'Start a long background task and return immediately',
        'large_data': 'x' * 50000  # 50KB - same as sync test
    }
    
    session_id = f'agentcore-async-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🚀 Starting AgentCore ASYNC test with session ID: {session_id}')
    print('⚡ Using AgentCore async task pattern')
    print('📊 Expecting immediate response with task_id, then background processing')
    print('🔄 Agent should return "HealthyBusy" status while processing')
    print('')
    
    try:
        account_id = os.getenv('AWS_ACCOUNT_ID')
        if not account_id:
            raise ValueError("AWS_ACCOUNT_ID environment variable is required")
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/atomicIvory_Agent-hy21w68p1l"
        
        start_time = time.time()
        
        print("📡 Making AgentCore async invoke call...")
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f'✅ Initial response received after {duration:.1f} seconds')
        print(f'📋 Response status: {response.get("ResponseMetadata", {}).get("HTTPStatusCode", "unknown")}')
        print(f'🎯 Session ID: {session_id}')
        print('')
        
        # Simulate checking agent status (ping endpoint)
        print('🔍 In production, you would now poll the agent status:')
        print('   GET /ping endpoint should return {"status": "HealthyBusy"}')
        print('   Continue polling until {"status": "Healthy"}')
        print('   Then make another invoke call to get results')
        
        return session_id
        
    except Exception as e:
        duration = time.time() - start_time
        print(f'❌ Error after {duration:.1f} seconds: {e}')
        print('🔍 Check if this is connection timeout or agent configuration issue')
        return None

def simulate_status_polling(session_id):
    """Simulate AgentCore status polling pattern"""
    if not session_id:
        return
        
    print('')
    print('🔄 AGENTCORE ASYNC POLLING PATTERN:')
    print(f'   session_id = "{session_id}"')
    print('   ')
    print('   # Check agent status via ping endpoint')
    print('   while True:')
    print('       ping_response = GET /ping')
    print('       if ping_response["status"] == "Healthy":')
    print('           # Agent finished background task')
    print('           break')
    print('       elif ping_response["status"] == "HealthyBusy":')
    print('           # Still processing, wait and check again')
    print('           time.sleep(30)')
    print('       else:')
    print('           # Handle error states')
    print('           break')
    print('   ')
    print('   # Get final results')
    print('   final_response = invoke_agent_runtime(session_id, {"get_results": True})')

if __name__ == "__main__":
    session_id = test_agentcore_async_pattern()
    simulate_status_polling(session_id)
