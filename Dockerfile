FROM python:3.10-slim-bullseye
ENV FLIT_ROOT_INSTALL=1
ENV PYTHONPATH=/src/app

WORKDIR /src/app

COPY base.pip ./
RUN pip install --no-cache-dir -r base.pip
RUN pip install --no-cache-dir flit

COPY . .
RUN flit install

RUN apt-get update -q && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

CMD ["flask", "--app", "ads", "run", "--host=0.0.0.0"]
