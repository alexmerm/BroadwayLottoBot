FROM python:latest

WORKDIR /usr/src/broadwayRunner

COPY requirements.txt ./
RUN apt-get update && \
apt-get install -y cron && \
rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py ./
ADD broadway-runner-cron /etc/cron.d/broadway-runner-cron
RUN chmod 0644 /etc/cron.d/broadway-runner-cron
RUN touch /cron.log
ENV TZ="America/New_York"
#CMD ["tail", "-f", "/dev/null"]
# CMD [ "python" , "./runDefault.py"]
CMD cron && tail -f /cron.log