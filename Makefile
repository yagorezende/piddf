.PHONY: build
build:
	@echo "Building..."
	@cd orb && make clean orb-docker build-orb-cli-binaries extract-orb-cli-binaries

.PHONY: run
run:
	@echo "Running..."
	@docker compose -f docker-compose.yaml up --build

.PHONY: run-sample-orb
run-sample-orb:
	@echo "Running sample orb..."
	@cd orb/samples/tutorial && docker compose -f docker-compose-cli.yml -f ../docker/docker-compose-dev.yml up

.PHONY: stop-sample-orb
stop-sample-orb:
	@echo "Stopping sample orb..."
	@cd orb/samples/tutorial && docker compose -f docker-compose-cli.yml -f ../docker/docker-compose-dev.yml down

.PHONY: destroy
destroy:
	docker compose down -v --rmi all --remove-orphans
	docker system prune -af --volumes
	docker container prune
	docker network prune
	docker image prune -a
	@echo "Docker environment destroyed."
