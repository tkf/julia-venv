PROJECT = julia_venv

.PHONY: test clean clean-pycache inject-readme upload

## Testing
test: inject-readme
	tox

test-cov: test-cov-py2 test-cov-py3

test-cov-py2 test-cov-py3: \
test-cov-%: inject-readme
	tox -e $* -- --cov $(PROJECT) --cov-report term \
		--cov-report html:$(PWD)/.tox/$*/tmp/cov_html

clean: clean-pycache
	rm -rf src/*.egg-info .tox MANIFEST

clean-pycache:
	find src -name __pycache__ -o -name '*.pyc' -print0 \
		| xargs --null rm -rf

## Inject content of README.rst to the docstring of __init__.py.
inject-readme: src/$(PROJECT)/__init__.py
src/$(PROJECT)/__init__.py: README.rst
	sed '1,/^"""$$/d' $@ > $@.tail
	rm $@
	echo '"""' >> $@
	cat README.rst >> $@
	echo '"""' >> $@
	cat $@.tail >> $@
	rm $@.tail
# Note that sed '1,/^"""$/d' prints the lines after the SECOND """
# because the first """ appears at the first line.

## Upload to PyPI
upload: inject-readme
	rm -rf dist/
	python setup.py sdist
	twine upload dist/*
