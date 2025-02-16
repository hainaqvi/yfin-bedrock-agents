#!/usr/bin/env python3
from aws_cdk import App
from agent_cdk.agent_cdk_stack import YfinStack  # Changed from AgentCdkStack to YfinStack

app = App()
YfinStack(app, "YfinStack")
app.synth()
