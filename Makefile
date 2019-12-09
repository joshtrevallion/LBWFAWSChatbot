PROJECT_NAME=lbwf-chatbot
S3_BUCKET=dasmthc-lbwf-chatbot
S3_WEB_BUCKET=lbwfchatbot-website
API_KEY=Y9svZs2PPUqdGDQFCd45cQ20776

install:
	pip install -r requirements-dev.txt

clean:
	pip freeze --local | xargs pip uninstall -y

build:
	sam build --template samTemplate.yaml

package:
	sam package --template-file samTemplate.yaml --output-template-file samTemplate-output.yaml --s3-bucket $(S3_BUCKET)

deploy:
	aws cloudformation deploy --template-file samTemplate-output.yaml --stack-name $(PROJECT_NAME) --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --parameter-overrides ProjectName=lbwfchatbot APIKey=$(API_KEY)

all: clean install build package deploy update_website

log:
	aws cloudformation describe-stack-events --stack-name $(PROJECT_NAME)

invoke:
	sam local invoke --template samTemplate.yaml ChatBotFunction --event lambda_chatbot/events/QOne_danger.json 
	sam local invoke --template samTemplate.yaml ChatBotFunction --event lambda_chatbot/events/QOne_no-danger.json 

test:
	python -m pytest

update_website:
	aws s3 cp ./website s3://$(S3_WEB_BUCKET)/ --recursive --exclude "*.yaml" --acl public-read

.PHONY: install clean build package deploy all log invoke test update_website
