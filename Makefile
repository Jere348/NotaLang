FILENAME = NotaLang.g4
PREFIX = $(basename $(FILENAME))
ANTLR_JAR ?= /usr/local/lib/antlr-4.13.1-complete.jar

all:
	java -jar $(ANTLR_JAR) -Dlanguage=Python3 -visitor $(FILENAME) -o gen/
	touch gen/__init__.py

test:
	@for f in tests/*.nota; do echo "\n########## $$f"; python3 main.py $$f; done

clean:
	rm -f gen/$(PREFIX)*.py gen/$(PREFIX)*.tokens gen/$(PREFIX)*.interp

