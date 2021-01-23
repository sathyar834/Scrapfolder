import json
import time
import boto3
from botocore.exceptions import ClientError
import re
from flask import Flask,jsonify,request
import logging



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('logfile.log')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


client = boto3.client('organizations')


def list_roots():
  global rootId
  logger.info('Listing the roots of the AWS account')
  rootId_response = client.list_roots(
  )
  rootId = rootId_response['Roots'][0]['Id']
  logger.info("RootId: %s",rootId)
  return {"RootId":rootId}

def global_variables_to_create_ou():
  event= request.get_json(force=True)
  global list_of_OUNames
  global list_of_ParentId
  list_of_OUNames = event["Enter the list of names on which the OU has to be created"]
  list_of_ParentId = event["Enter the Id of the parent where the OU has to be created"]

def global_variables_to_list_ou():
  event= request.get_json(force=True)
  global OU_parentId_list
  OU_parentId_list = event["Enter the Id of the parent OU whose child OUs you want to list"]

def global_variables_for_account():
  event= request.get_json(force=True)
  global list_of_Emails
  global list_of_Names
  list_of_Emails = event["Enter the list of Emails to create account"]
  list_of_Names = event["Enter the names for the respective Emails to create account"]

def create_organizational_units():
  logger.info('Create Organizational Units')
  global_variables_to_create_ou()
  for x,y in zip(list_of_ParentId,list_of_OUNames):
    try:
      Create_OU_response = client.create_organizational_unit(
      ParentId= x,
      Name=y
      )
      time.sleep(10)
    except ClientError as e:
      logger.exception('Client Error!! %s',e)
      raise e
  logger.info('Organizational Units Created Succesfully')

def list_organizational_units():
  logger.info('Listing the Organizational Units for the Respective Parent')
  global_variables_to_list_ou()
  OUnames_list = []
  OUId_list = []
  for x in OU_parentId_list:
    try:
      list_OU_response = client.list_organizational_units_for_parent(
        ParentId=x,
      )
      NameofOU = list_OU_response["OrganizationalUnits"]
      for y in NameofOU:
        for x in y.keys():
          for a in y.keys():
            Names = y["Name"]
            OUnames_list.append(Names)
            Ids = y["Id"]
            OUId_list.append(Ids)
            break
          break
    except ClientError as e:
      logger.exception('Client Error!! %s',e)
      raise e

  OUdict = {OUnames_list[i]: OUId_list[i] for i in range(len(OUnames_list))}
  OU_json = json.dumps(OUdict, indent=4)
  # print(OUdict)
  # keys = {k:OUdict[k] for k in (OUdict.keys() & list_of_OUNames)}
  # print(keys)
  logger.info('The Organizational Units for the Respective Parent are : %s',OU_json)
  return {"Organizational units":OUdict}

def list_accounts():
  logger.info('Listing all the Accounts')
  listresponse = client.list_accounts(
  )

  listmoreresponse = client.list_accounts(
    NextToken=listresponse["NextToken"]
  )

  AccountName = listresponse['Accounts']
  AccountNamemore = listmoreresponse['Accounts']

  Namelist =[]
  Idslist =[]
  for y in AccountName:
    for x in y.keys():
      for a in y.keys():
        Names = y["Name"]
        Namelist.append(Names)
        Ids = y["Id"]
        Idslist.append(Ids)
        break
      break

  Namelistmore =[]
  Idslistmore =[]
  for y in AccountNamemore:
    for x in y.keys():
      for a in y.keys():
        Names = y["Name"]
        Namelistmore.append(Names)
        Ids = y["Id"]
        Idslistmore.append(Ids)
        break
      break

  res = {Namelist[i]: Idslist[i] for i in range(len(Namelist))}

  resmore = {Namelistmore[i]: Idslistmore[i] for i in range(len(Namelistmore))}

  finaldict = dict(list(res.items()) + list(resmore.items()))
  accounts_json = json.dumps(finaldict, indent=4)
  logger.info('List of Accounts : %s',accounts_json)
  return{"Accounts":finaldict}


def list_existing_email():
  logger.info('Listing all the existing Emails from AWS Account')
  listresponse = client.list_accounts(
  )

  listmoreresponse = client.list_accounts(
    NextToken=listresponse["NextToken"]
  )

  AccountEmail = listresponse['Accounts']
  AccountEmailmore = listmoreresponse['Accounts']

  Emaillist =[]
  for y in AccountEmail:
    for x in y.keys():
      for a in y.keys():
        Email = y["Email"]
        Emaillist.append(Email)
        break
      break

  Emaillistmore =[]
  for y in AccountEmailmore:
    for x in y.keys():
      for a in y.keys():
        Email = y["Email"]
        Emaillistmore.append(Email)
        break
      break

  final_email_list = Emaillist + Emaillistmore
  logger.info('List of Emails : %s',final_email_list)
  return final_email_list

