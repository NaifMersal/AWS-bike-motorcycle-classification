#serializeImageData

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key']
    bucket =  event['s3_bucket']
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, '/tmp/image.png')
    
    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }


#imageClassifier

import json
import base64
import sys
sys.path.append("./packages.zip")
from sagemaker.serializers import IdentitySerializer
import sagemaker

ENDPOINT = 'image-classification-2023-07-23-11-13-42-624'

def lambda_handler(event, context):
    # Decode the image data
    image = base64.b64decode(event["image_data"])

    # Instantiate a Predictor
    predictor  = sagemaker.Predictor(ENDPOINT,sagemaker_session=sagemaker.Session())

    # For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    # Make a prediction:
    inferences =predictor.predict(image, initial_args={'ContentType': 'application/x-image'}) 

    # We return the data back to the Step Function
    event["inferences"] = inferences.decode('utf-8')
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }


#filter
import json


THRESHOLD = .92


def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = eval(event["inferences"])
    event["inferences"]=inferences
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(pre>THRESHOLD for pre in inferences)
    
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': event
    }
