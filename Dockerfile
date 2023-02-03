FROM python:3.10
WORKDIR /opt/cmu-trustm
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD uvicorn --host 0.0.0.0 server:app
