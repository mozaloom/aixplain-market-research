ecr:
	docker build -t market-agent .
	@echo "Set ACCOUNT_ID first: export ACCOUNT_ID=\$$(aws sts get-caller-identity --query Account --output text)"
	@test -n "$(ACCOUNT_ID)" || (echo "ACCOUNT_ID not set" && exit 1)
	docker tag market-agent:latest $(ACCOUNT_ID).dkr.ecr.us-east-1.amazonaws.com/market-agent:latest
	docker push $(ACCOUNT_ID).dkr.ecr.us-east-1.amazonaws.com/market-agent:latest
	aws lambda update-function-code --function-name market-agent-2 --image-uri $(ACCOUNT_ID).dkr.ecr.us-east-1.amazonaws.com/market-agent:latest


