.PHONY: build run clean

# Default number of records if not provided on command line: make run NUM_RECORDS=500
NUM_RECORDS ?= 1000
CONTAINER_NAME ?= sample-data-container

# Build the Docker image
build:
	docker build -t sample-data-generator .

# Run the Docker container
run:
	@echo "Running with NUM_RECORDS=$(NUM_RECORDS)"
	@if docker ps -a --format '{{.Names}}' | grep -w $(CONTAINER_NAME) >/dev/null 2>&1; then \
	  echo "Container $(CONTAINER_NAME) exists. Removing..."; \
	  docker rm -f $(CONTAINER_NAME) >/dev/null; \
	fi
	docker run -e NUM_RECORDS=$(NUM_RECORDS) --name $(CONTAINER_NAME) -it sample-data-generator
	docker cp $(CONTAINER_NAME):app/sampledata_duckdb.db ./sampledata_duckdb.db
	duckdb sampledata_duckdb.db

# Connect back to duckdb 
duckdb:
	duckdb sampledata_duckdb.db

# Make csvs ouputs available for futher local processing
csvs:
	docker cp sample-data-container:app/products.csv ./products.csv 
	docker cp sample-data-container:app/transactions.csv ./transactions.csv 
	docker cp sample-data-container:app/user_profiles.csv ./user_profiles.csv 

# Stop and remove the container, image and generated files
clean:
	docker stop sample-data-container || true
	docker rm sample-data-container || true
	docker rmi sample-data-generator || true
	python3 clean_files.py