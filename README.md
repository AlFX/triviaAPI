
UdaciTrivia API documentation
=============================

These API rely on calls made with the `GET`, `POST` and `DELETE` methods. On top of that, **no API key is required.**


### CORS and Same-Origin Policy

The backend and the frontend access different ports even on the same host therefore they don't respect the Same-Origin Policy. In order to enforce it, while preserving the application functionality, CORS is enabled on all the routes, except the `/api/` routes.


### Responses and error codes

All responses are returned in JSON format containing at least a boolean `"success"` key.

By the same token, error codes are returned in JSON format as follows:
```json
{
    "success": false,
    "error": 404,
    "message": "Not found"
}
```
At the moment, the supported error codes are 400, 404, 422, and 500.


### API Objects

The UdaciTrivia API comes in two types:

- **Categories** sorting the questions, i.e.: Science, Art, Geography, History, Entertainment, and Sports
- **Questions** which contain the question text itself, its category, the difficulty (from 1 to 5) and an answer.


#### GET `api/categories`

Returns an object with a single key, `categories`, that contains another dictionary object `id` as keys and `category_string` as values

Example: **`curl http://localhost:5000/api/categories`**

```json
{
    "categories": {
        "1" : "Science",
        "2" : "Art",
        "3" : "Geography",
        "4" : "History",
        "5" : "Entertainment",
        "6" : "Sports"
    },
    "success": true
}
```


#### GET `api/questions`

Returns:
- a list of all categories
- a list of questions across all categories, paginated to limit 10 results per page with key value pairs, success status, and total number of questions in database

the URL parameter `?page=<num>` selects the page to return and defaults to page 1

Example: **`curl http://localhost:5000/api/questions?page=2`**

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null,
  "questions": [
    {
      "answer": "Jackson Pollock",
      "category": 2,
      "difficulty": 2,
      "id": 19,
      "question": "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
    },

    ...

    {
      "answer": "Scarab",
      "category": 4,
      "difficulty": 4,
      "id": 23,
      "question": "Which dung beetle was worshipped by the ancient Egyptians?"
    },
  ],
  "success": true,
  "total_questions": 16
}

```


#### DELETE `/api/questions/<question_id>`

- Deletes a question by id
- Request Arguments: question id
- Returns: Success status and id of deleted question if successful

Example: **`curl -X DELETE http://localhost:5000/api/questions/4`**

```json
{
    "deleted": 4,
    "success": true
}
```


#### POST `/api/questions`

This endpoint serves the following purposes:

1. Creating a new question through a form
1. Searching through questions via a search form


###### Creating a new question through a form

- Request Arguments: question data via application
- Returns: Success status and id of newly created question if successful

Example **`curl -X POST http://localhost:5000/api/questions -H "Content-Type: application/json" -d '{"question": "Conan! What is best in life?", "answer": "To crush your enemies -- See them driven before you and to hear the lamentation of their women!", "category": "4", "difficulty": 5}'`**
```json
{
  "added": 26,
  "success": true
}
```


###### Searching through questions via a search form

- Request Arguments: search term data via application/json type
- Returns: Success status and a list of questions and their data that met the search results

Example **`curl -X POST http://localhost:5000/api/questions -H "Content-Type: application/json" -d '{"searchTerm": "Conan"}'`**

```json
{
  "questions": [
    {
      "answer": "To crush your enemies -- See them driven before you and to hear the lamentation of their women!",
      "category": 4,
      "difficulty": 5,
      "id": 26,
      "question": "Conan! What is best in life?"
    }
  ],
  "success": true
}
```


#### GET `/api/categories/<category_id>/questions`

Considering a single category, retrieve all the questions.
- Request Arguments: category_id
- Returns: Success status and list of questions for that category, plus a total question count of the non-paginated results

Example **`curl http://localhost:5000/api/categories/3/questions`**

```json
{
  "categories": {
    "id": 3,
    "type": "Geography"
  },
  "current_category": 3,
  "questions": [
    {
      "answer": "Lake Victoria",
      "category": "3",
      "difficulty": 2,
      "id": 13,
      "question": "What is the largest lake in Africa?"
    },
    {
      "answer": "The Palace of Versailles",
      "category": "3",
      "difficulty": 3,
      "id": 14,
      "question": "In which royal palace would you find the Hall of Mirrors?"
    },
    {
      "answer": "Agra",
      "category": "3",
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```


#### POST `/api/quizzes`

Enables the playing of a Trivia game
- Returns a random question for a given category that has not been already asked
- Can return questions randomly chosen from a particular category, or across all of them
- Request Arguments: quiz category and a list of previously asked questions (client app must keep track of this), encoded in `application/json` format
- Returns: `success` status and if successful, a random question. If there are no more questions to return in that category, the API just returns success but with no question key/value pair, which tells the frontend the quiz is over.

Example: get a question from all categories (category 0), and none have been asked yet
**`curl -X POST http://localhost:5000/api/quizzes -H "Content-Type: application/json" -d '{previous_questions: [], quiz_category: {type: "click", id: 0}}'`**

```json
{
  "question": {
    "answer": "Uruguay",
    "category": "6",
    "difficulty": 4,
    "id": 11,
    "question": "Which country won the first ever soccer World Cup in 1930?"
  },
  "success": true
}
```

Example: get a question from the History category (category 4), and there are no more questions left in that category
**`curl -X POST http://localhost:5000/api/quizzes -H "Content-Type: application/json" -d '{previous_questions: [5, 9, 23, 12], quiz_category: {type: "History", id: "4"}}'`**

```json
{
  "success": true
}
```
