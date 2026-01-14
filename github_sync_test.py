"""
GitHub Actions test for sync agent
"""
import boto3
import json
import time
import os
import sys
from botocore.config import Config

def test_sync_agent():
    """Test sync agent - single call, waits for completion"""
    
    prompt = os.getenv('PROMPT', 'tell me a joke')
    duration = int(os.getenv('DURATION_SECONDS', '0'))
    
    # Configure timeout based on expected duration
    timeout_seconds = max(300, duration + 60)  # At least 5 minutes, or duration + 1 minute buffer
    
    config = Config(
        read_timeout=timeout_seconds,
        connect_timeout=30,
        retries={'max_attempts': 1}
    )
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2', config=config)
    
    payload = {
        'prompt': prompt,
        'steps': max(1, duration // 60)  # Convert duration to steps (1 step = 1 minute)
    }
    
    session_id = f'github-sync-test-{int(time.time())}-{int(time.time() * 1000000)}'
    
    print(f'🚀 GITHUB SYNC TEST: Starting')
    print(f'🎯 Prompt: {prompt}')
    print(f'⏱️  Duration: {duration} seconds = {max(1, duration // 60)} steps (1 step = 1 minute)')
    print(f'📝 Session ID: {session_id}')
    print(f'⏰ Client timeout: {timeout_seconds} seconds')
    print('')
    
    try:
        account_id = os.getenv('AWS_ACCOUNT_ID')
        if not account_id:
            raise ValueError("AWS_ACCOUNT_ID environment variable required")
        
        # Your sync agent ARN
        agent_arn = f"arn:aws:bedrock-agentcore:us-west-2:{account_id}:runtime/syncAgentv2_Agent-PMR8N7GtlK" #syncAgentv1_Agent-TylzyR83Ge"
        
        start_time = time.time()
        print(f"📡 Starting sync agent at {time.strftime('%H:%M:%S')}")
        print("⏳ Waiting for complete response...")
        
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            runtimeSessionId=session_id,
            payload=json.dumps(payload)
        )
        
        # Read response
        response_body = response['response'].read().decode('utf-8')
        
        end_time = time.time()
        duration_actual = end_time - start_time
        
        print(f'✅ SYNC RESPONSE RECEIVED after {duration_actual:.1f} seconds')
        print(f'📄 Raw Response: {response_body}')
        print('')
        
        # Parse response
        try:
            response_data = json.loads(response_body)
        except json.JSONDecodeError:
            try:
                response_data = eval(response_body)
            except:
                print(f'⚠️  Could not parse response, showing raw: {response_body}')
                return
        
        # Display results
        if hasattr(response_data, 'get') and response_data.get('status') == 'completed':
            print('🎉 SYNC AGENT SUCCESS!')
            print(f'📝 Generated Content: {response_data.get("processed_data", "No content")}')
            print(f'⏰ Completed at: {response_data.get("completion_time", "Unknown")}')
            print(f'🕐 Total Duration: {duration_actual:.1f} seconds')
            
            # Compare expected vs actual timing
            expected_duration = duration
            if expected_duration > 0:
                if abs(duration_actual - expected_duration) <= 10:
                    print(f'✅ Timing verification: PASSED ({duration_actual:.1f}s ≈ {expected_duration}s)')
                else:
                    print(f'⚠️  Timing difference: Expected {expected_duration}s, got {duration_actual:.1f}s')
            
        elif hasattr(response_data, 'get'):
            print(f'⚠️  Agent Status: {response_data.get("status", "Unknown")}')
            print(f'📝 Message: {response_data.get("message", "No message")}')
            if response_data.get("error"):
                print(f'❌ Error: {response_data.get("error")}')
        else:
            print(f'📄 Response Data: {response_data}')
        
    except Exception as e:
        duration_actual = time.time() - start_time
        print(f'❌ SYNC AGENT FAILED after {duration_actual:.1f} seconds: {e}')
        
        # Analyze failure type
        if "Read timeout" in str(e):
            print(f'🔍 TIMEOUT: Client timed out after {timeout_seconds}s')
            print(f'💡 This demonstrates the sync timeout problem!')
        elif "Connection" in str(e):
            print(f'🔍 CONNECTION: Network connection issue')
        else:
            print(f'🔍 OTHER: {type(e).__name__}')

if __name__ == "__main__":
    test_sync_agent()
