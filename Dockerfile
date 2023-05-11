FROM python:latest

WORKDIR /usr/src/broadwayRunner

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./
#CMD ["tail", "-f", "/dev/null"]
CMD [ "python" , "./runDefault.py"]