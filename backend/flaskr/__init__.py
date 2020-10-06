import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={r"*": {"origins":"*"}})
  
  '''
  @: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @: Use the after_request decorator to set Access-Control-Allow
  '''
  #@app.route('/')
  #def handle():
    #selection = Category.query.order_by(categories.id).all()
    #current_categories = paginate_categories(request, selection)
  @app.route('/categories', methods=['GET'])
  def retrive_categories():
    categories = Category.query.order_by(Category.type).all()

    if len(categories) == 0:
        abort(404)

    return jsonify ({
      'success': True,
      'categories' : {category.id : category.type for category in categories},
    })
  '''
  @: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/questions')  
  def retrieve_questions():
    
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = Category.query.order_by(Category.type).all()
    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'categories': {category.id: category.type for category in categories},
      'current category': None
    })

  '''
  @: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(422)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'deleted': book_id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    difficulty = body.get('difficulty', None)
    search = body.get('search', None)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=difficulty)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True,
        'answer': answer,
        'category': category,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      }) 
    except:
        abort(400)
  '''
  @: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()

    search_term = body.get('search_term', None)

    try:
      selection = Question.query.order_by(Question_id).filter(Question.title.ilike('%{}%'.format(search_term)))
      current_questions = paginate_questions(request, selection)
    except:
      return jsonify({
        'success': True,
        #'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all()),
        'current_category': None
      })


  @app.route('/categories/<int:category_id>/questions')
  def category_question(category_id):
    category_id = str(category_id)
    selection = Question.query.filter(Question.category == category_id).all()
    current_questions = paginate_questions(request, selection)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(Question.query.all()),
      'current_category': category_id
    })


  
  @app.route('/quizzes', methods=['POST'])
  def take_quizes():
    body = request.get_json()
    if not body:
        abort(400)
    previous_q = body['previous_questions']
    category_id = body['quiz_category']['id']
    if category_id == 0:
      if previous_q is not None:
        questions = Question.query.filter(Question.id.notin_(previous_q)).all()
      else:
        questions = Question.query.all()
    else:
      if previous_q is not None:
        questions = Question.query.filter(Question.id.notin_(previous_q),
        Question.category == category_id).all()
      else:
        questions = Question.query.filter(Question.category == category_id).all()
    if not next_question:
      abort(404)
    if next_question is None:
      next_question = False
    next_question = random.choice(questions).format()
    return jsonify({
        'success': True,
        'question': next_question
    })

 # '''
 # @: 
 # Create a POST endpoint to get questions to play the quiz. 
 
 # This endpoint should take category and previous question parameters 
  
  #and return a random questions within the given category, 
  #if provided, and that is not one of the previous questions. 

 # TEST: In the "Play" tab, after a user selects "All" or a category,
  #one question at a time is displayed, the user is allowed to answer
  #and shown whether they were correct or not. 
 # '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "bad request"
      }), 400
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
      }), 404
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
      }), 422
  #'''
 # @: 
 # Create error handlers for all expected errors 
 # including 404 and 422. 
 # '''
  
  return app

    
