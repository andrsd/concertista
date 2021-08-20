# Notes For Developers

## Developing

Clone the repository and install `concertista` and its dependencies:

```
git clone https://github.com/andrsd/concertista.git
cd concertista
pip install -e .
```

Install additional development requirements:

```
pip install -r requirements/dev.txt
```

Setup connection to spotify:

```
TODO
```

Run unit tests with:

```
pytest .
```

Run code checks with:

```
flake8 .
```

Run unit tests with coverage report:

```
coverage run --source=concertista -m pytest
coverage html
```

Open `htmlcov/index.html`

## Building the app

```
pyinstaller Concertista.spec
```

This will create a distributable in `dist` directory.
