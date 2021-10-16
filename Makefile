CONDABASE=$(shell conda info --base)
DIST=`pwd`/dist/
FRAMEWORKS=$(DIST)/Concertista.app/Contents/Frameworks
SRC=concertista

all:
	@echo ""

create-venv:
	@python -m venv venv

init:
	@pip install -e .
	@pip install -r requirements/devel.txt

syntax-check check-syntax:
	@flake8 $(SRC) tests setup.py

test:
	@PYTEST_QT_API=pyqt5 pytest .

coverage:
	@PYTEST_QT_API=pyqt5 coverage run --source=$(SRC) -m pytest -v -s
	@coverage html

app:
	@python setup.py py2app
	@cp $(CONDABASE)/lib/libffi.7.dylib $(FRAMEWORKS)
	@cp $(CONDABASE)/lib/libssl.1.1.dylib $(FRAMEWORKS)
	@cp $(CONDABASE)/lib/libcrypto.1.1.dylib $(FRAMEWORKS)
