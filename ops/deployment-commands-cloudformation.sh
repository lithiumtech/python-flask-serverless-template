# This file should never be actually executed! Just a reference for the commands.
exit 1

local STACK_NAME=python-flask-serverless-template-qa
# Deploy QA Infrastructure CloudFormation stack
aws cloudformation create-stack --stack-name $STACK_NAME --template-body file://cloudformation-template-update-stack.yaml --parameters ParameterKey=DomainSuffix,ParameterValue=pci ParameterKey=Region,ParameterValue=us-west-2 ParameterKey=Universe,ParameterValue=qa
