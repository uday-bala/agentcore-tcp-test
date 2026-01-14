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
        
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/asyncAgentv3_Agent-pcnPRl8xbN"
        
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
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/asyncAgentv3_Agent-pcnPRl8xbN"
        
        print(f"📡 Retrieving results at {time.strftime('%H:%M:%S')}")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        # Read response
        response_body = response['response'].read().decode('utf-8')
        
        print(f'✅ RESULTS RETRIEVED')
        print(f'📄 Raw Response: {response_body}')
        print(f'📄 Response Type: {type(response_body)}')
        print('')
        
        # Handle different response formats
        try:
            # Try JSON parsing first
            response_data = json.loads(response_body)
        except json.JSONDecodeError:
            try:
                # Try eval for dict-like strings from DynamoDB
                response_data = eval(response_body)
            except:
                # If all else fails, treat as error
                print(f'❌ Could not parse response: {response_body}')
                return
        
        # Now safely access the data
        if hasattr(response_data, 'get') and response_data.get('status') == 'completed':
            print('🎉 ASYNC AGENT SUCCESS!')
            print(f'📝 Generated Content: {response_data.get("processed_data", "No content")}')
            print(f'⏰ Completed at: {response_data.get("completion_time", "Unknown")}')
        elif hasattr(response_data, 'get'):
            print(f'⚠️  Task Status: {response_data.get("status", "Unknown")}')
            print(f'📝 Message: {response_data.get("message", "No message")}')
        else:
            print(f'📄 Response Data: {response_data}')
        
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
