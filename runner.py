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

def post_xml(event, context):
    namespaces = {
        "https://www.w3schools.com/xml/":None,
        "http://www.w3.org/2001/XMLSchema-instance":None,
        "http://www.w3.org/2001/XMLSchema":None,
        "http://schemas.xmlsoap.org/soap/envelope/":None,
        "http://prueba.com.co/serviciosoap/v1": None
    }
    obj = xmltodict.parse(event['body'], process_namespaces=True, namespaces=namespaces)
    return respuesta_soap(obj["Envelope"]["Body"]["rentalProperties"])

    #return obj

def respuesta_soap(resp):
    body_start = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:v1=\"http://prueba.com.co/serviciosoap/v1\"><soap:Body><v1:rentalPropertiesResponse>"
    body_end = "</v1:rentalPropertiesResponse></soap:Body></soap:Envelope>"
    my_item_func = lambda x: None  
    return {
        'statusCode':200,
        'body': body_start + dicttoxml.dicttoxml(resp, attr_type=False, root=False, item_func=my_item_func).replace(b'<None>',b'').replace(b'</None>',b'').decode("utf-8") + body_end,
        'headers': {
            'Content-Type': 'application/xml',
        }
    }
