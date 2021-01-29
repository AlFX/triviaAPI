import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.db_name = "trivia_test"
        self.username = "postgres"
        self.password = "postgres"
        self.host = "localhost"
        self.port = "5432"
        self.database_path = \
            f"postgres://{self.username}:{self.password}@{self.host}:{self.port}/{self.db_name}"

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # question for test_add_delete_question()
        self.test_question = {
            "question": "Conan! What is best in life?",
            "answer": "To crush your enemies -- See them driven before you and to hear the lamentation of their women!",
            "category": "4",
            "difficulty": 5
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    # DONE Write at least one test for each test for successful operation and
    # for expected errors.
    def test_retrieve_categories(self):
        """Check that all categories are retrieved"""
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)

    def test_retrieve_questions(self):
        """Check that all questions are retrieved and paginated."""
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['questions'][0]['id'], 5)

    def test_questions_pagination(self):
        """Load page 2 from a complete set of paginated questions and
        check."""
        res = self.client().get('/api/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(len(data['questions']), 9)
        self.assertEqual(data['questions'][0]['id'], 15)

    def test_page_404(self):
        """Make sure a 404 error is returned when a non-existing page
        is requested"""
        res = self.client().get('/api/questions?page=666')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['error'], 404)

    def test_add_delete_question(self):
        """Starting from the default test database, create a test question
        then check for nominal deleting behavior"""

        # Create
        test_question = Question(
            question=self.test_question['question'],
            answer=self.test_question['answer'],
            category=self.test_question['category'],
            difficulty=self.test_question['difficulty']
        )
        test_question.insert()
        test_question_id = test_question.id

        # Test addition
        all_questions = Question.query.all()
        self.assertEqual(len(all_questions), 20)  # started as 19

        # Delete
        res = self.client().delete(f'/api/questions/{test_question_id}')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], test_question_id)

    def test_delete_question_404(self):
        """Delete a non-existing question and get a 404 error code"""
        res = self.client().delete("/api/questions/666")
        data = json.loads(res.data)

        self.assertEqual(data['error'], 404)

    def test_question_search(self):
        """Make sure that the search tool strips whitespace and is
        case-insensitive"""
        res = self.client().post('/api/questions',
                                 json={"searchTerm": "  CaSSiuS   "})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['id'], 9)

    def test_retrieve_questions_by_category(self):
        """Test GET request for questions by category: Science"""
        res = self.client().get('/api/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 3)

        # Get questions non-existent category
        res = self.client().get('/api/categories/666/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)

    def test_post_empty_question(self):
        """POST a new empty question"""
        empty_question = {
            "question": "          ",
            "answer": "           ",
            "category": "6",
            "difficulty": 1
        }
        res = self.client().post('/api/questions', json=empty_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)

    def test_post_new_question(self):
        """POST a new question, ensure it gets added to the last page"""

        original_questions = len(Question.query.all())
        self.assertEqual(original_questions, 19)

        # POST
        res = self.client().post('/api/questions', json=self.test_question)
        data = json.loads(res.data)
        new_id = data['added']

        self.assertEqual(data['success'], True)

        new_questions = len(Question.query.all())
        self.assertEqual(new_questions, original_questions + 1)

        res = self.client().delete(f'/api/questions/{new_id}')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_id)

    def test_play_quiz_all_left(self):
        """Test playing when all Science questions are left"""
        res = self.client().post(
            '/api/quizzes',
            json={"previous_questions": [],
                  "quiz_category": {"type": "Science", "id": "1"}})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['question'])
        self.assertEqual(data['question']['category'], 1)

    def test_play_quiz_one_left(self):
        """Test playing when 1/3 Science questions are left"""
        res = self.client().post(
            '/api/quizzes',
            json={"previous_questions": [21, 22],
                  "quiz_category": {"type": "Science", "id": "1"}})
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['id'], 20)


if __name__ == "__main__":
    unittest.main()
