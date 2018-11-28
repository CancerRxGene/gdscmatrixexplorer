FROM python:3.6-slim

RUN adduser matrixexplorer --disabled-password

WORKDIR /home/matrixexplorer

COPY --chown=matrixexplorer:matrixexplorer . /home/matrixexplorer/

RUN pip install -r requirements.txt
RUN pip install gunicorn

USER matrixexplorer

EXPOSE 8080

CMD gunicorn -b 0.0.0.0:8080 --access-logfile - --error-logfile - index:server
