PREFIX=/usr/local

all:

install:
	cp -r lib/devo $(PREFIX)/lib/
	cp -r bin/* $(PREFIX)/bin/
