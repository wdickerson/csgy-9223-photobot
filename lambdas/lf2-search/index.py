import json, os, requests
from sign import get_signed_headers


def lambda_handler(event, context):

    # ************* BUILD ENDPOINT AND PAYLOAD *************
    qs_params = event.get('queryStringParameters') or {}
    es_label = qs_params.get('q', '')
    payload = {
        "query": {
            "match": {
                "labels": {
                    "query": ' '.join([es_label]),
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
            "body": json.dumps([]),
        }

    response_body = [{
        "url": f"https://{os.environ['S3_BUCKET_ENDPOINT']}/{hit.get('_id')}",
        "labels": hit.get('_source', {}).get('labels', []),
    } for hit in r.json()['hits']['hits']]

    return {
        "statusCode": 200,
        "headers": { "Access-Control-Allow-Origin": '*' },
        "body": json.dumps(response_body),
    }
