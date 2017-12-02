mkfile_path := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))


install:
	ln -sf $(mkfile_path)bin/ksvn.py ~/bin/ksvn
