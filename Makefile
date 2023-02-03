build:
	docker build -t cmu/trustm .

run:
	docker run -itp 8000:8000 cmu/trustm
