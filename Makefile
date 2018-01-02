init:
	virtualenv venv
	source venv/bin/activate
	venv/bin/pip install rpython

test:
	venv/bin/py.test src/
	
build:
	venv/bin/rpython src/targethoe.py

all: test build
