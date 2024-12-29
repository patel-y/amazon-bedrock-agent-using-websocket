import boto3
import json
import io

# Initialize Bedrock client
bedrock_client = boto3.client('bedrock-runtime')



# Replace with your model ID and region
MODEL_ID = "amazon.titan-tg1-large"

def lambda_handler(event, context):
    print(event)
    connection_id = event['requestContext']['connectionId']
    user_message = event['body']
    print(user_message)

    api_gateway_client = boto3.client(
        'apigatewaymanagementapi', 
        endpoint_url = "https://" + event["requestContext"]["domainName"] + "/" + event["requestContext"]["stage"]
    )

    # Prepare request body for Bedrock
    

    # Call Bedrock
    response = bedrock_client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({"inputText": user_message}),
        accept="application/json",
        contentType="application/json"
    )

    print(response)
    # Read the StreamingBody content
    stream = io.BytesIO()
    for chunk in response['body'].iter_chunks():
        stream.write(chunk)
    stream.seek(0) 
    response_body_bytes = stream.read() 
    response_body_str = response_body_bytes.decode('utf-8') 
    response_body = json.loads(response_body_str) 

    # Extract the AI response
    ai_response = response_body.get('results', [{}])[0].get('outputText', 'Sorry, I didn’t understand that.')

    # Send response back to client
    api_gateway_client.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps({"response": ai_response})
    )

    return {'statusCode': 200}