def create_account():
  logger.info('Creating an account')
  Existing_emails = list_existing_email()
  global_variables_for_account()
  Length_of_Emails = len(list_of_Emails)
  Length_of_Names = len(list_of_Names)

  if Length_of_Emails == Length_of_Names:
    for mail,name in zip(list_of_Emails,list_of_Names):
      for awsmail in Existing_emails:
        mailstatus = bool(re.search(r"^[\w\.\+\-]+\@[\w]+\.[a-z]{2,3}$", mail))
        if mailstatus == True:
          if mail == awsmail:
            status = "Invalid email"
            logger.exception('The email already exist!')
            return("The email already exist!")
          else:
            status = "Valid email"
        else:
          logger.exception('The email format is Invalid!')
          return("The email format is Invalid!")
      try:
        if status == "Valid email":
          cresponse = client.create_account(
            Email= mail,
            AccountName= name,
            IamUserAccessToBilling='ALLOW'
          )
      except ClientError as e:
        logger.exception('Client Error!! %s',e)
        raise e
    logger.info('Account created successfully')
    return("Account created successfully")
  else:
    logger.exception('Enter the respective names for the given Email!(The number of names and emails does not match')
    return("Enter the respective names for the given Email")

def global_variables_for_moving_accounts():
  event= request.get_json(force=True)
  global AccountId
  global SourceId
  global DestinationId
  AccountId = event["Enter the Ids of Accounts which you want to move"]
  DestinationId = event["Enter the Ids of respective Destination Account"]
  SourceId = event["Enter the Ids of respective Source Account"]

def global_variables_to_create_scp():
  event= request.get_json(force=True)
  global SCP_Description
  global SCP_Name
  global Document_name
  SCP_Description = event["Enter the List of Descriptions for SCP"]
  SCP_Name = event["Enter the List of Names for SCP"]
  Document_name = event["Enter the List of available Json Document Name"]

def global_variables_to_attach_scp():
  event= request.get_json(force=True)
  global SCP_PolicyId
  global SCP_TargetId
  SCP_PolicyId = event["Enter the List of SCP Policy Ids that you want to attach"]
  SCP_TargetId = event["Enter the List of respective Account Ids for the Policies chosen"]

def move_account():
  logger.info('Moving Account from Source Parent to Destination Parent')
  global_variables_for_moving_accounts()
  try:
    for a,b,c in zip(AccountId,SourceId,DestinationId):
      Moveresponse = client.move_account(
        AccountId= a,
        SourceParentId= b,
        DestinationParentId= c
      )
      logger.info('The Account %s moved to %s Successfully',a,c)
  except ClientError as e:
    logger.exception('Client Error!! %s',e)
    raise e

def create_scp_policy():
  logger.info('Create SCP policy')
  global_variables_to_create_scp()
  for a,b,c in zip(Document_name,SCP_Description,SCP_Name):
    if a == "scp_policy":
      with open('scp_policy.json') as f:
        data = json.load(f)
    elif a == "duplicatepolicy":
      with open('duplicatepolicy.json') as f:
        data = json.load(f)
    else:
      logger.exception('Invalid Document Name')
      return("Invalid Document Name")
    try:
      create_scp_response = client.create_policy(
      Content= data,
      Description= b,
      Name= c,
      Type='SERVICE_CONTROL_POLICY',
      )
      logger.info('SCP Policy created Successfully')
    except ClientError as e:
      logger.exception('Client Error!! %s',e)
      raise e

def list_scp_policy():
  logger.info('Listing all the SCP policies of the AWS account')
  list_scp_response = client.list_policies(
    Filter='SERVICE_CONTROL_POLICY',
  )
  listscpstatus = list_scp_response["Policies"]

  scpNamelist =[]
  scpIdslist =[]
  for y in listscpstatus:
    for x in y.keys():
      for a in y.keys():
        Names = y["Name"]
        scpNamelist.append(Names)
        Ids = y["Id"]
        scpIdslist.append(Ids)
        break
      break
  scpdict = {scpNamelist[i]: scpIdslist[i] for i in range(len(scpNamelist))}
  scp_json = json.dumps(scpdict, indent=4)
  logger.info('SCP Policies: %s',scp_json)
  return {"SCP Policies":scpdict}

def attach_scp_policy():
  logger.info('Attaching SCP policy')
  global_variables_to_attach_scp()
  try:
    for x,y in zip(SCP_PolicyId,SCP_TargetId):
      attachresponse = client.attach_policy(
        PolicyId= x,
        TargetId= y
      )
    logger.info("Policy attached Successfully")
  except ClientError as e:
    logger.exception('Client Error!! %s',e)
    raise e



