from flask import Flask, request
import git
import logging
from service_properties import GITHUB_REPO, APP_NAME
import uuid
import json
import os
import shutil
from subprocess import Popen, PIPE

# Base git dir name
BASE_GIT_DIR_NAME = "gitdir"

def setupLoggerAndDir():
   logger = logging.getLogger('webhook-service')
   logger.setLevel(logging.DEBUG)
   ch = logging.StreamHandler()
   ch.setLevel(logging.DEBUG)
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -'
                                 ' %(message)s')
   ch.setFormatter(formatter)
   logger.addHandler(ch)

   os.makedirs("./%s" % BASE_GIT_DIR_NAME, exist_ok=True)

   return logger

def cloneRepo(repoUrl, logger):
   """Clone repo using @repoUrl"""

   logger.info("Fetching latest code")
   dirName = str(uuid.uuid4())
   dirPath = "./%s/%s" % (BASE_GIT_DIR_NAME, dirName)
   os.makedirs(dirPath, exist_ok=True)
   try:
      git.Git(dirPath).clone(repoUrl)
   except Exception:
      logger.exception("Unable to clone repo")
      raise
   dirPath = "%s/%s" % (dirPath, APP_NAME)

   return dirPath

def cleanRepo(dirPath):
   """"""
   dirPath = dirPath.split(APP_NAME)[0][:-1]
   shutil.rmtree(dirPath)

def executeCommand(command):
   """Execute command using subprocess module"""

   command = command.split()
   process = Popen(command, stdout=PIPE, stderr=PIPE)
   stdout, stderr = process.communicate()
   if stderr:
      raise Exception(stderr)

def buildDockerImage(logger, dirPath):
   """Build docker image using @dirPath and return image tag Name"""

   logger.info("Building docker image: %s" % dirPath)
   imageTagName = "%s:%s" % (APP_NAME, str(uuid.uuid4()).split("-")[0])
   logger.info("Using Build Tag: %s" % imageTagName)
   try:
      executeCommand("docker build -t %s %s" % (imageTagName, dirPath))
   except Exception:
      logger.exception("Building docker image failed: %s" % dirPath)
      raise
   logger.info("Build Image with tag: %s" % imageTagName)

   return imageTagName

def deployApp(imageTag):
   """
   """
   logger.info("Deploying image with tag: %s" % imageTag)
   appName = imageTag.replace(":", "")
   deployCommand = ("kubectl run %s --image=%s --port=5000 "
                    "--image-pull-policy=Never" % (appName, imageTag))
   logger.info("Deploy Command: %s" % deployCommand)
   try:
      executeCommand(deployCommand)
   except Exception:
      logger.exception("Deploying docker image failed: %s" % imageTag)
      raise
   return appName

def exposeAppService(appName):
   """
   """
   exposeAppCmd = "kubectl expose deployment %s --type=LoadBalancer" % appName
   logger.info("Exposing app: %s" % appName)
   logger.info("Expose app command: %s" % exposeAppCmd)
   try:
      executeCommand(exposeAppCmd)
   except Exception:
      logger.exception("Exposing App failed: %s" % appName)
      raise
   logger.info("Exposed app %s on Cluster sucessfully" % appName)

def triggerDeploy(logger):
   deploymentData = {}
   dirPath = cloneRepo(GITHUB_REPO, logger)
   imageTag = buildDockerImage(logger, dirPath)
   appName = deployApp(imageTag)
   exposeAppService(appName)
   deploymentData = {"ServiceName" : appName,
                     "DeploymentName" : appName,
                     "DockerImageTag": imageTag}
   return dirPath, deploymentData

app = Flask(__name__)
logger = setupLoggerAndDir()

@app.route('/triggerDeploy', methods=['GET', 'POST'])
def hello_world():
   logger.info(request.data)
   try:
      dirPath, deploymentData = triggerDeploy(logger)
   except Exception as e:
      logger.exception(str(e))
      return json.dumps({ "error": str(e) }), 500
   else:
      cleanRepo(dirPath)

   return json.dumps({ "data": deploymentData }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
