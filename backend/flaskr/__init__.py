import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    """Return a paginated list of question objects"""
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [x.format() for x in selection]
    return questions[start:end]


def format_categories():
    categories = Category.query.all()
    return {category.id: category.type for category in categories}


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # DONE: Set up CORS. Allow '*' for origins. Delete the sample route
    # after completing the TODOs
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # DONE: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Headers",
                             "GET, PATCH, POST, DELETE, OPTIONS")
        return response

    # DONE: Create an endpoint to handle GET requests for all available
    # categories.
    @app.route("/api/categories", methods=["GET"])
    def retrieve_categories():
        try:
            return jsonify({
                "success": True,
                "categories": format_categories(),
            })
        except Exception:
            abort(500)

    # DONE: Create an endpoint to handle GET requests for questions,
    # including pagination (every 10 questions).
    # This endpoint should return a list of questions,
    # number of total questions, current category, categories.
    # TEST: curl localhost:5000/questions
    @app.route("/api/questions", methods=["GET"])
    def retrieve_questions():
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)
        if not current_questions:
            abort(404)
        return jsonify({
            "success": True,
            "questions": current_questions,
            "total_questions": len(selection),
            "categories": format_categories(),
            "current_category": None
        })

    # TEST: At this point, when you start the application
    # you should see questions and categories generated,
    # ten questions per page and pagination at the bottom of the screen
    # for three pages.
    # Clicking on the page numbers should update the questions.

    # DEBUG route
    # TEST: curl localhost:5000/questions/4 -X GET
    @app.route("/api/questions/<int:question_id>", methods=["GET"])
    def retrieve_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if not question:
                abort(404)
            return jsonify({
                "success": True,
                "questions": question.format(),
                "current_category": None
            })
        except Exception:
            abort(422)

    # DONE: Create an endpoint to DELETE question using a question ID.
    # TEST: curl localhost:5000/questions/5 -X DELETE
    @app.route("/api/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if not question:
                abort(404)
            question.delete()
            selection = Question.query.all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                "success": True,
                "questions": current_questions,
                "total_questions": len(selection),
                "categories": format_categories(),
                "current_category": None,
                "deleted": question_id
            })
        except Exception:
            abort(404)

    # TEST: When you click the trash icon next to a question, the question will
    # be removed.
    # This removal will persist in the database and when you refresh the page.

    # DONE: Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.
    # DONE: Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.
    @app.route("/api/questions", methods=["POST"])
    def add_question():
        form_data = request.json
        if "searchTerm" in form_data:
            search_term = form_data["searchTerm"].strip()
            questions = Question.query.filter(Question.question.
                                              ilike(f"%{search_term}%")).all()
            current_questions = [q.format() for q in questions]
            return jsonify({
                "success": True,
                "questions": current_questions
            })
        else:
            if (form_data['question'].strip() == "") or (form_data["answer"].strip() == ""):
                abort(400)
            try:
                new_question = Question(question=form_data['question'].strip(),
                                        answer=form_data['answer'].strip(),
                                        category=form_data['category'],
                                        difficulty=form_data['difficulty'])
                new_question.insert()
            except Exception:
                abort(422)

            return jsonify({
                "success": True,
                "added": new_question.id
            })

    # TEST: When you submit a question on the "Add" tab,
    # the form will clear and the question will appear at the end of the last
    # page of the questions list in the "List" tab.
    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.

    # TODO: Create a GET endpoint to get questions based on category.
    @app.route('/api/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        questions = Question.query.filter_by(category=str(category_id)).all()
        current_questions = paginate_questions(request, questions)
        if not current_questions:
            abort(404)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': Category.query.get(category_id).format(),
            'current_category': category_id
        })
    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.

    # DONE: Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.
    @app.route('/api/quizzes', methods=['POST'])
    def play():
        request_data = request.json
        try:
            request_cat = request_data['quiz_category']['id']
        except Exception:
            abort(400)
        if request_cat == 0:
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=str(request_cat)).all()
        questions = [x.format() for x in questions]
        # Remove questions that have been already asked
        try:
            previous_questions = request_data['previous_questions']
        except Exception:
            abort(400)
        fresh_questions = []
        for question in questions:
            if question['id'] not in previous_questions:
                fresh_questions.append(question)
        # Make sure not all the questions were asked
        # If so, return nothing to tell the frontend that the game is over
        if not fresh_questions:
            return jsonify({
                'success': True
            })
        question = random.choice(fresh_questions)
        return jsonify({
            'success': True,
            'question': question
        })
    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.

    # DONE: Create error handlers for all expected errors
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        })

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        })

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        })

    return app
