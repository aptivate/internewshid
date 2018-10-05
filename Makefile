PIPENV := pipenv run

apply-isort:
	@$(PIPENV) isort \
	--recursive \
	--apply \
	--settings-path=setup.cfg
.PHONY: apply-isort

isort:
	@$(PIPENV) isort \
	--quiet \
	--recursive \
	--check-only \
	--diff \
	--settings-path=setup.cfg
.PHONY: isort

pylava:
	@ls -d */ | xargs $(PIPENV) pylava
.PHONY: pylava

checks:
	$(PIPENV) python manage.py check
	$(PIPENV) python manage.py makemigrations --check
.PHONY: checks

style: isort pylava
.PHONY: style

test:
	$(PIPENV) pytest -v --cov
.PHONY: test

gitlab-ci: checks style test
.PHONY: gitlab-ci
