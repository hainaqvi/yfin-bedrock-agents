## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html). 
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)
* Install latest aws-cdk using this command ```sudo npm install -g aws-cdk@latest```

To build and deploy your application for the first time, run the following in your shell:



## Setup of environment
```bash

python -m venv .yf-agent-env
source .yf-agent-env/bin/activate
pip install src/requirement.txt
```

## Use the SAM CLI to build and test locally


You need to login to ecr public 

```bash
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

Build your application with the `sam build --use-container` command.


```bash
sam build --use-container
```


Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash

yfin-api$ sam local invoke ApiFunction -e events/world-indices-event.json
          sam local invoke ApiFunction -e events/day-gainers-event.json
          sam local invoke ApiFunction -e events/day-most-active-event.json
          sam local invoke ApiFunction -e events/day-losers-event.json
          sam local invoke ApiFunction -e events/bonds-event.json
          sam local invoke ApiFunction -e events/ticker-detail-event.json
          sam local invoke ApiFunction -e events/stock-news-event.json
          sam local invoke ApiFunction -e events/cash-flow-event.json
          sam local invoke ApiFunction -e events/income-stmt-event.json
          sam local invoke ApiFunction -e events/balance-sheet-event.json
          sam local invoke ApiFunction -e events/stock-news-event.json
          sam local invoke ApiFunction -e events/days_forex.json
          sam local invoke ApiFunction -e events/mf-best-perform-event.json
          sam local invoke ApiFunction -e events/mf-top-lists-event.json
          sam local invoke ApiFunction -e events/etf-hist-event.json          
          sam local invoke ApiFunction -e events/etf-trend-lists-event.json
          sam local invoke ApiFunction -e events/etf-losing-event.json
          sam local invoke ApiFunction -e events/sector-detail-event.json
          sam local invoke ApiFunction -e events/industry-detail-event.json ( not working)

```
## Lambda Tests

Tests are defined in the `tests` folder in this project. Use PIP to install the test dependencies and run tests.

```bash
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
pip install -r tests/requirements.txt --user

```

## Deploy lambda

After building it use sam deploy the lambda

```bash
sam build --use-container
pytest -v -s tests/integration/test_api.py

sam deploy --guided
```

## Deploy Agents

```bash
cd agent-cdk
pip install -r requirements.txt
cdk deploy
```
 This will deploy following agents
  * stock_info_agent
  * market_indices_agent
  * crypto_agent
  * bonds_agent
  * futures_agent
  * etf_agent
 
## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

first delete the yfin-agent stack 
```bash
sam delete --stack-name "yfin-api"
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)

## Issues
sudo cat /var/log/cloud-init-output.log
sudo tail -f -n 500 /var/log/cloud-init-output.log

zip -r yfin-api-lambda.zip .

## configure plugin
yfinAgent

This agent is used by Financial advisors to provide comprehensive market insights across various investment domains, including stocks, ETFs, cryptocurrencies, bonds, futures, and market sectors.  


sam deploy --parameter-overrides YfinAgentId=$YFIN_AGENT_ID YfinAgentAliasId=$YFIN_AGENT_ALIAS_ID

# License
This project is licensed under the MIT-0 License - see the LICENSE file for details.

