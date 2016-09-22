hint:
	@echo "virtualenv -p /usr/bin/python3.5 venv"
	@echo "source venv/bin/activate"
	@echo "pip install -r requirements.txt"

run:
	python run.py -c dev

init:
	python init.py -c dev --drop

test:
	python test.py

coverage:
	coverage run test.py
	coverage report -m  --omit venv/*.py
