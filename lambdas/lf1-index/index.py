def lambda_handler(event, context):
    # ************* SEND THE RESPONSE *************
    return {
        "statusCode": 200,
        "headers": { "Access-Control-Allow-Origin": '*' },
        "body": "coming soon",
    }
