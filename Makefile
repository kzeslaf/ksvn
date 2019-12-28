mkfile_path := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: env clean install uninstall

all:
	@echo "usage:\n\tmake env|install|uninstall|clean"

env:
	python3 -m venv $(mkfile_path).env
	( . $(mkfile_path).env/bin/activate ; pip install --upgrade pip; pip install -r requirements.txt ; deactivate )
	( cd $(mkfile_path).env/lib/python3.5/site-packages ; ln -sfT /usr/lib/python3/dist-packages/pysvn pysvn )

clean:
	rm -rI $(mkfile_path).env

install: env
	ln -sf $(mkfile_path)bin/ksvn.sh ~/bin/ksvn

uninstall:
	rm -rI ~/bin/ksvn
