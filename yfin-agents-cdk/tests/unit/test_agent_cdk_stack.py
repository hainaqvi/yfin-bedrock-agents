import aws_cdk as core
import aws_cdk.assertions as assertions

from agent_cdk.agent_cdk_stack import AgentCdkStack

# example tests. To run these tests, uncomment this file along with the example
# resource in agent_cdk/agent_cdk_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AgentCdkStack(app, "agent-cdk")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
