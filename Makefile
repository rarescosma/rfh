PROJECT=rfh
ENTRYPOINT=$(PROJECT)/main.py
PREFIX?=$(HOME)
DESTDIR?=$(PREFIX)/bin

all: dist/$(PROJECT)

dist/$(PROJECT): .venv/freeze
	. .venv/bin/activate && pip install pyinstaller==4.5.1 && pyinstaller --onefile $(ENTRYPOINT) -n $(PROJECT)

install: dist/$(PROJECT)
	mkdir -p $(DESTDIR)
	cp dist/$(PROJECT) $(DESTDIR)/$(PROJECT)
	chmod 755 $(DESTDIR)/$(PROJECT)

clean:
	rm -rf dist build *.spec __pycache__ *.egg-info .python-version .venv
	rm -f $(DESTDIR)/$(PROJECT)

.python-version:
	pyenv local 3.9.4

.venv/freeze: .python-version
	test -f .venv/bin/activate || python3 -mvenv .venv --prompt $(PROJECT)
	. .venv/bin/activate && pip install -e . && pip freeze > .venv/freeze
