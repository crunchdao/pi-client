# π Client

A client for the Pi project.

- [π Client](#π-client)
- [Install](#install)
- [Usage](#usage)
  - [Endpoints](#endpoints)
    - [Get Current User](#get-current-user)
    - [List Datasources](#list-datasources)
    - [Create a Question](#create-a-question)
    - [List Questions](#list-questions)
    - [Get Question (by ID)](#get-question-by-id)
    - [Get a Question's Timeseries](#get-a-questions-timeseries)
  - [Handling Errors](#handling-errors)

# Install

```bash
pip install git+https://github.com/crunchdao/pi-client.git#egg_name=pi
```

# Usage

```python
import pi

# will read api key from CRUNCHDAO_PI_API_KEY
client = pi.api.Client()

# test if it is working
print(client.get_current_user())
```

> [!NOTE]
> [A notebook is available!](./examples/notebook.ipynb)

## Endpoints

### Get Current User

```python
from pi.api import CurrentUser

current_user: CurrentUser = client.get_current_user()
```

### List Datasources

```python
from pi.api import Datasource

datasources: List[Datasource] = client.list_datasources()
```

### Create a Question

```python
from pi.api import Question

prompt = "How Apple is doing?"
question: Question = client.create_question(prompt)

# specify a datasource
client.create_question(
    prompt,
    datasource_name="FOMC"
)

# wait until a question processing finished
client.create_question(
    prompt,
    wait=True
)
```

### List Questions

```python
from pi.api import Question

questions: List[Question] = client.list_questions(
    only_successful=True,
    user_id=1,
)

# get a dataframe instead
questions: DataFrame = client.list_questions(
    as_dataframe=True
)
```

### Get Question (by ID)

```python
from pi.api import Question

question: Question = client.get_question_by_id(123)
```

### Get a Question's Timeseries

```python
from pi.api import Timeseries

timeseriess: List[Timeseries] = client.list_question_timeseries(123)
```

## Handling Errors

Most API errors have an equivalent Python error class.

```python
try:
    client.get_question(123456789)
except pi.api.QuestionNotFoundError:
    print("question not found")
```
