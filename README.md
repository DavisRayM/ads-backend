# Automated Diagnosis System(ADS) Backend

This repository contains backend code for the ADS Project presented during
the ACM Project showcase.

## Technologies

- Python (Programming Language): Specifically using the Flask framework
- Docker: Containerized environment for developer testing and deployments
- Github workflows: Automated Continous testing

## Setting up a development environment

1. Clone repository to a local directory

```sh
git clone https://github.com/DavisRayM/ads-backend.git
```

2. Setup a virtual environment. More info [here](https://docs.python.org/3/library/venv.html#creating-virtual-environments)

3. Install [flit](https://pypi.org/project/flit/) via [pip](https://pip.pypa.io/en/stable/installation/)

```sh
pip install flit
```

4. Install required packages; _items within `{}` are options pick one of them i.e `--deps production`_:

```sh
flit install --only-deps --deps {'all', 'production', 'develop'}
```

5. Check that the server is running and tests pass

```sh
flask --app ads run
./scripts/run-tests.sh
```
