#https://www.youtube.com/watch?v=WxGBoY5iNXY
#install sqllite-> https://www.sqlite.org/2017/sqlite-tools-win32-x86-3170000.zip
#for importing databse open python and write- from filename import db
#db.create_all() 

#https://www.youtube.com/watch?v=LUFn-QVcmB8 -> to use domain name in flask

from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import jwt, datetime, uuid #generate random public id
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# token has 3 sections- header, payload and signature.

app = Flask(__name__)

app.config['SCERET_KEY'] = 'myKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Python\\FlaskRestApi\\FlaskApiAndSQL\\todo.db'
app.config['SERVER_NAME'] = 'localhost:5000'

db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	public_id = db.Column(db.String(50), unique=True)
	name = db.Column(db.String(50))
	password = db.Column(db.String(80))
	admin = db.Column(db.Boolean)
	
class Todo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(50))
	complete = db.Column(db.Boolean)
	user_id = db.Column(db.Integer)
	
def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = None

		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
	
		if not token:
			return jsonify({'message' : 'Token is missing!'}), 401

		try: 
			data = jwt.decode(token, app.config['SECRET_KEY'], verify=False) #verify=false for signature validation
			current_user = User.query.filter_by(public_id=data['public_id']).first()
		except:
			return jsonify({'message' : 'Token is invalid!'}), 401

		return f(current_user, *args, **kwargs)

	return decorated
			
@app.route('/user', methods=['POST'])
def create_user():
	data = request.get_json()
	hashed_password = generate_password_hash(data['password'], method='sha256')
	new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
	db.session.add(new_user)
	db.session.commit()
	return jsonify({'message' : 'New User Created!'})
	
@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
	if not current_user.admin: #check if user is admin or not
		return jsonify({'message' : 'Cannot perform that function!'})
		
	users = User.query.all() 
	output = []	#list
	for user in users:
		user_data = {} #dictionary
		user_data['public_id'] = user.public_id
		user_data['name'] = user.name
		user_data['password'] = user.password
		user_data['admin'] = user.admin
		output.append(user_data)
		
	return jsonify({'users': output})

@app.route('/user/<public_id_local>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id_local):
	if not current_user.admin: #check if user is admin or not
		return jsonify({'message' : 'Cannot perform that function!'})
		
	user = User.query.filter_by(public_id=public_id_local).first()
	if not user:
		return jsonify({'message':'No user found!'})
	else:
		user_data = {} #dictionary
		user_data['public_id'] = user.public_id
		user_data['name'] = user.name
		user_data['password'] = user.password
		user_data['admin'] = user.admin	
	return jsonify({'users': user_data})
				
@app.route('/user/<public_id_local>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id_local):
	if not current_user.admin: #check if user is admin or not
		return jsonify({'message' : 'Cannot perform that function!'})
		
	user = User.query.filter_by(public_id=public_id_local).first()
	if not user:
		return jsonify({'message':'No user found!'})
	
	user.admin = True
	db.session.commit()
	
	return jsonify({'message':'user is promoted'})
	
@app.route('/user/<public_id_local>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id_local):
	if not current_user.admin: #check if user is admin or not
		return jsonify({'message' : 'Cannot perform that function!'})
		
	user = User.query.filter_by(public_id=public_id_local).first()
	if not user:
		return jsonify({'message':'No user found!'})
		
	db.session.delete(user)
	db.session.commit()
	
	return jsonify({'message':'user has been deleted!'})
	
@app.route('/login')
def login():
	auth = request.authorization
	if not auth or not auth.username or not auth.password:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
		
	user = User.query.filter_by(name=auth.username).first()
	
	if not user:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
		
	if check_password_hash(user.password, auth.password):
		token = jwt.encode({'public_id' : user.public_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SCERET_KEY'])
		
		return jsonify({'token' : token.decode('UTF-8')})
		
	return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
	
# Todo----------------------------------------------------------------------------------------------------------

@app.route('/todo', methods=['GET'])
@token_required
def get_all_todos(current_user):
	todos = Todo.query.filter_by(user_id=current_user.id).all()
	#todos = Todo.query.all()
	output = []	#list
	for todo in todos:
		todo_data = {} #dictionary
		todo_data['text'] = todo.text
		todo_data['complete'] = todo.complete
		todo_data['user_id'] = todo.user_id
		output.append(todo_data)
		
	return jsonify({'todo': output})
	
@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def get_one_todo(current_user, todo_id):
	todo = Todo.query.filter_by(id=todo_id).first()
	todo_data = {} #dictionary
	todo_data['text'] = todo.text
	todo_data['complete'] = todo.complete
	todo_data['user_id'] = todo.user_id
	
	return jsonify({'todo': todo_data})
	
@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
	data = request.get_json()
	new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
	db.session.add(new_todo)
	db.session.commit()
	return jsonify({'message' : 'Todo created!'})
	
@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def complete_todo(current_user, todo_id):
	todo = Todo.query.filter_by(id=todo_id).first()
	todo.complete = True
	db.session.commit()	
	return jsonify({'message' : 'Todo completed!'})
	
@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
	todo = Todo.query.filter_by(id=todo_id).first()
	db.session.delete(todo)
	db.session.commit()
	
	return jsonify({'message' : 'Todo Deleted!'})

	
if __name__ == '__main__':
	app.run(debug=True)
