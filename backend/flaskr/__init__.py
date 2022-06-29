import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


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
        categoryData = Category.query.all()
        categories = {}
        for category in categoryData:
            categories[category.id] = category.type
        

        if len(categoryData) == 0:
            abort(404)
        
        else:
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
        page = request.args.get('page' ,1 , type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        getQuestions= Question.query.all()
        questions =  [question.format() for question in getQuestions]
        paginatedQuestions = questions[start:end]

        categoryData = Category.query.all()
        categories = {}
        for category in categoryData:
            categories[category.id] = category.type

        if len(getQuestions) == 0:
            abort(404)

        else:
            return jsonify({
                'success': True,
                'totalQuestions': len(getQuestions),
                'questions': paginatedQuestions,
                'categories': categories
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        getQuestion = Question.query.filter(Question.id==id).one_or_none()

        if getQuestion is None:
                abort(404)

        else: 
            getQuestion.delete()

            return jsonify({
               'success': True,
               'deleted': getQuestion    
            })
        
            
       
        
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

        getDaTa = request.get_json()

        new_question = getDaTa['question']
        input_answer = getDaTa['answer']
        input_category = getDaTa['category']
        input_difficulty = getDaTa['difficulty']

        if (len(new_question)==0) or (len(input_answer)==0) :
            abort(422)

        else:
            newQuestion = Question(
                    question = new_question,
                    answer = input_answer,
                    category=input_category,
                    difficulty=input_difficulty
                )

            newQuestion.insert()
        
            getQuestion = Question.query.all()
            page = request.args.get('page' ,1 , type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = getQuestion[start:end]

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
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
       
        getData = request.get_json()

        if(getData['searchTerm']):
            searchField = getData['searchTerm']
        
    
            getQuestions = Question.query.filter(Question.question.ilike('%{}%'.format(searchField))).all()
            questions =  [question.format() for question in getQuestions]

            if questions==[]:
                abort(404)

            else:
                page = request.args.get('page' ,1 , type=int)
                start = (page - 1) * QUESTIONS_PER_PAGE
                end = start + QUESTIONS_PER_PAGE
                result = questions[start:end]

                return jsonify({
                    'success': True,
                    'questions': result,
                    'total_questions': len(questions)
                })
        else:
            abort(422)
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

        else:
            getQuestions = Question.query.filter_by(category=getCategory.id).all()
            questions = [question.format() for question in getQuestions]
            
            page = request.args.get('page' ,1 , type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            result = questions[start:end]

            return jsonify({
                'success': True,
                'questions': result,
                'current_category': getCategory.type,
                'total_questions': len(questions)
            })

       

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
        lastQuestion = quizData['previous_questions']     

        if quizCategory['id'] != 0:
            quizQuestions = Question.query.filter_by(category=quizCategory['id']).all()
        
        else:
            quizQuestions = Question.query.all()

        if (len(lastQuestion) != len(quizQuestions)): 
            randomQuestion = random.choice(quizQuestions)
            question = randomQuestion.format()
            if question['id'] not in lastQuestion:
                return jsonify({
                    'success': True,
                    'question': question
                })

        else:
            return jsonify({
                'success': True,
                'message': "Quiz over"
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


 

