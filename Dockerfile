FROM python:3.7-alpine
RUN adduser -D matrixexplorer
WORKDIR /home/matrixexplorer
COPY --chown=matrixexplorer:matrixexplorer requirements.txt ./
RUN python -m venv venv
RUN apk add --no-cache libstdc++ \
    && apk add --no-cache --virtual .build-deps \
        build-base openssl-dev libffi-dev \
    && venv/bin/pip install --upgrade pip \
    && venv/bin/pip install --no-cache-dir -r requirements.txt \
    && venv/bin/pip install gunicorn \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps\
    && apk del .build-deps
COPY --chown=matrixexplorer:matrixexplorer . /home/matrixexplorer/
USER matrixexplorer
EXPOSE 8080
CMD source venv/bin/activate && gunicorn -b 0.0.0.0:8080 --access-logfile - --error-logfile - app:server