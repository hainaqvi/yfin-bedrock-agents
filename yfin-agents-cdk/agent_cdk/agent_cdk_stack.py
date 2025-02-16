from aws_cdk import (
   Stack,
   aws_lambda as lambda_,
   aws_iam as iam,
   CfnResource,
   Duration
)
from cdklabs.generative_ai_cdk_constructs import bedrock
from constructs import Construct
import json, os
from aws_cdk import CfnOutput



class YfinStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.stock_info_agent = self.create_stock_info_agent()
        self.stock_news_agent = self.create_stock_news_agent()
        self.market_indices_agent = self.create_market_indices_agent()
        self.crypto_agent = self.create_crypto_agent()
        self.bonds_agent = self.create_bonds_agent()
        self.futures_agent = self.create_futures_agent()
        self.etf_agent = self.create_etf_agent()
        self.mutual_funds_agent = self.create_mutual_funds_agent()
        self.forex_agent = self.create_forex_agent()
        self.sectors_agent = self.create_sectors_agent()
        
        
        # Add these after your agent creation code
        CfnOutput(self, "StockInfoAgentArn",
            value=self.stock_info_agent.agent_arn,
            description="ARN of the Stock Info Agent",
            export_name="StockInfoAgentArn"
        )

        CfnOutput(self, "StockNewsAgentArn",
            value=self.stock_news_agent.agent_arn,
            description="ARN of the Stock News Agent",
            export_name="StockNewsAgentArn"
        )

        CfnOutput(self, "MarketIndicesAgentArn",
            value=self.market_indices_agent.agent_arn,
            description="ARN of the Market Indices Agent",
            export_name="MarketIndicesAgentArn"
        )

        CfnOutput(self, "CryptoAgentArn",
            value=self.crypto_agent.agent_arn,
            description="ARN of the Crypto Agent",
            export_name="CryptoAgentArn"
        )

        CfnOutput(self, "BondsAgentArn",
            value=self.bonds_agent.agent_arn,
            description="ARN of the Bonds Agent",
            export_name="BondsAgentArn"
        )

        CfnOutput(self, "FuturesAgentArn",
            value=self.futures_agent.agent_arn,
            description="ARN of the Futures Agent",
            export_name="FuturesAgentArn"
        )

        CfnOutput(self, "EtfAgentArn",
            value=self.etf_agent.agent_arn,
            description="ARN of the ETF Agent",
            export_name="EtfAgentArn"
        )

        CfnOutput(self, "MutualFundsAgentArn",
            value=self.mutual_funds_agent.agent_arn,
            description="ARN of the Mutual Funds Agent",
            export_name="MutualFundsAgentArn"
        )

        CfnOutput(self, "ForexAgentArn",
            value=self.forex_agent.agent_arn,
            description="ARN of the Forex Agent",
            export_name="ForexAgentArn"
        )

        CfnOutput(self, "SectorsAgentArn",
            value=self.sectors_agent.agent_arn,
            description="ARN of the Sectors Agent",
            export_name="SectorsAgentArn"
        )

            
    def create_lambda_reference(self, id_name: str) -> lambda_.IFunction:
        lambda_arn = os.getenv('LAMBDA_ARN')
        if not lambda_arn:
            raise ValueError("LAMBDA_ARN environment variable is not set")
        return lambda_.Function.from_function_attributes(
            self, 
            id_name,
            function_arn=lambda_arn,
            same_environment=True
    )
    
    def create_stock_info_agent(self):
        
        agent = bedrock.Agent(
            self,
            "stock_info_agent",
            name="stock_info_agent",
            description="You are a Financial Market Analyst Assistant that helps customers stocks and day's stock performance.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/stock_info_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "stock_info_agent_v1",
            alias_name="stock_info_agent_v1",
            agent=agent,
            description="Stock Info Agent Alias",
        )
        
        stock_info: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="stock_info_service",
            description="Get stock's symbol details",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("stock_info_service_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/stock_info.json"),  
        )
        agent.add_action_group(stock_info)
        
        stock_list: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="stock_list_service",
            description="Stock list for Days performance",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("stock_list_service_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/stock_list_service.json"),  
        )
        agent.add_action_group(stock_list)
        
        stock_financials: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="stock_financials",
            description="stock_financials balance sheet, cash flow, income statement and news API",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("stock_financials_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/stock_financials.json"),  
        )
        agent.add_action_group(stock_financials)
        return agent    


    def create_stock_news_agent(self):
        
        agent = bedrock.Agent(
            self,
            "stock_news_agent",
            name="stock_news_agent",
            description="Stock news Analyst Assistant that helps customers understand stocks news.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/stock_news_agent.txt").read().strip(),

        )
        
        bedrock.AgentAlias( 
            self,
            "stock_news_agent_v1",
            alias_name="stock_news_agent_v1",
            agent=agent,
            description="stock_news_agent Alias",
        )
        
        
        stock_news: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="stock_news",
            description="Get stock news for given symbol",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("stock_news_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/stock_news.json"),  
        )
        agent.add_action_group(stock_news)
        return agent   
                



    def create_market_indices_agent(self):
        
        agent = bedrock.Agent(
            self,
            "market_indices",
            name="market_indices_agent",
            description="Financial Market Analyst Assistant that helps customers understand financial Markets indies performance.",
            should_prepare_agent=True,	
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/market_indices_agent.txt").read().strip(),

        )
        
        bedrock.AgentAlias( 
            self,
            "market_indices_agent_v1",
            alias_name="market_indices_agent_v1",
            agent=agent,
            description="market_indices_agent Alias",
        )

        
        
        market_indices: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="market_indices_service",
            description="Market Indices covering the world",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("market_indices_service_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/market_indices.json"),  
        )
        agent.add_action_group(market_indices)
        return agent   

    def create_crypto_agent(self):
        
        agent = bedrock.Agent(
            self,
            "crypto_agent",
            name="crypto_agent",
            description="Cryptocurrencies Analyst Assistant that helps customers understand Crypto choices.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/crypto_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "crypto_agent_v1",
            alias_name="crypto_agent_v1",
            agent=agent,
            description="crypto_agent Alias",
        )
        
        crypto_service: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="crypto_service",
            description="Cryptocurrencies performance",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("crypto_service_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/crypto_service.json"),  
        )
        agent.add_action_group(crypto_service)
        return agent   

    def create_bonds_agent(self):
        
        agent = bedrock.Agent(
            self,
            "bonds_agent",
            name="bonds_agent",
            description="Bonds Analyst Assistant that helps customers understand Bonds choices.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/bonds_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "bonds_agent_v1",
            alias_name="bonds_agent_v1",
            agent=agent,
            description="bonds_agent Alias",
        )

        
        bonds_service: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="bonds_service",
            description="markets bonds performanc",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("bonds_service_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/bonds_service.json"),  
        )
        agent.add_action_group(bonds_service)
        return agent   

    def create_futures_agent(self):
        
        agent = bedrock.Agent(
            self,
            "futures_agent",
            name="futures_agent",
            description="Futures contract Analyst Assistant that helps customers understand Futures choices.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/futures_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "futures_agent_v1",
            alias_name="futures_agent_v1",
            agent=agent,
            description="futures_agent Alias",
        )


        
        futures_service: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="futures_service",
            description="Futures contracts performance",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("futures_service_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/futures_service.json"),  
        )
        agent.add_action_group(futures_service)
        return agent   


    def create_etf_agent(self):
        
        agent = bedrock.Agent(
            self,
            "etf_agent",
            name="etf_agent",
            description="ETF Market Analyst Assistant that helps customers understand ETF choices.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/etf_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "etf_agent_v1",
            alias_name="etf_agent_v1",
            agent=agent,
            description="etf_agent Alias",
        )

        etf_service: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="etf_service",
            description="ETF performance",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("etf_service_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/etf_service.json"),  
        )
        agent.add_action_group(etf_service)
        return agent   


    def create_mutual_funds_agent(self):
        
        agent = bedrock.Agent(
            self,
            "mutual_funds_agent",
            name="mutual_funds_agent",
            description="Mutual funds Analyst Assistant that helps customers understand Mutual funds.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/mutual_funds_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "mutual_funds_v1",
            alias_name="mutual_funds_v1",
            agent=agent,
            description="mutual_funds Alias",
        )

        
        etf_service: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="mutual_funds_service",
            description="Mutual funds performance",
            executor= bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("mutual_funds_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/mutual_funds_service.json"),  
        )
        agent.add_action_group(etf_service)
        return agent   
        
    def create_forex_agent(self):
        """
        Creates a Forex agent with Bedrock integration
        """
        agent = bedrock.Agent(
            self,
            "forex_agent",
            name="forex_agent",
            description="Forex Market Analyst Assistant that helps customers understand currency market performance.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/forex_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "forex_agent_v1",
            alias_name="forex_agent_v1",
            agent=agent,
            description="mutual_funds Alias",
        )

        
        forex_service: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="forex_service",
            description="Forex market performance",
            executor=bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("forex_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/forex_service.json"),
        )
        agent.add_action_group(forex_service)
        return agent   


    def create_sectors_agent(self):
        """
        Creates a Sectors Analysis agent with Bedrock integration
        """
        agent = bedrock.Agent(
            self,
            "sectors_agent",
            name="sectors_agent",
            description="Sectors Analysis Assistant that helps customers understand market sectors and their performance.",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/sector_agent.txt").read().strip(),
        )
        
        bedrock.AgentAlias( 
            self,
            "sectors_agent_v1",
            alias_name="sectors_agent_v1",
            agent=agent,
            description="sectors_agent Alias",
        )

        
        sector_service: bedrock.AgentActionGroup = bedrock.AgentActionGroup(
            name="sectors_service",
            description="Market sectors performance and analysis",
            executor=bedrock.ActionGroupExecutor.fromlambda_function(self.create_lambda_reference("sector_lambda")),
            enabled=True,
            api_schema=bedrock.ApiSchema.from_local_asset("open_api_schema/sector_service.json"),  
        )
        agent.add_action_group(sector_service)
        return agent  
    
    
    def create_orchestrator_agent(self):
        """
        Creates an orchestrator agent that coordinates between different financial agents
        """
        # Create the main orchestrator agent
        orchestrator = bedrock.Agent(
            self,
            "orchestrator_agent",
            name="financial_orchestrator",
            description="Financial Market Orchestrator that coordinates analysis between different market experts",
            should_prepare_agent=True,
            foundation_model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_HAIKU_V1_0,
            instruction=open("instructions/orchestrator_agent.txt").read().strip(),
            agent_collaboration='SUPERVISOR_ROUTER'
        )

        # Create sub-agents list
        sub_agents_list = [
            {
                'sub_agent_alias_arn': self.mutual_funds_agent.agent_alias_arn,
                'sub_agent_instruction': """Delegate mutual funds analysis and performance tracking tasks to the Mutual Funds Expert, 
                ensuring comprehensive fund analysis and performance metrics.""",
                'sub_agent_association_name': 'MutualFundsExpertAgent',
                'relay_conversation_history': 'TO_COLLABORATOR'
            },
            {
                'sub_agent_alias_arn': self.forex_agent.agent_alias_arn,
                'sub_agent_instruction': """Direct foreign exchange market analysis and currency performance tasks to the Forex Expert, 
                leveraging its market analysis capabilities.""",
                'sub_agent_association_name': 'ForexExpertAgent',
                'relay_conversation_history': 'TO_COLLABORATOR'
            },
            {
                'sub_agent_alias_arn': self.sectors_agent.agent_alias_arn,
                'sub_agent_instruction': """Assign sector analysis and performance tracking to the Sectors Expert, 
                ensuring detailed sector insights and trend analysis.""",
                'sub_agent_association_name': 'SectorsExpertAgent',
                'relay_conversation_history': 'TO_COLLABORATOR'
            }
            # Add other agents as needed...
        ]

        # Associate sub-agents with the orchestrator
        bedrock.associate_sub_agents(
            orchestrator.agent_id, 
            sub_agents_list
        )

        return orchestrator
    
            