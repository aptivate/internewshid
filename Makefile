PROJECT_NAME := internewshid
MANAGEPY     := python manage.py
PIPENVRUN    := pipenv run
PROJECT_ROOT := .
SOURCE_DIR   := $(PROJECT_ROOT)/$(PROJECT_NAME)/
FIXTURES_DIR := $(PROJECT_NAME)/hid/fixtures

lint:
	@$(PIPENVRUN) pylava -o setup.cfg $(SOURCE_DIR)
.PHONY: lint

sort:
	$(PIPENVRUN) isort -c -rc --diff -sp setup.cfg $(SOURCE_DIR)
.PHONY: sort

test:
	@$(PIPENVRUN) pytest --cov=$(PROJECT_NAME)
.PHONY: test

sudan-db-reset:
	$(PIPENVRUN) $(MANAGEPY) reset_db && \
	$(PIPENVRUN) $(MANAGEPY) migrate && \
	$(PIPENVRUN) $(MANAGEPY) loaddata $(FIXTURES_DIR)/sudan.json && \
	$(PIPENVRUN) $(MANAGEPY) loaddata $(FIXTURES_DIR)/taxonomies.json
.PHONY: sudan-db-reset
