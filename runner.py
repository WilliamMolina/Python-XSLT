import lxml.etree as ET
import xmltodict, dicttoxml
import os, datetime, io, json
import boto3
import requests
from pytz import timezone

#set timezone
tz = timezone('America/Bogota')
fmt = "%Y%m%d%H%M%S"
fmt_elastic = "%Y-%m-%dT%H:%M:%S-05:00"

s3 = boto3.client('s3')

BUCKET = os.getenv('BUCKET')

def transxslt(event, content):

    obj = ET.fromstring(event['body'])

    #dom = ET.parse(obj)
    xslt = ET.parse("XSLT/transformation.xsl")
    transform = ET.XSLT(xslt)
    newdom = transform(obj)
    res= ET.tostring(newdom, pretty_print=False)
    response= res.decode("utf-8")
    
    r = requests.post('https://j2dihjgwn9.execute-api.us-east-1.amazonaws.com/dev/xml', data = response)

    save(r.text)

    return {
        'statusCode':200,
        'body': response,
        'headers': {
            'Content-Type': 'application/xml',
        }
    }

def save(response):
    fechaHora = datetime.datetime.now(tz).strftime(fmt)  
    s3.put_object(
        Bucket=BUCKET,
        Key=f'{fechaHora}.xml',
        Body=response,
    )