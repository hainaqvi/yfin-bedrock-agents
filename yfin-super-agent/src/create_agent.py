
import boto3, time, os, json
from typing import List, Dict, Tuple
from boto3.session import Session



DEFAULT_ALIAS = "TSTALIASID"
DEFAULT_AGENT_IAM_ROLE_NAME = "DEFAULT_AgentExecutionRole"
DEFAULT_AGENT_IAM_ASSUME_ROLE_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowBedrock",
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ],
}

DEFAULT_AGENT_IAM_POLICY = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AmazonBedrockAgentInferencProfilePolicy1",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel*",
                "bedrock:CreateInferenceProfile",
                "bedrock:GetFoundationModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/*",
                "arn:aws:bedrock:*:*:inference-profile/*",
                "arn:aws:bedrock:*:*:application-inference-profile/*",
            ],
        },
        {
            "Sid": "AmazonBedrockAgentInferencProfilePolicy2",
            "Effect": "Allow",
            "Action": [
                "bedrock:GetInferenceProfile",
                "bedrock:ListInferenceProfiles",
                "bedrock:DeleteInferenceProfile",
                "bedrock:TagResource",
                "bedrock:UntagResource",
                "bedrock:ListTagsForResource"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:inference-profile/*",
                "arn:aws:bedrock:*:*:application-inference-profile/*"
            ]
        },
        {
            "Sid": "AmazonBedrockAgentBedrockFoundationModelPolicy",
            "Effect": "Allow",
            "Action": [
                "bedrock:GetAgentAlias",
                "bedrock:InvokeAgent"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:agent/*",
                "arn:aws:bedrock:*:*:agent-alias/*"
            ]
        },
        {
            "Sid": "AmazonBedrockAgentBedrockInvokeGuardrailModelPolicy",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:GetGuardrail",
                "bedrock:ApplyGuardrail"
            ],
            "Resource": "arn:aws:bedrock:*:*:guardrail/*"
        },
        {
            "Sid": "QueryKB",
            "Effect": "Allow",
            "Action": [
                "bedrock:Retrieve",
                "bedrock:RetrieveAndGenerate"
            ],
            "Resource": "arn:aws:bedrock:*:*:knowledge-base/*"
        }
    ]
}

class BedrockAgentManager:
    def __init__(self, region_name="us-west-2"):
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region_name)
        self.bedrock_runtime_client = boto3.client('bedrock-runtime', region_name=region_name)
        self._boto_session = Session() 
        self._region = self._boto_session.region_name
        self._account_id = boto3.client("sts").get_caller_identity()["Account"]
        self._bedrock_agent_client = boto3.client("bedrock-agent",region_name=region_name)
        self._sts_client = boto3.client("sts")
        self._iam_client = boto3.client("iam")


    def create_yahoo_finance_agent(self):
        """
        Creates an orchestrator agent that coordinates between different financial agents
        """
        agent_foundation_model = ['anthropic.claude-3-5-haiku-20241022-v1:0']
        agent_name = "yahoo_finance_agent"
        agent_id = self.get_agent_id_by_name(agent_name)
        if agent_id:
            self.delete_agent(agent_name, False, True)
        try:
            # Create the main orchestrator agent
            instruction=open("instructions/orchestrator_agent.txt").read().strip()
            agent_id, agent_alias_id, agent_alias_arn = self.create_agent(
                agent_name,
                "Financial Market Orchestrator that coordinates analysis between different market experts",
                instruction,
                agent_foundation_model,
                agent_collaboration='SUPERVISOR_ROUTER'
            )
            self.associate_collaborators(agent_id)
            
            return agent_id, agent_alias_id, agent_alias_arn

        except Exception as e:
            print(f"Error creating super agent: {str(e)}")
            raise
    
    
    
    
    def associate_collaborators(self, agent_id):
        """
        Associates collaborator agents with the main agent.
        
        Args:
            agent_id (str): The ID of the main agent
            agent_version (str): The version of the agent
            alias_id (str): The alias ID of the agent
        """
        try:
            # Define collaborators (sub-agents)
            sub_agent_id= self.get_existing_agent_id("mutual_funds_agent")
            sub_agent_alias_id = self.get_latest_agent_alias_id(sub_agent_id)
            sub_agent_alias = self.bedrock_agent_client.get_agent_alias(agentId=sub_agent_id, agentAliasId=sub_agent_alias_id)
            mutual_funds_arn = sub_agent_alias['agentAlias']['agentAliasArn']
            
            forex_agent_arn = self.get_agent_alias_arn("forex_agent")
            sectors_agent_arn = self.get_agent_alias_arn("sectors_agent")
            stock_info_agent_arn = self.get_agent_alias_arn("stock_info_agent")
            stock_news_agent_arn = self.get_agent_alias_arn("stock_news_agent")
            futures_agent_arn = self.get_agent_alias_arn("futures_agent")
            market_indices_agent_arn = self.get_agent_alias_arn("market_indices_agent")
            bonds_agent_arn = self.get_agent_alias_arn("bonds_agent")
            etf_agent_arn = self.get_agent_alias_arn("etf_agent")
            crypto_agent_arn = self.get_agent_alias_arn("crypto_agent")
            
            sub_agents = [
                {
                    'sub_agent_alias_arn': mutual_funds_arn,
                    'sub_agent_instruction': """Delegate mutual funds analysis and performance tracking tasks to the Mutual Funds Expert,
                                ensuring comprehensive fund analysis and performance metrics.""", 
                    'sub_agent_association_name': 'MutualFundsExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                },
                {
                    'sub_agent_alias_arn': forex_agent_arn,
                    'sub_agent_instruction': """Delegate mutual funds analysis and performance tracking tasks to the Mutual Funds Expert, 
                ensuring comprehensive fund analysis and performance metrics.""", 
                    'sub_agent_association_name': 'ForexExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                },
                {
                    'sub_agent_alias_arn': sectors_agent_arn,
                    'sub_agent_instruction': """Assign sector analysis and performance tracking to the Sectors Expert, 
                    ensuring detailed sector insights and trend analysis.""",
                    'sub_agent_association_name': 'SectorsExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }, 
                {
                    'sub_agent_alias_arn': stock_info_agent_arn,
                    'sub_agent_instruction': """Route stock-specific queries to the Stock Information Expert. Analyze individual stocks, financial statements, technical indicators, and company fundamentals.""",
                    'sub_agent_association_name': 'StockInfoExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }, 
                {
                    'sub_agent_alias_arn': stock_news_agent_arn,
                    'sub_agent_instruction': """Assign sector analysis and performance tracking to the Sectors Expert, 
                    ensuring detailed sector insights and trend analysis.""",
                    'sub_agent_association_name': 'StockNewsExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }, 
                {
                    'sub_agent_alias_arn': futures_agent_arn,
                    'sub_agent_instruction': """Assign sector analysis and performance tracking to the Sectors Expert, 
                    ensuring detailed sector insights and trend analysis.""",
                    'sub_agent_association_name': 'FuturesExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }, 
                {
                    'sub_agent_alias_arn': market_indices_agent_arn,
                    'sub_agent_instruction': """Direct market index analysis to the Market Indices Expert. Track major indices, market breadth, volatility metrics, and broad market trends.""",
                    'sub_agent_association_name': 'MarketIndicesExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }, 

                {
                    'sub_agent_alias_arn': bonds_agent_arn,
                    'sub_agent_instruction': """Route fixed income and bond market analysis to the Bonds Expert. Analyze yield curves, interest rates, bond ratings, and fixed income securities.""",
                    'sub_agent_association_name': 'BondsExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }, 


                {
                    'sub_agent_alias_arn': etf_agent_arn,
                    'sub_agent_instruction': """Direct ETF analysis tasks to the ETF Expert.  Analyze ETF performance, holdings, tracking error, and investment strategies.""",
                    'sub_agent_association_name': 'ETF-ExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }, 



                {
                    'sub_agent_alias_arn': crypto_agent_arn,
                    'sub_agent_instruction': """Delegate cryptocurrency analysis to the Crypto Expert. Analyze digital assets, blockchain metrics, trading volumes, and crypto market trends.""",
                    'sub_agent_association_name': 'CryptoExpertAgent',
                    'relay_conversation_history': 'TO_COLLABORATOR'
                }
                
            # Add other agents as needed...
        ]

            super_agent_alias_id, super_agent_alias_arn = self.associate_sub_agents(agent_id, sub_agents)
            print(f"Successfully associated collaborators")

        except Exception as e:
            print(f"Error associating collaborators: {str(e)}")
            raise

    
    def associate_sub_agents(self, supervisor_agent_id, sub_agents_list):
        for sub_agent in sub_agents_list:
            self.wait_agent_status_update(
                supervisor_agent_id
            )  # Be sure agent is not still in CREATING state
            association_response = (
                self._bedrock_agent_client.associate_agent_collaborator(
                    agentId=supervisor_agent_id,
                    agentVersion="DRAFT",
                    agentDescriptor={"aliasArn": sub_agent["sub_agent_alias_arn"]},
                    collaboratorName=sub_agent["sub_agent_association_name"],
                    collaborationInstruction=sub_agent["sub_agent_instruction"],
                    relayConversationHistory=sub_agent["relay_conversation_history"],
                )
            )
            self.wait_agent_status_update(supervisor_agent_id)
            self._bedrock_agent_client.prepare_agent(agentId=supervisor_agent_id)
            self.wait_agent_status_update(supervisor_agent_id)

        supervisor_agent_alias = self._bedrock_agent_client.create_agent_alias(
            agentAliasName="multi-agent", agentId=supervisor_agent_id
        )
        supervisor_agent_alias_id = supervisor_agent_alias["agentAlias"]["agentAliasId"]
        supervisor_agent_alias_arn = supervisor_agent_alias["agentAlias"][
            "agentAliasArn"
        ]
        return supervisor_agent_alias_id, supervisor_agent_alias_arn

    def get_agent_alias_arn(self, agent_name):
        """
        Gets the ARN of a collaborator agent's alias
        
        Args:
            agent_name (str): Name of the collaborator agent
            
        Returns:
            str: ARN of the collaborator agent's alias
            
        Raises:
            Exception: If agent not found or alias cannot be retrieved
        """
        try:
            # Get the collaborator agent ID
            sub_agent_id = self.get_existing_agent_id(agent_name)
            if not sub_agent_id:
                raise Exception(f"Collaborator agent '{agent_name}' not found")
                
            # Get the latest alias ID for the collaborator
            sub_agent_alias_id = self.get_latest_agent_alias_id(sub_agent_id)
            if not sub_agent_alias_id:
                raise Exception(f"No alias found for collaborator agent '{agent_name}'")
                
            # Get the alias details
            sub_agent_alias = self.bedrock_agent_client.get_agent_alias(
                agentId=sub_agent_id, 
                agentAliasId=sub_agent_alias_id
            )
            
            # Extract and return the alias ARN
            alias_arn = sub_agent_alias['agentAlias']['agentAliasArn']
            print(f"Retrieved alias ARN for {agent_name}: {alias_arn}")
            return alias_arn
            
        except Exception as e:
            print(f"Error getting collaborator alias ARN: {str(e)}")
            raise

    
    def wait_agent_status_update(self, agent_id):
        response = self._bedrock_agent_client.get_agent(agentId=agent_id)
        agent_status = response["agent"]["agentStatus"]
        _waited_at_least_once = False
        while agent_status.endswith("ING"):
            print(f"Waiting for agent status to change. Current status {agent_status}")
            time.sleep(5)
            _waited_at_least_once = True
            try:
                response = self._bedrock_agent_client.get_agent(agentId=agent_id)
                agent_status = response["agent"]["agentStatus"]
            except self._bedrock_agent_client.exceptions.ResourceNotFoundException:
                agent_status = "DELETED"
        if _waited_at_least_once:
            print(f"Agent id {agent_id} current status: {agent_status}")

    def wait_agent_alias_status_update(self, agent_id, agent_alias_id, verbose=False):
        response = self._bedrock_agent_client.get_agent_alias(
            agentId=agent_id, agentAliasId=agent_alias_id
        )
        agent_alias_status = response["agentAlias"]["agentAliasStatus"]
        while agent_alias_status.endswith("ING"):
            if verbose:
                print(
                    f"Waiting for agent ALIAS status to change. Current status {agent_alias_status}"
                )
            time.sleep(5)
            try:
                response = self._bedrock_agent_client.get_agent_alias(
                    agentId=agent_id, agentAliasId=agent_alias_id
                )
                agent_alias_status = response["agentAlias"]["agentAliasStatus"]
            except self._bedrock_agent_client.exceptions.ResourceNotFoundException:
                agent_status = "DELETED"
        if verbose:
            print(
                f"Agent id {agent_id}, Alias {agent_alias_id} current status: {agent_alias_status}"
            )

    
    
    
    def wait_for_agent_status(self, agent_id, max_retries=30, delay=10):
        """
        Waits for the Bedrock agent to reach appropriate state.
        """
        for _ in range(max_retries):
            response = self.bedrock_agent_client.get_agent(agentId=agent_id)
            status = response["agent"]["agentStatus"]
            
            print(f"Current Status: {status}")
            
            if status == "CREATING":
                print("Agent is in CREATING state, waiting for NOT_PREPARED...")
                time.sleep(delay)
                continue
                
            if status == "FAILED":
                print("Agent entered FAILED state. Exiting.")
                return False
                
            if status == "DELETING":
                print("Agent is being deleted. Exiting.")
                return False
                
            if status in ["PREPARING", "PREPARED", "NOT_PREPARED", "UPDATING"]:
                print(f"Agent is in valid state: {status}")
                return True

            time.sleep(delay)  # Wait before the next check

        print(f"Timed out waiting for agent to reach appropriate state after {max_retries} retries")
        return False

        
    def update_agent_collaboration(self, agent_id, role_arn):
        """
        Updates the agent to set collaboration role to SUPERVISOR_ROUTER
        
        Args:
            agent_id (str): The ID of the agent
        """
        try:
            # Get current agent configuration
            response = self.bedrock_agent_client.get_agent(agentId=agent_id)
            agent = response['agent']
            
            # Update the agent with SUPERVISOR_ROUTER collaboration
            update_response = self.bedrock_agent_client.update_agent(
                agentId=agent_id,
                agentName=agent['agentName'],
                roleArn=role_arn,
                agentCollaboration='SUPERVISOR_ROUTER',
            )
            print(f"Updated agent {agent_id} to SUPERVISOR_ROUTER collaboration role")
            return update_response
            
        except Exception as e:
            print(f"Error updating agent collaboration: {str(e)}")
            raise

    
        
    def wait_for_agent_prepared(self, agent_id, max_retries=30, delay=10):
        """Waits for the Bedrock agent to reach PREPARED state."""
        for _ in range(max_retries):
            response = self.bedrock_agent_client.get_agent(agentId=agent_id)
            status = response["agent"]["agentStatus"]
            
            print(f"Current Status: {status}")
            
            if status == "PREPARED":
                print("Agent is now in PREPARED state.")
                return True
            elif status in ["FAILED", "DELETING"]:
                print(f"Agent entered {status} state. Exiting.")
                return False

            time.sleep(delay)  # Wait before the next check

        print("Timed out waiting for the agent to reach PREPARED state.")
        return False
        
        
    def get_existing_agent_id(self, name):
        """Check if an agent with the given name already exists and return its ID."""
        try:
            response = self.bedrock_agent_client.list_agents()
            agents = []
            paginator = self.bedrock_agent_client.get_paginator('list_agents')
        
            # Iterate through all pages
            for page in paginator.paginate():
                agents.extend(page.get("agentSummaries", []))


            for agent in agents:
                if agent["agentName"] == name:
                    print(f"Agent '{name}' already exists with ID: {agent['agentId']}")
                    return agent["agentId"]  # Return existing agent ID
                    
            return None  # No existing agent found
            
        except Exception as e:
            print(f"Error listing agents: {str(e)}")
            raise
        
    def get_existing_agent(self, agent_name):
        """Check if an agent with the given name already exists and return its ID."""
        try:
            response = self.bedrock_agent_client.list_agents()
            
            for agent in response.get("agentSummaries", []):
                if agent["agentName"] == agent_name:
                    print(f"Agent '{agent_name}' already exists with ID: {agent['agentId']}")
                    return agent
                    
            return None  # No existing agent found
            
        except Exception as e:
            print(f"Error listing agents: {str(e)}")
            raise


    def get_latest_agent_alias_id(self, agent_id):
        """
        Gets the latest agent alias ID for a given agent.
        Args: agent_id (str): The ID of the agent to get aliases for   
        Returns: str: The latest agent alias ID if found, None otherwise
        """
        try:
            response = self.bedrock_agent_client.list_agent_aliases(
                agentId=agent_id
            )
            
            aliases = response.get('agentAliasSummaries', [])
            
            if not aliases:
                print(f"No aliases found for agent {agent_id}")
                return None
                
            # Sort aliases by creation time to get the latest one
            latest_alias = sorted(
                aliases,
                key=lambda x: x['updatedAt'],
                reverse=True
            )[0]
            
            print(f"Latest alias for agent {agent_id}: {latest_alias['agentAliasName']} (ID: {latest_alias['agentAliasId']})")
            return latest_alias['agentAliasId']

        except Exception as e:
            print(f"Error getting agent aliases: {str(e)}")
            raise

        # Optional: Additional method to list all aliases for debugging
    def list_agent_aliases(self, agent_id):
            """
            Lists all aliases for a given agent.        
            Args:  agent_id (str): The ID of the agent to list aliases for
            """
            try:
                response = self.bedrock_agent_client.list_agent_aliases(
                    agentId=agent_id
                )
                
                aliases = response.get('agentAliasSummaries', [])
                
                print(f"\nAliases for Agent {agent_id}:")
                print("-" * 80)
                print(f"{'Alias Name':<20} {'Alias ID':<12} {'Status':<15} {'Updated At'}")
                print("-" * 80)
                
                for alias in aliases:
                    print(f"{alias['agentAliasName']:<20} "
                        f"{alias['agentAliasId']:<12} "
                        f"{alias['agentAliasStatus']:<15} "
                        f"{alias['updatedAt'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
            except Exception as e:
                print(f"Error listing agent aliases: {str(e)}")
                raise

    def create_agent(
            self,
            agent_name: str,
            agent_description: str,
            agent_instructions: str,
            model_ids: List[str],
            kb_arns: List[str]=None,
            agent_collaboration: str="DISABLED",
            routing_classifier_model: str=None,
            code_interpretation: bool=False,
            guardrail_id: str=None,
            kb_id: str=None,
            verbose: bool=False
        ) -> Tuple[str, str, str]:
            """Creates an agent given a name, instructions, model, description, and optionally
            a set of knowledge bases. Action groups are added to the agent as a separate
            step once you have created the agent itself.

            Args:
                agent_name (str): name of the agent
                agent_description (str): description of the agent
                agent_instructions (str): instructions for the agent
                model_ids (List[str]): IDs of the foundation models this agent is allowed to use, the first one will be used
                to create the agent, and the others will also be captured in the agent IAM role for future use
                kb_arns (List[str], Optional): ARNs of the Knowledge Base(s) this agent is allowed to use
                agent_collaboration (str, Optional): collaboration type for the agent, defaults to 'SUPERVISOR_ROUTER'
                code_interpretation (bool, Optional): whether to enable code interpretation for the agent, defaults to False
                verbose (bool, Optional): whether to print verbose output, defaults to False
            
            Returns:
                str: agent ID
            """
            if verbose:
                print(f"Creating agent: {agent_name}...")

            _role_arn = self._create_agent_role(agent_name, model_ids, kb_arns, reuse_default=True,
                                                verbose=True)
            _model_id = model_ids[0]

            if verbose:
                print(f"Created agent IAM role: {_role_arn}...")
                print(f"Creating agent: {agent_name} with model: {_model_id}...")

            _num_tries = 0
            _agent_created = False
            _create_agent_response = None
            _agent_id = None

            _kwargs = {}

            if routing_classifier_model is not None:
                _kwargs['promptOverrideConfiguration'] = {
                                "promptConfigurations": [{
                                    "promptType": "ROUTING_CLASSIFIER",
                                    "promptCreationMode": "DEFAULT",
                                    "foundationModel": routing_classifier_model,
                                    "parserMode": "DEFAULT",
                                    "promptState": "ENABLED"
                                }]
                            }
            if guardrail_id is not None:
                _kwargs['guardrailConfiguration'] = {
                    "guardrailIdentifier": guardrail_id,
                    "guardrailVersion": "DRAFT"}
                
            while not _agent_created and _num_tries <= 2:
                try:
                    if verbose:
                        print(f"kwargs: {_kwargs}")
                    _create_agent_response = self._bedrock_agent_client.create_agent(
                        agentName=agent_name,
                        agentResourceRoleArn=_role_arn,
                        description=agent_description.replace(
                            "\n", ""
                        ),  # console doesn't like newlines for subsequent editing
                        idleSessionTTLInSeconds=1800,
                        foundationModel=_model_id,
                        instruction=agent_instructions,
                        agentCollaboration=agent_collaboration,
                        **_kwargs,
                    )
                    _agent_id = _create_agent_response["agent"]["agentId"]
                    if verbose:
                        print(f"Created agent, resulting id: {_agent_id}")
                        _get_resp = self._bedrock_agent_client.get_agent(agentId=_agent_id)
                        print(_get_resp)
                    _agent_created = True

                except Exception as e:
                    if verbose:
                        print(
                            f"Error creating agent: {e}\n. Retrying in case it was just waiting to be deleted."
                        )
                    _num_tries += 1
                    if _num_tries <= 2:
                        time.sleep(4)
                        pass
                    else:
                        if verbose:
                            print(f"Giving up on agent creation after 2 tries.")
                        raise e

            if code_interpretation:
                # possible time.sleep(15) needed here
                self.add_code_interpreter(agent_name)

            _agent_alias_id = DEFAULT_ALIAS 
            _agent_alias_arn = _create_agent_response['agent']['agentArn'].replace("agent", "agent-alias") + f"/{_agent_alias_id}"

            return _agent_id, _agent_alias_id, _agent_alias_arn
        
        
    def _create_agent_role(
            self,
            agent_name: str,
            agent_foundation_models: List[str],
            kb_arns: List[str] = None,
            reuse_default: bool = True,
            verbose: bool = True,) -> str:
        """Creates an IAM role for an agent.

        Args:
            agent_name (str): name of the agent for this new role
            agent_foundation_models (List[str]): List of IDs or Arn's of the Bedrock foundation model(s) this agent is allowed to use
            kb_arns (List[str], Optional): List of ARNs of the Knowledge Base(s) this agent is allowed to use

        Returns:
            str: the Arn for the new role
        """

        if verbose:
            print(f"Creating IAM role for agent: {agent_name}")

        if reuse_default:
            _agent_role_name = DEFAULT_AGENT_IAM_ROLE_NAME

            # try creating the default role, which may already exist
            try:
                # create the default role w/ the proper assume role policy
                _assume_role_policy_document_json = DEFAULT_AGENT_IAM_ASSUME_ROLE_POLICY
                _assume_role_policy_document = json.dumps(
                    _assume_role_policy_document_json
                )

                _bedrock_agent_bedrock_allow_policy_document_json = (
                    DEFAULT_AGENT_IAM_POLICY
                )
                _bedrock_agent_bedrock_allow_policy_document = json.dumps(
                    _bedrock_agent_bedrock_allow_policy_document_json
                )

                _agent_role = self._iam_client.create_role(
                    RoleName=_agent_role_name,
                    AssumeRolePolicyDocument=_assume_role_policy_document,
                )
            except Exception as e:
                if verbose:
                    print(
                        f"Caught exc when creating default role for role: {_agent_role_name}: {e}"
                    )
                    print(f"using assume role json: {_assume_role_policy_document}")
            else:
                self._iam_client.put_role_policy(
                    PolicyDocument=_bedrock_agent_bedrock_allow_policy_document,
                    PolicyName="bedrock_allow_policy",
                    RoleName=_agent_role_name,
                )

            return f"arn:aws:iam::{self._account_id}:role/{DEFAULT_AGENT_IAM_ROLE_NAME}"

        else:
            _agent_role_name = f"AmazonBedrockExecutionRoleForAgents_{agent_name}"
            # _tmp_resources = [f"arn:aws:bedrock:{self._region}::foundation-model/{_model}" for _model in agent_foundation_models]

            # Create IAM policies for agent
            _assume_role_policy_document = DEFAULT_AGENT_IAM_ASSUME_ROLE_POLICY
            _assume_role_policy_document_json = json.dumps(_assume_role_policy_document)

            _agent_role = self._iam_client.create_role(
                RoleName=_agent_role_name,
                AssumeRolePolicyDocument=_assume_role_policy_document_json,
            )

            # Pause to make sure role is created
            time.sleep(10)

            if verbose:
                print(
                    f"Role {_agent_role_name} created. ARN: {_agent_role['Role']['Arn']}"
                )
                print(
                    f"Adding bedrock_allow_policy to role {_agent_role_name}\n{_bedrock_policy_json}..."
                )

            _bedrock_agent_bedrock_allow_policy_statement = DEFAULT_AGENT_IAM_POLICY
            _bedrock_policy_json = json.dumps(
                _bedrock_agent_bedrock_allow_policy_statement
            )

            self._iam_client.put_role_policy(
                PolicyDocument=_bedrock_policy_json,
                PolicyName="bedrock_allow_policy",
                RoleName=_agent_role_name,
            )

            # add Knowledge Base retrieve and retrieve and generate permissions if agent has KB attached to it
            if kb_arns is not None:
                _kb_policy_doc = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "QueryKB",
                            "Effect": "Allow",
                            "Action": [
                                "bedrock:Retrieve",
                                "bedrock:RetrieveAndGenerate",
                            ],
                            "Resource": kb_arns,
                        }
                    ],
                }
                _kb_policy_json = json.dumps(_kb_policy_doc)
                self._iam_client.put_role_policy(
                    PolicyDocument=_kb_policy_json,
                    PolicyName="bedrock_kb_allow_policy",
                    RoleName=_agent_role_name,
                )

                # Pause to make sure role is updated
                time.sleep(10)

            # TODO: scope down GR access to a single GR passed as param
            # # Support Guardrail access
            # _gr_policy_doc = {
            #     "Version": "2012-10-17",
            #     "Statement": [{
            #         "Sid": "AmazonBedrockAgentBedrockInvokeGuardrailModelPolicy",
            #             "Effect": "Allow",
            #             "Action": [
            #                 "bedrock:InvokeModel",
            #                 "bedrock:GetGuardrail",
            #                 "bedrock:ApplyGuardrail"
            #             ],
            #             "Resource": f"arn:aws:bedrock:*:{self._account_id}:guardrail/*"
            #         }]
            # }
            # _gr_policy_json = json.dumps(_gr_policy_doc)
            # self._iam_client.put_role_policy(
            #     PolicyDocument=_gr_policy_json,
            #     PolicyName="bedrock_gr_allow_policy",
            #     RoleName=_agent_role_name
            # )

            return _agent_role["Role"]["Arn"]
        
    def get_agent_id_by_name(self, agent_name: str) -> str:
        """Gets the Agent ID for the specified Agent.

        Args:
            agent_name (str): Name of the agent whose ID is to be returned

        Returns:
            str: Agent ID, or None if not found
        """
        _get_agents_resp = self._bedrock_agent_client.list_agents(maxResults=100)
        _agents_json = _get_agents_resp["agentSummaries"]
        _target_agent = next(
            (agent for agent in _agents_json if agent["agentName"] == agent_name), None
        )
        if _target_agent is None:
            return None
        else:
            return _target_agent["agentId"]

    
    def delete_agent(
            self, agent_name: str, delete_role_flag: bool = True, verbose: bool = False
    ) -> None:
        """Deletes an existing agent. Optionally, deletes the IAM role associated with the agent.

        Args:
            agent_name (str): Name of the agent to delete.
            delete_role_flag (bool, Optional): Flag indicating whether to delete the IAM role associated with the agent.
            Defaults to True.
        """

        # first find the agent ID from the agent Name
        _get_agents_resp = self._bedrock_agent_client.list_agents(maxResults=100)
        _agents_json = _get_agents_resp['agentSummaries']
        _target_agent = next((agent for agent in _agents_json if agent["agentName"] == agent_name), None)

        if _target_agent is None:
            print(f"Agent {agent_name} not found")
            return
        
        if _target_agent is not None and verbose:
            print(f"Found target agent, name: {agent_name}, id: {_target_agent['agentId']}")

        # Delete the agent aliases
        if _target_agent is not None:
            _agent_id = _target_agent["agentId"]

            if verbose:
                print(f"Deleting aliases for agent {_agent_id}...")

            try:
                _agent_aliases = self._bedrock_agent_client.list_agent_aliases(
                    agentId=_agent_id,
                    maxResults=100
                )
                for alias in _agent_aliases['agentAliasSummaries']:
                    alias_id = alias['agentAliasId']
                    print(f'Deleting alias {alias_id} from agent {_agent_id}')
                    response = self._bedrock_agent_client.delete_agent_alias(
                        agentAliasId=alias_id,
                        agentId=_agent_id
                    )
            except Exception as e:
                print(f"Error deleting aliases: {e}")
                pass

        # if the agent exists, delete the agent
        if _target_agent is not None:
            _agent_id = _target_agent['agentId']

            if verbose:
                print(f"Deleting agent: {_agent_id}...")
            time.sleep(5)
            self._bedrock_agent_client.delete_agent(
                agentId=_agent_id
                )
            time.sleep(5)
            
        # TODO: add delete_lambda_flag parameter to optionall take care of
        # deleting the lambda function associated with the agent.

        # delete Agent IAM role if desired
        if delete_role_flag:
            _agent_role_name = f'AmazonBedrockExecutionRoleForAgents_{agent_name}'
            if verbose:
                print(f"Deleting IAM role: {_agent_role_name}...")

            try:
                self._iam_client.delete_role_policy(
                    PolicyName="bedrock_gr_allow_policy", 
                    RoleName=_agent_role_name
                )
            except Exception as e:
                pass

            try:
                self._iam_client.delete_role_policy(
                    PolicyName="bedrock_allow_policy", 
                    RoleName=_agent_role_name
                )
            except Exception as e:
                pass

            try:
                self._iam_client.delete_role_policy(
                    PolicyName="bedrock_kb_allow_policy", 
                    RoleName=_agent_role_name
                )
            except Exception as e:
                pass

            try:
                self._iam_client.delete_role(
                    RoleName=_agent_role_name
                )
            except Exception as e:
                pass


        return

def main():
    # Initialize the manager
    manager = BedrockAgentManager()
    
    # Create the super agent
    yfin_agent_id, yfin_agent_alias_id, yfin_agent_alias_arn = manager.create_yahoo_finance_agent()
    
    # Set the values as environment variables
    # Write to a file that can be sourced
    with open('yfin_agent_env.sh', 'w') as f:
        f.write(f'export YFIN_AGENT_ID={yfin_agent_id}\n')
        f.write(f'export YFIN_AGENT_ALIAS_ID={yfin_agent_alias_id}\n')
        f.write(f'export YFIN_AGENT_ALIAS_ARN={yfin_agent_alias_arn}\n')    
        
    print(f"Created YFIN_AGENT_ID: {yfin_agent_id}")
    print(f"YFIN_AGENT_ALIAS_ID: {yfin_agent_alias_id}")
    print(f"YFIN_AGENT_ALIAS_ARN: {yfin_agent_alias_arn}")
    print("\nTo set these variables in your shell, run:")
    print("source yfin_agent_env.sh")
    


if __name__ == "__main__":
    main()
