from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# إعداد التطبيق و قاعدة البيانات
app = Flask(__name__)

# استخدام متغير البيئة لتحديد URI لقاعدة البيانات PostgreSQL من Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إضافة مفتاح سري لتأمين الجلسات
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_default_secret_key')

# إعداد قاعدة البيانات
db = SQLAlchemy(app)

# نموذج المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# إنشاء الجداول في قاعدة البيانات (إذا لم تكن موجودة)
with app.app_context():
    db.create_all()

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # البحث عن المستخدم في قاعدة البيانات
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):  # التحقق من كلمة المرور باستخدام check_password_hash
            session['user_id'] = user.id  # تخزين ID المستخدم في الجلسة
            return redirect(url_for('services'))  # إعادة التوجيه إلى صفحة الخدمات
        else:
            flash('حسابك غير موجود أو كلمة المرور خاطئة', 'danger')

    return render_template('login.html')

# صفحة التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # التحقق إذا كان المستخدم موجودًا بالفعل
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('البريد الإلكتروني موجود بالفعل', 'danger')
            return redirect(url_for('register'))

        # تشفير كلمة المرور
        password_hash = generate_password_hash(password)

        new_user = User(username=username, email=email, password=password_hash)

        # إضافة المستخدم إلى قاعدة البيانات
        db.session.add(new_user)
        db.session.commit()

        flash('تم التسجيل بنجاح، يمكنك تسجيل الدخول الآن', 'success')
        return redirect(url_for('login'))  # إعادة التوجيه إلى صفحة تسجيل الدخول بعد التسجيل الناجح

    return render_template('register.html')

# صفحة الخدمات (تظهر فقط للمستخدمين المسجلين)
@app.route('/services')
def services():
    if 'user_id' not in session:
        flash('من فضلك قم بتسجيل الدخول أولاً', 'warning')
        return redirect(url_for('login'))  # إعادة التوجيه إلى صفحة تسجيل الدخول إذا لم يكن المستخدم مسجل دخول

    return render_template('services.html')

if __name__ == '__main__':
    app.run(debug=True)
