# Photobot Index

A Lambda function that searches photos for the Photobot app, created in the final project of CS-GY 9223 at NYU.

The Lambda function is invoked via an API Gateway proxy. The function expects a search phrase from the user. It calls a Lex bot to extract labels from that phrase, then searches an OpenSearch index for those labels. It response with a list of matching image URLs.

## Development

Make changes to `index.py`. 

`test_lambda.py` is provided as a convenient way to execute your Lambda handler locally.

`.env.template` shows the expected environment variables.

## Deployment

This app is deployed to Lambda through a CodePipeline pipeline defined in https://github.com/wdickerson/csgy-9223-photobot-infrastructure. Any modification to the `main` branch results in a new deployment.
