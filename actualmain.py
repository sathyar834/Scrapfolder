from updatedscript import *
from flask import Flask,jsonify,request
import json
import boto3
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler('logfile.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


client = boto3.client('organizations')

app=Flask(__name__)

@app.route("/listroot",methods=["GET"])
def root():
  rootId=list_roots()
  return rootId

@app.route("/createou",methods=["POST"])
def create_ou():
  create_organizational_units()
  return("OU Succesfully Created")

@app.route("/listou",methods=["GET"])
def list_ou():
  OUdict = list_organizational_units()
  return OUdict

@app.route("/createaccount",methods=["POST"])
def create_acc():
  event= request.get_json(force=True)
  status = create_account()
  return status

@app.route("/listaccounts",methods=["GET"])
def list_acc():
  event= request.get_json(force=True)
  finaldict = list_accounts()
  return finaldict

@app.route("/moveaccount",methods=["POST"])
def move_acc():
  event= request.get_json(force=True)
  move_account()
  return("Accounts are moved to respective Destination")

@app.route("/createscp",methods=["POST"])
def create_scp():
  event= request.get_json(force=True)
  create_scp_policy()
  return("SCP Policy Created Successfully")

@app.route("/listscp",methods=["GET"])
def list_scp():
  event= request.get_json(force=True)
  scpdict = list_scp_policy()
  return scpdict

@app.route("/attachscp",methods=["POST"])
def attach_scp():
  event= request.get_json(force=True)
  attach_scp_policy()
  return("SCP Policy attached Successfully")


if __name__ == "__main__":
  app.run(debug=True)
