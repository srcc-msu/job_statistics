hint:
	@echo "python3.5 -m venv venv"
	@echo "source venv/bin/activate"
	@echo "pip install -r requirements.txt"
	@echo "python init.py -c prod --drop"

run:
	gunicorn --workers 4 --timeout 3600 --bind 0.0.0.0:5000 wsgi:app

test:
	python test.py

coverage:
	coverage run test.py
	coverage report -m  --omit venv/*.py
