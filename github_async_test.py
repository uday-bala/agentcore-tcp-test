"""
GitHub Actions test for async agent
"""
import boto3
import json
import time
import os
import sys
from botocore.config import Config

def start_async_task():
    """Start async agent task"""
    
    config = Config(
        read_timeout=60,  # Short timeout since we expect immediate response
        connect_timeout=30,
        retries={'max_attempts': 1}
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    prompt = os.getenv('PROMPT', 'tell me a joke')
    duration = int(os.getenv('DURATION_SECONDS', '420'))
    
    payload = {
        'prompt': prompt,
        'duration_seconds': duration
    }
    
    session_id = f'github-async-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🚀 GITHUB ASYNC TEST: Starting task')
    print(f'🎯 Prompt: {prompt}')
    print(f'⏱️  Duration: {duration} seconds')
    print(f'📝 Session ID: {session_id}')
    print('')
    
    try:
        account_id = os.getenv('AWS_ACCOUNT_ID')
        if not account_id:
            raise ValueError("AWS_ACCOUNT_ID environment variable required")
        
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/asyncAgentv3_Agent-pcnPRl8xbN" #asyncAgentv2_Agent-dpeKIS4Lv6"
        
        start_time = time.time()
        print(f"📡 Starting async task at {time.strftime('%H:%M:%S')}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        # Read response
        response_body = response['response'].read().decode('utf-8')
        response_data = json.loads(response_body)
        
        end_time = time.time()
        duration_actual = end_time - start_time
        
        print(f'✅ TASK STARTED: Response received after {duration_actual:.1f} seconds')
        print(f'📄 Response: {response_body}')
        print(f'🆔 Task ID: {response_data.get("task_id")}')
        
        # Output task_id for next step
        print(f'::set-output name=task_id::{response_data.get("task_id")}')
        
        return response_data.get("task_id")
        
    except Exception as e:
        print(f'❌ FAILED to start task: {e}')
        sys.exit(1)

def get_task_results():
    """Get results from completed async task"""
    
    config = Config(
        read_timeout=60,
        connect_timeout=30,
        retries={'max_attempts': 1}
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    task_id = os.getenv('TASK_ID')
    if not task_id:
        print('❌ TASK_ID environment variable required')
        sys.exit(1)
    
    payload = {
        'action': 'get_results',
        'task_id': int(task_id)
    }
    
    session_id = f'github-results-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🔍 GETTING RESULTS: Task ID {task_id}')
    print('')
    
    try:
        account_id = os.getenv('AWS_ACCOUNT_ID')
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/asyncAgentv3_Agent-pcnPRl8xbN" #asyncAgentv2_Agent-dpeKIS4Lv6"
        
        print(f"📡 Retrieving results at {time.strftime('%H:%M:%S')}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        # Read response
        response_body = response['response'].read().decode('utf-8')
        
        # Handle both JSON string and direct dict responses
        try:
            response_data = json.loads(response_body)
        except (json.JSONDecodeError, TypeError):
            # If it's already a dict (from DynamoDB), use it directly
            response_data = eval(response_body) if isinstance(response_body, str) else response_body
        
        print(f'✅ RESULTS RETRIEVED')
        print(f'📄 Response Type: {type(response_data)}')
        print('')
        
        if response_data.get('status') == 'completed':
            print('🎉 ASYNC AGENT SUCCESS!')
            print(f'📝 Generated Content: {response_data.get("processed_data")}')
            print(f'⏰ Completed at: {response_data.get("completion_time")}')
        else:
            print(f'⚠️  Task Status: {response_data.get("status")}')
            print(f'📝 Message: {response_data.get("message")}')
        
    except Exception as e:
        print(f'❌ FAILED to get results: {e}')
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 github_async_test.py [start|get_results]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'start':
        start_async_task()
    elif action == 'get_results':
        get_task_results()
    else:
        print("Invalid action. Use 'start' or 'get_results'")
        sys.exit(1)
