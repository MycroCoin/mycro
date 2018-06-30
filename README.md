Mycro: A Platform for Open-Source Consumer Application

# Django backend
I'm not 100% sure how to get started. I followed http://docs.graphene-python.org/projects/django/en/latest/tutorial-plain/

I think the only commands you need to do are:

```python
$ python manage.py migrate
$ python ./manage.py loaddata projects
$ python ./manage.py runserver
```

Then visit `localhost:8000/graphql` and enter the following as your query to
see if it works:

```
query {
  allProjects {
    name,
    id
  }
}
```

You should see

```
{
  "data": {
    "allProjects": [
      {
        "name": "paymahn",
        "id": "1"
      },
      {
        "name": "aaron",
        "id": "2"
      },
      {
        "name": "kyle",
        "id": "3"
      }
    ]
  }
}
```
