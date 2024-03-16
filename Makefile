PROJECT=rfh
ENTRYPOINT=$(PROJECT)/main.py
PREFIX?=$(HOME)
DESTDIR?=$(PREFIX)/bin
BUILDPATH=dist/static
BUILD_VERSION:=latest
ARCH=linux-x86_64

all: dist/$(PROJECT)

dist/$(PROJECT): .venv/freeze
	. .venv/bin/activate && pip install pyinstaller\>=5.1 && pyinstaller --onefile $(ENTRYPOINT) -n $(PROJECT)

install: dist/$(PROJECT)
	mkdir -p $(DESTDIR)
	cp dist/$(PROJECT) $(DESTDIR)/$(PROJECT)
	chmod 755 $(DESTDIR)/$(PROJECT)

clean:
	rm -rf dist build *.spec __pycache__ *.egg-info .python-version .venv
	rm -f $(DESTDIR)/$(PROJECT)

.python-version:
	pyenv local 3.11.1

.venv/freeze: .python-version
	test -f .venv/bin/activate || python3 -mvenv .venv --prompt $(PROJECT)
	. .venv/bin/activate && pip install -e . && pip freeze > .venv/freeze
	patch -p0 -d .venv/lib/python3.11/site-packages/tuyapy --forward --reject-file=- < tuya.patch || true

.PHONY: test
test:
	. .venv/bin/activate && pip install --no-cache-dir pytest && pytest

build_static:
	./portable/alpine-build.sh

pack_static:
	@rm -rf pack
	@mkdir -p pack
	@cd ${BUILDPATH} && tar -czvf ${PROJECT}-${BUILD_VERSION}-$(ARCH).tar.gz *
	@mv ${BUILDPATH}/${PROJECT}-${BUILD_VERSION}-$(ARCH).tar.gz pack
	@openssl sha256 < pack/${PROJECT}-${BUILD_VERSION}-$(ARCH).tar.gz | sed 's/^.* //' > pack/${PROJECT}-${BUILD_VERSION}-$(ARCH).sha256sum
	@cat pack/${PROJECT}-${BUILD_VERSION}-$(ARCH).sha256sum
