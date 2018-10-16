PIPENV := pipenv run

apply-isort:
	@$(PIPENV) isort \
	--recursive \
	--apply \
	--settings-path=setup.cfg
.PHONY: apply-isort
