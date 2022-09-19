# Flask API

A simple API for getting recipes.

## Run the code

First create and activate your virtualenv - with the `venv` package on OSX or Linux, this will be:

```bash
python3 -m venv venv
source venv/bin/activate
```

With your virtualenv active, install the project locally:

```bash
pip install -e .
```

Set mongo atlas cloud db uri as an environment variable for flask to use.

```bash
export MONGO_URI="export MONGO_URI="mongodb+srv://admin:<password>@cocktails.c7qomug.mongodb.net/cocktails?retryWrites=true&w=majority""
```

Importing data from recipes.json for testing:

```bash
mongoimport --uri "$MONGO_URI" --file ../data/recipes.json
```

And now you should be able to run the service like this or use makefile "make run":

```bash
FLASK_APP=cocktailapi flask run
```

## Developing

Run the following to install the project (and dev dependencies) into your active virtualenv:

```bash
pip install -e .[dev]
```

You can run the tests with:

```bash
pytest
```
