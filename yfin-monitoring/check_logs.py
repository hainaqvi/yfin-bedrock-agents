import boto3
from datetime import datetime, timedelta

logs_client = boto3.client('logs', region_name="us-west-2")

try:
    # First check for log streams
    streams_response = logs_client.describe_log_streams(
        logGroupName='/agentops/bedrock/llm',
        orderBy='LastEventTime',
        descending=True,
        limit=5
    )
    
    if not streams_response.get('logStreams'):
        print("No log streams found in the log group")
    else:
        print(f"Found {len(streams_response['logStreams'])} log streams")
        
        # Check for actual log events in the most recent stream
        if streams_response['logStreams']:
            most_recent_stream = streams_response['logStreams'][0]
            
            # Get events from the last 24 hours
            start_time = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
            
            events_response = logs_client.get_log_events(
                logGroupName='/agentops/bedrock/llm',
                logStreamName=most_recent_stream['logStreamName'],
                startTime=start_time
            )
            
            if not events_response.get('events'):
                print("No log events found in the most recent stream")
            else:
                print(f"Found {len(events_response['events'])} log events")
                # Print sample event
                print("\nSample log event:")
                print(events_response['events'][0])

except Exception as e:
    print(f"Error: {e}")
