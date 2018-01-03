init:
	virtualenv venv
	source venv/bin/activate
	venv/bin/pip install rpython

test:
	venv/bin/py.test src/
	
build:
	venv/bin/rpython src/targethoe.py
	rm -rf henv
	mkdir -p henv/bin
	mkdir -p henv/lib
	mkdir -p henv/include
	mv ./hoe henv/bin
	cp -R pkg henv

all: test build
