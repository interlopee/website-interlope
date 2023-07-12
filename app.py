from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired
from flask_bootstrap import Bootstrap
from functools import wraps
import pdfkit
from PIL import Image
import base64

app = Flask(__name__, template_folder='template')

app.config['SECRET_KEY'] = 'Bismillah23'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cpses_inxywsck83@localhost/interlope'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
bootstrap = Bootstrap(app)



class Login(FlaskForm):
    username = StringField('', validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Username'})
    password = PasswordField('', validators=[InputRequired()], render_kw={'autofocus':True, 'placeholder':'Password'})
    level = SelectField('level', validators=[InputRequired()], choices=[('Admin','Admin'), ('Administrasi','Administrasi')])

class User(db.Model):
    __tabelname__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.Text)
    level = db.Column(db.String(100))
    db.relationship('Pasien', backref=db.backref('user', lazy=True))

    def __init__(self,username,password,level):
        self.username = username
        if password != '':
            self.password = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.level = level

class Pasien(db.Model):
    __tabelname__ = 'Pasien'
    id = db.Column(db.BigInteger, primary_key=True)
    nama = db.Column(db.String(150))
    umur = db.Column(db.String(100))
    jk = db.Column(db.String(100))
    no_hp = db.Column(db.String(100))
    alamat = db.Column(db.Text)
    keterangan = db.Column(db.String(100))
    hasil_pemeriksaan = db.Column(db.BLOB)
    hasil_label = db.Column(db.Text)


def __init__(self,nama,umur,jk,no_hp,alamat,keterangan,hasil_pemeriksaan,hasil_label):
    self.nama = nama
    self.umur = umur
    self.jk = jk
    self.no_hp = no_hp
    self.alamat = alamat
    self.keterangan = keterangan
    self.hasil_pemeriksaan = hasil_pemeriksaan
    self.hasil_label = hasil_label
    
app.app_context().push()
db.create_all()

@app.route('/')
def Home():
    return render_template('Home.html')

@app.route('/tambahdaftar', methods=['GET','POST'])
def tambahdaftar():
    if request.method == "POST":
        nama = request.form['nama']
        umur = request.form['umur']
        jk = request.form['jk']
        no_hp = request.form['no_hp']
        alamat = request.form['alamat']
        keterangan = request.form['keterangan']
        pasien = Pasien(nama=nama, umur=umur, jk=jk, no_hp=no_hp, alamat=alamat, keterangan=keterangan)
        db.session.add(pasien)
        db.session.commit()
        return jsonify({'success':True})

@app.route('/Klasifikasi Mata')
def klasifikasi():
    return render_template('Klasifikasi.html')
    
@app.route('/Login', methods=['GET','POST'])
def login():
    if session.get('login') == True:
        return redirect(url_for('Hasil'))
    else:
        form = Login()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user:
                if bcrypt.check_password_hash(user.password, form.password.data) and user.level == form.level.data:
                    session['login'] = True
                    session['id'] = user.id
                    session['level'] = user.level
                    return redirect(url_for('Hasil'))
            pesan = "Username atau Password anda salah"
            return render_template("Login.html", pesan=pesan, form=form)
        return render_template('Login.html', form=form)

def login_dulu(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'login' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@login_dulu
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/Hasil')
@login_dulu
def Hasil():
    datanya = Pasien.query.all()
    return render_template('Hasil.html', datanya=datanya)

@app.route('/cetak_pdf/<id>', methods=['GET','POST'])
@login_dulu
def cetak_pdf(id):
    datanya = Pasien.query.filter_by(id=id).first()
    if request.method == "GET":
        image_data = base64.b64encode(datanya.hasil_pemeriksaan).decode('utf-8')
        html = render_template("pdf.html", datanya=datanya, image_data=image_data)
        config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
        pdf = pdfkit.from_string(html, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=laporan.pdf'
        return response


@app.route('/Tentang Kami')
def About():
    return render_template('About.html')

@app.route('/User')
@login_dulu
def kelola_user():
    data = User.query.all()
    return render_template('User.html', data=data)

@app.route('/tambahuser', methods=['GET','POST'])
@login_dulu
def tambahuser():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        level = request.form['level']
        db.session.add(User(username,password,level))
        db.session.commit()
        return redirect(url_for('kelola_user'))

@app.route('/edituser/<id>', methods=['GET','POST'])
@login_dulu
def edituser(id):
    data = User.query.filter_by(id=id).first()
    if request.method == "POST":
         try:
             data.username = request.form['username']
             if data.password != '':
                 password = bcrypt.generate_password_hash(request.form['password']).decode('UTF-8')
             data.level = request.form['level']
             db.session.add(User(username,password,level))
             db.session.commit()
             return redirect(url_for('kelola_user'))
         except:
             flash("Ada trouble")
             return redirect(request.referrer)

@app.route('/hapususer/<id>', methods=['GET','Post'])
@login_dulu
def hapususer(id):
    data = User.query.filter_by(id=id).first()
    db.session.delete(data)
    db.session.commit()
    return redirect(url_for('kelola_user'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
