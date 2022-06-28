import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={"/": {"origins": "*"}})

    

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(res):
        res.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        res.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONs')
        return res

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        data = Category.query.all()
        categories = {}
        for category in data:
            categories[category.id] = category.type

        if len(data) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        getQuestions= Question.query.all()
        total = len(getQuestions)
        question = paginate_questions(request, getQuestions)

        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        if (len(question) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': question,
            'total_questions': total,
            'categories': categories_dict
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['GET', 'DELETE'])
    def delete_question(id):
        try:
            question = Question.query.get(id)

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': id        
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():

        data = request.get_json()

        new_question = data['question']
        input_answer = data['answer']
        input_category = data['category']
        input_difficulty = data['difficulty']

        if (len(new_question)==0) or (len(input_answer)==0) or (len(input_category)==0) or (len(input_difficulty)==0):
            abort(422)

        newQuestion = Question(
                question = new_question,
                answer = input_answer,
                category=input_category,
                difficulty=input_difficulty
            )

        newQuestion.insert()
    
        getQuestion = Question.query.all()
        questions = paginate_questions(request, getQuestion)

        return jsonify({
            'success': True,
            'created': newQuestion.id,
            'questions': questions,
            'total_questions': len(getQuestion)
        })


    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['GET','POST'])
    def search_questions():
       
        data = request.get_json()

        if(data['searchTerm']):
            searchField = data['searchTerm']
    
        questions = Question.query.filter(Question.question.ilike('%{}%'.format(searchField))).all()
        
        if questions==[]:
            abort(404)

        result = paginate_questions(request, questions)

        return jsonify({
            'success': True,
            'questions': result,
            'total_questions': len(questions)
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_question_by_category(id):
        getCategory = Category.query.get(id)
        if (getCategory is None):
            abort(404)

        try:
            questions = Question.query.filter_by(category=getCategory.id).all()
        
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'current_category': getCategory.type,
                'total_questions': len(questions)
            })

        except:
            abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_a_quiz_question():
        
        quizData = request.get_json()
        quizCategory = quizData['quiz_category']
        lastQuestions = quizData['previous_questions']

        
        if quizCategory['id'] != 0:
            quizQuestions = Question.query.filter_by(category=quizCategory['id']).all()
        
        else:
            quizQuestions = Question.query.all()

        def get_random_question():
            nextQuestion = random.choice(quizQuestions).format()
            return nextQuestion

        randomQuestion = get_random_question()

        loaded = False
        if randomQuestion['id'] in lastQuestions:
            loaded = True

        while loaded:
            randomQuestion = random.choice(quizQuestions).format()

        if (len(lastQuestions) == len(quizQuestions)):
            return jsonify({
                'success': True,
                'message': "game over"
                }), 200

        return jsonify({
            'success': True,
            'question': randomQuestion
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request error, Please try again '
            })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'File Not found.'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422, 
            'message': 'unprocessable. structure error.'
        }), 422

    @app.errorhandler(500)
    def server(error):
        return jsonify({
            'success': False,
            'error': 500, 
            'message': 'Please bear with us, Fault not from you'
        }), 500

    return app


 
