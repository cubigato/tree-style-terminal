.DEFAULT_GOAL := deb

.PHONY: appimage appimage-check clean deb deb-check lint test

clean:
	rm -rf -- "$(CURDIR)/build"

appimage:
	./packaging/appimage/build.sh package

appimage-check:
	./packaging/appimage/build.sh check

deb:
	./packaging/debian/build.sh package

deb-check:
	./packaging/debian/build.sh check

test:
	.venv/bin/python -m pytest

lint:
	.venv/bin/python -m ruff check src tests
