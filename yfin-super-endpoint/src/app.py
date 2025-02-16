import boto3, os, pydantic
from typing_extensions import Annotated
from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.logging import correlation_paths
from botocore.exceptions import ClientError

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()

@app.post("/invoke")
@tracer.capture_method
def invoke_agent():
    """Handle POST requests to invoke Bedrock agent"""
    try:
        body = app.current_event.json_body  # Parse JSON body
        prompt = body.get('prompt')
        
        bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime'        )
        agent_id = os.environ.get('BEDROCK_AGENT_ID')
        agent_alias_Id = os.environ.get('AGENT_ALIAS_ID')
        logger.info(f"invoke_agent prompt: {prompt} agent_id: {agent_id} and agent_alias_Id: {agent_alias_Id}")
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_Id,
            sessionId="test-session",
            inputText=prompt
        )
        
        completion = ""
        for event in response['completion']:
            chunk = event['chunk']
            if 'bytes' in chunk:
                completion += chunk['bytes'].decode('utf-8')
        
        return {
            'statusCode': 200,
            'body': {
                'response': completion,
                'sessionId': "test-session"
            }
        }
            
    except Exception as e:
        logger.exception("Error invoking Bedrock agent")
        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
def lambda_handler(event, context: LambdaContext):
    return app.resolve(event, context)

if __name__ == "__main__":  
    print(app.get_openapi_json_schema())