
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.widgets import TextArea
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import date

from wtforms.ext.sqlalchemy.fields import QuerySelectField


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = 'thisisupposedtobesecret!'

Bootstrap(app)
db = SQLAlchemy(app) # obj de acesso ao
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
admin= Admin(app, template_mode="Bootstrap3")

class Usuario(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	nome = db.Column(db.String(50))
	email = db.Column(db.String(50), unique= True)
	senha = db.Column(db.String(50), unique= True)

class Tipodispositivo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	descricao = db.Column(db.String(200))
	tipodeDado =  db.Column(db.String(200))

class Dadosdisp(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	dispositivo_id = db.Column(db.Integer, db.ForeignKey('dispositivo.id'))
	data = db.Column(db.String(80))
	status = db.Column(db.Boolean)
	dados = db.Column(db.Integer)

class Dispositivo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tipoDispositivo_id = db.Column(db.Integer, db.ForeignKey('tipodispositivo.id'))
	name = db.Column(db.String(50))
	ip = db.Column(db.String(50))
	url = db.Column(db.String(50))
	usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))


#########################################################

class DispositivoView(ModelView):
	form_columns = ['usuario_id','tipoDispositivo_id','name','ip','url']

class DispositivosView(BaseView):
	@expose('/')
	def index(self):
		dispositivo = Dispositivo.query.all()
		return self.render('admin/todosdispositivos.html', dispositivo=dispositivo)

#########################################################
admin.add_view(ModelView(Usuario, db.session)) 
admin.add_view(ModelView(Tipodispositivo, db.session)) 
admin.add_view(DispositivoView(Dispositivo, db.session)) 
admin.add_view(DispositivosView(name='todosdispositivos', endpoint='todosdispositivos'))

@login_manager.user_loader
def load_user(user_id):
	return Usuario.query.get(int(user_id))

class LoginForm(FlaskForm):
	nome = StringField('Nome', validators=[InputRequired(), Length(min=4, max =15)])
	senha = PasswordField('Senha', validators=[InputRequired(), Length(min=8, max =80)])
	remember = BooleanField('remember me')


@app.route('/')
def index():
	
	return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		usuario = Usuario.query.filter_by(nome=form.nome.data).first()
		if usuario:		#compara o hash do banco com a transformacao da senha passa em hash
			#if check_password(usuario.senha, form.senha.data):
			if usuario.senha == form.senha.data:
				login_user(usuario, remember=form.remember.data)
				return redirect(url_for('dashboard'))

		return '<h2> Invalid username or password </h1>'
		#return '<h1>' + form.username.data + ' ' +form.password.data + '</h1>' 


	return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required #para nao poder acessar diretamente
def dashboard():
	idusuario = current_user.id
	dispositivo = Dispositivo.query.filter_by(usuario_id=idusuario)
	return render_template('dashboard.html', name = current_user.nome, dispositivo=dispositivo)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/dispositivoCompleto/<int:id>', methods=['GET','POST'])
def abrirTexto(id):

	#texto = Texto.query.filter_by(id=id).first()
	dispositivo = Dispositivo.query.get(id)
	

	nome=dispositivo.name
	id= dispositivo.id
	
	
	
	return render_template('dispositivoCompleto.html', nome=nome, id=id )



if __name__ == '__main__':
	app.run(debug=True)