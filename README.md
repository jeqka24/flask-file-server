## About

This is a sample project, showing how to implement remote file processing

Following requirements met:
 * store only encoded files with a UUID name
 * file names are stored in database
 * a user can see files that was uploaded only by user
 * users are authentificated via `api-key` token in request (header or parameter)

## Installation

1. Create a virtual environment (venv):
```shell
python -m venv safeweb
```

2. Activate venv (see https://docs.python.org/3/library/venv.html#creating-virtual-environments):

Windows:
```shell
safeweb\Scripts\activate.bat
```

POSIX:
```shell
safeweb/bin/activate
```

3. Install dependencies
```shell
cd safeweb
python -m pip install -r requirements.txt
```

## Running
Required two different consoles:

1. Start task runner:
```shell
python taskrunner.py tasks.huey -w2
```

2. Run a web-interface:
```shell
python app.py
```

...or a single liner:
```shell
python taskrunner.py tasks.huey -w2 && python app.py
```
