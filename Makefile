mkfile_path := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))


install:
	virtualenv --no-site-packages $(mkfile_path).env
	( . $(mkfile_path).env/bin/activate ; pip install -r requirements.txt ; deactivate )
	( cd $(mkfile_path).env/lib/python2.7/site-packages ; ln -sfT /usr/lib/python2.7/dist-packages/pysvn pysvn )
	ln -sf $(mkfile_path)bin/ksvn.sh ~/bin/ksvn
