import boto3
import os

def test_bedrock_connection():
    try:
        # Initialize the Bedrock client
        bedrock_agent = boto3.client('bedrock-agent')
        
        agents = []
        paginator = bedrock_agent.get_paginator('list_agents')
        
        # Iterate through all pages
        for page in paginator.paginate():
            agents.extend(page.get("agentSummaries", []))
        
        print("\nExisting Agents:")
        print("-" * 100)
        print(f"{'Name':<25} {'ID':<12} {'Status':<10} {'Version':<10}")
        print("-" * 100)
        
        for agent in agents:
            print(f"{agent['agentName']:<25} {agent['agentId']:<12} {agent['agentStatus']:<10} {agent.get('latestAgentVersion', 'N/A'):<10}")

            
    except Exception as e:
        print(f"Error connecting to Bedrock: {str(e)}")


if __name__ == "__main__":
    test_bedrock_connection()
