import os
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = 'postgres://{}:{}@{}/{}'.format('postgres', 'password', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_getCategories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
    
    def test_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_invalid_page(self):
        res = self.client().get('/questions?page=10000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_delete_questions(self):
        res = self.client().delete('questions/62')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 62)


    def search_question(self):
        response = self.client().post('questions/search', json={"searchTerm": "van"})
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])


    def tes_invalid_search(self):
        response = self.client().post('questions/search', json={"searchTerm": ""})
        data = json.loads(response.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(response.status_code, 422)


    def test_create_question(self):
        new_question = {
        'question': 'what is a chair used for ',
        'answer': 'sitting',
        'category': '1',
        'difficulty': 1,
        }

        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)

       
    
    def test_422_cannot_create_question(self):
        empty_question = {
        'question': '',
        'category': '2',
        'answer':'7',
        'difficulty': 1,
        }

        res = self.client().post('/questions', json=empty_question)
        data = json.loads(res.data)

        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 422)


    def test_play_quiz(self):
        input_data = {
            'previous_questions':['27', '30', '26'],
            'quiz_category': {
                'id': 6,
                'type': 'Sports'
            }
        }

        res = self.client().post('/quizzes', json=input_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertEqual(data['question']['id'], 67)
        self.assertEqual(data['question']['category'], 6)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()