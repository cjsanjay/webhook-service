Webhook service for triggering automated deployment on kubernetes on github push

These setup steps are relevant for Mac OS sierra
Assumed setup
- Kubernetes setup with local docker environment and right driver
- python3.7, virtualenv and pip3 installed in system(There is openTLS issue with Mac. Ensure your OPENSSSL version is 2018)
- Download ngrok and do setup steps until setp 3 provided on URL: https://ngrok.com/download

1. Fork App Code and clone to local
   - Fork code from app repository to your own github: https://github.com/cjsanjay/hello-node.git
   - Note fork code github url <APP_CODE_URL>
   - clone code to your local environment

2. Clone webhook-service code from github to your local directory
   - git clone https://github.com/cjsanjay/webhook-service.git

3. Move to app directory, setup and activate virtualenv
 - cd webhook-service
 - virtualenv venv-webhook-service --python=python3.7
 - source venv-webhook-service/bin/activate
 - pip3 install -r requirements.txt

4. Edit service_properties.py and change GITHUB_REPO with your noted    
   APP_CODE_URL

5. start minikube
   - minikube start --vm-driver=hyperkit

6. Run setup script
   - sh setup.sh

7. Run app
   - python3 webhook_service.py
   - Leave this terminal open

8. Setup ngrok tunnel session in another terminal window
   - Open terminal window and move to ngrok installed location
   - Start ngrok tunnel session: ./ngrok http 5000
   - <NGROK_URL> Copy the ngrok URL provided in output: Forwarding http://592304d1.ngrok.io -> localhost:5000

9. Use ngrok url to setup webhook in APP_CODE_URL
 - go to APP_CODE_URL on github and navigate to settings> webhooks> Add webhook
 - Paste following in Payload URL section:
   NGROK_URL/triggerDeploy
 - Hit Add Webhook

10. Step 9 should trigger deployment process, on webhook service.

11. Modify hello world statement in App code and push code to APP_CODE_URL
  - This would trigger deployment on backend side
  - service will generate logs
  - use logline <Exposed app hello-nodec0e2fa00 on Cluster successfully> to get service_name
  - view service using service name > minikube service hello-nodec0e2fa00
  - You should see hello world statement on browser

12. Repeat step 11 to verify

13. Tear down is manual in this version
 - Use following commands to clear spawned services and deployments
   - kubectl delete service <service_name>
   - kubectl delete deployment <deployment_name>
 - Stop webhook_service from step7 using ctrl+c and deactivate virtualenv
 - Stop ngrok from step 8 using ctrl+c
 - Clear webhook from APP_CODE_URL
 - Run sh deactivate.sh
