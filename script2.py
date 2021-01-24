import json
import boto3
import logging
import logging.config


logging.config.fileConfig('C:/Users/Sathya R/Desktop/AWS project/config.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

client = boto3.client('organizations')

def scriptroot():
  logger.info('Listing the roots of the AWS account')
  rootId_response = client.list_roots(
  )
  rootId = rootId_response['Roots'][0]['Id']
  logger.info("RootId: %s",rootId)
  return {"RootId":rootId}