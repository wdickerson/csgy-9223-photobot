import boto3, json, os, requests
from sign import get_signed_headers

lex_client = boto3.client('lexv2-runtime')


def lambda_handler(event, context):
    # ************* BUILD ENDPOINT AND PAYLOAD *************
    qs_params = event.get('queryStringParameters') or {}
    user_input = qs_params.get('q', '')
    lex_response = lex_client.recognize_text(
        botId=os.environ['LEX_BOT_ID'],
        botAliasId=os.environ['LEX_ALIAS_ID'],
        localeId='en_US',
        sessionId='id',
        text=user_input,
    )

    interpretations = lex_response['interpretations']
    interpretation = next(
        intent for intent in interpretations 
        if intent['intent']['name'] == 'SearchIntent'
    )
    intent = interpretation['intent']
    slot = intent.get('slots', {}).get('label', None)
    
    resolved_labels = [
        (
            value['value']['resolvedValues'][0] 
            if len(value['value']['resolvedValues']) > 0
            else value['value']['interpretedValue']
        )
        for value in (slot or {}).get('values', []) or []
    ]

    print('HERE!!! resolved labels')
    print(json.dumps(resolved_labels))
    query_text = ' '.join(resolved_labels) if len(resolved_labels) > 0 else user_input
    print('HERE!!! query_text')
    print(json.dumps(query_text))

    payload = {
        "size": 25,
        "query": {
            "match": {
                "labels": {
                    "query": query_text,
                    "fuzziness": "AUTO"
                }
            }
        }
    }
    endpoint = f"https://{os.environ['OPENSEARCH_ENDPOINT']}/photos/_search"

    # ************* SIGN THE REQUEST *************
    headers = get_signed_headers(
        method='GET',
        payload=payload,
        service='es',
        host=os.environ['OPENSEARCH_ENDPOINT'],
        canonical_uri='/photos/_search',
        request_parameters='',
        region = 'us-east-1',
    )

    # ************* SEND THE REQUEST *************
    r = requests.get(endpoint, headers=headers, data=json.dumps(payload))

    # ************* SEND THE RESPONSE *************
    if r.json().get('hits', {}).get('total', {}).get('value', 0) == 0:
        return {
            "statusCode": 200,
            "headers": { "Access-Control-Allow-Origin": '*' },
            "body": json.dumps({ "results": [] }),
        }

    response_body = {
        "results": [{
            "url": f"https://{os.environ['S3_BUCKET_ENDPOINT']}/{hit.get('_id')}",
            "labels": hit.get('_source', {}).get('labels', []),
        } for hit in r.json()['hits']['hits']]
    }

    return {
        "statusCode": 200,
        "headers": { "Access-Control-Allow-Origin": '*' },
        "body": json.dumps(response_body),
    }
