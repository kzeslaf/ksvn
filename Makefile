mkfile_path := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: env clean install uninstall

all:
	@echo "usage:\n\tmake env|clean|install|uninstall"

env:
	python3 -m venv --system-site-packages $(mkfile_path).env
	. $(mkfile_path).env/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

clean:
	rm -rI $(mkfile_path).env

install: env
	ln -sf $(mkfile_path)bin/ksvn.sh ~/bin/ksvn

uninstall:
	rm -rI ~/bin/ksvn
