.DEFAULT_GOAL := deb

.PHONY: clean deb deb-check lint test

clean:
	rm -rf -- "$(CURDIR)/build"

deb:
	./packaging/debian/build.sh package

deb-check:
	./packaging/debian/build.sh check

test:
	.venv/bin/python -m pytest

lint:
	.venv/bin/python -m ruff check src tests
