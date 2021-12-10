# python-flask-serverless-template
Originally adapted from the `lithiumtech/pci-handler` repository, use this to quickly spin up a new Python3 Flask Lambda using Serverless

### Important Files
1. `app.py` is the "entry point" for the Python Flask server
2. `templates` directory contains the Jinja2 templates. Easy to google syntax and help on StackOverflow with "flask jinja template" keywords
3. `serverless-config.js` allows you to pass parameters into the serverless.yml file and then, into environment variables in app.py
4. `serverless.yml` easily googleable for help because `serverless` is a very common Lambda utility
5. `cloudformation-template-update-stack.yaml` is for setting up the dependencies that serverless needs - S3, Api Gateway etc. Serverless is good at "modifying" stuff in-place but does not know how to create it. Use regular old cloudformation to do this. Example commands can be found in `deployment-commands-cloudformation.sh`
6. All the Jenkinsfiles - they will require heavy modification because Jenkins sucks

### Amenities
Various Python amenities are included. Specifically,
1. Dynamo client with some models.py examples for using these objects in Python code and the Jinja2 templates
2. HMAC client for hitting other microservices in the caredev/careprod AWS infrastructure
3. AWS Secrets Manager client
4. Signature Service that takes uses an HMAC key from Secrets Manager and checks the signature of UUIDv3 format
5. Custom Logger set up
6. ml-processor client as an example of using HMAC client. Not batteries included and has some pci specific code to change!

### Local Development
Use `./startServer.sh` locally to run the Flask server and test it out with http://localhost:5000/your/path/here
