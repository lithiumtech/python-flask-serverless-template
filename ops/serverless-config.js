module.exports = (serverless) => {
    const options = serverless.variables.options;
    const region = (options.region) ? options.region : serverless.variables.serverless.service.provider.region;
    const stage = (options.stage) ? options.stage : serverless.variables.serverless.service.provider.stage;
    // stage aka 'universe' in Care parlance

    const dynamoDBPrefix = stage + '-live-service-name-';

    const deploymentBucket = `lithium-cloudops-serverless-deployment-${stage}-${region}`;

    const webviewGateway = {
        'qa': {
            'us-west-2': {
                'certArn': 'arn:aws:acm:us-west-2:642760139656:certificate/d7c7dbf3-0c6b-45fc-8165-a60e0f6f10ed',
                'certName': '*.qa.aws.lcloud.com',
                'domainName': 'service-name-us-west-2.qa.aws.lcloud.com'
            }
        },
        'stage': {
            'us-west-2': {
                'certArn': 'arn:aws:acm:us-west-2:180770971501:certificate/6b38b584-99ee-4df0-a6f9-46c0775d486d',
                'certName': '*.stage.aws.lcloud.com',
                'domainName': 'service-name-us-west-2.stage.aws.lcloud.com'
            }
        }
        // add prod here
    };

    return {
        dynamoDBPrefix: dynamoDBPrefix,
        deploymentBucket: deploymentBucket,
        webviewGatewayConfiguration: webviewGateway[stage] ? webviewGateway[stage][region] : null,
    }
};
