from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps 


#Login Required Decorator for Request Functions
def login_required(f):
    @wraps(f) #wrap original func
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs) 
        else:
            flash("Please login to view this page...","danger") 
            return redirect(url_for("login"))
    return decorated_function




#Class of RegisterForm
class RegisterForm(Form):
    name = StringField("Real Name",validators=[validators.Length(min=4,max=25),validators.DataRequired(message="The field is required!")]) 
    username = StringField("Username",validators=[validators.Length(min=4,max=35)])
    email = StringField("Mail Adress",validators=[validators.Email(message="Please enter a valid email address...")])
    password = PasswordField("Password:",validators=[
        validators.DataRequired(message= "Password does not match..."),
        validators.EqualTo(fieldname= "confirm",message="")
    ])
    confirm = PasswordField("Confirm Password")

#Class of LoginForm
class LoginForm(Form):
    username = StringField("UserName:")
    password = PasswordField("Password:")

#Flask App    
app = Flask(__name__)

#Configuration with MySql
app.secret_key = "ybblog" 
app.config["MYSQL_HOST"]= "localhost" 
app.config["MYSQL_USER"]= "root" 
app.config["MYSQL_PASSWORD"] = "" 
app.config["MYSQL_DB"] = "kbblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"    


#MySql App
mysql = MySQL(app) 

#Register Page
@app.route("/register",methods= ["GET","POST"]) 
def register():
    form = RegisterForm(request.form) 
    if request.method == "POST" and form.validate(): 
        name = form.name.data
        username = form.username.data
        email = form.email
        password = sha256_crypt.encrypt(form.password.data) 
        cursor = mysql.connection.cursor() 
        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)" 
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()
        cursor.close()
        flash("You have successfully registered","success")
        return redirect(url_for("login"))
    else: 
        return render_template("register.html",form=form) 

#Login Request ve Response
@app.route("/login",methods = ["GET","POST"]) 
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
            username = form.username.data
            password_entered = form.password.data
            cursor = mysql.connection.cursor()
            sorgu = "Select * From users where username = %s"
            result = cursor.execute(sorgu,(username,)) 
            
            if result >0:
                data = cursor.fetchone() 
                real_password = data["password"]
                if sha256_crypt.verify(password_entered,real_password): 
                    flash("You have successfully logged in...","success")
                    session["logged_in"] = True 
                    session["username"] = username
                    return redirect(url_for("index"))
                else:
                    flash("You Entered Your Password Wrong...","danger")
                    return redirect(url_for("login"))
            else:   
                flash("There is no such user.","danger")
                return redirect(url_for("login"))
    else:
        return render_template("login.html",form=form)




#Logout Request and Repsonse
@app.route("/logout")
def logout():
    session.clear() 
    return redirect(url_for("index")) 



#Control Panel of Articles 
@app.route("/dashboard")
@login_required 
def dashboard():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s"

    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:

        return render_template("dashboard.html")
   

#Main Page
@app.route("/")
def index():

    return render_template("index.html")



#About Page
@app.route("/about")
def about():
    return render_template("about.html")



#Dinamic Url with  
@app.route("/article/<string:id>")
def detail(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:

        return render_template("article.html")

     

#Adding Article Articles Database
@app.route("/addarticle",methods=["GET","POST"]) 
def addarticle():
    form = ArticleForm(request.form)
    if request.method =="POST":
        title = form.title.data
        content = form.content.data
        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(title,session["username"],content)) 

        mysql.connection.commit()

        cursor.close()

        flash("Article Added Successfully","success")

        return redirect(url_for("dashboard"))
    else:
        return render_template("addarticle.html",form=form)

    
#Form of Article
class ArticleForm(Form):
    title = StringField("Article title:",validators=[validators.Length(min=5,max=100)])
    content = TextAreaField(validators=[validators.length(min=10)])

#All of Articles Page
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles"

    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall() 
        return  render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")


#Deleting Articles with Specific id in Dynamic Url
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where author = %s and Id = %s"

    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from articles where Id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        flash("Article Deleted Successfully...","success")
        return redirect(url_for("dashboard"))
    elif result == 0:#else:
        sorgu3 = "Select * from articles where Id = %s"
        result = cursor.execute(sorgu3,(id,))
        if result > 0: 
            flash("You are not authorized for this operation..","warning")    
        else:    
            flash("There is no such article...","warning")
        return redirect(url_for("index"))



#Update Article
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def edit(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where Id = %s and author = %s"

        result = cursor.execute(sorgu,(id,session["username"]))

        if result == 0:
            sorgu3 = "Select * from articles where Id = %s"
            result = cursor.execute(sorgu3,(id,))
            if result > 0: 
                flash("You are not authorized for this operation...","warning")  
                return redirect(url_for("index"))  
            else:    
                flash("There is no such article...","warning")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm()

            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("update.html",form=form)

    else:
        form = ArticleForm(request.form)
        
        newTitle = form.title.data
        newContent = form.content.data

        sorgu2 = "Update articles Set title = %s, content = %s where id = %s"

        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newTitle,newContent,id))
        mysql.connection.commit()
        cursor.close()
        flash("*** Article Updated Successfully ***","success")
        return redirect(url_for("dashboard"))


#Search Article
@app.route("/search",methods=["GET","POST"]) 
def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")

        cursor = mysql.connection.cursor()

        sorgu = "SELECT * from articles where title like '%" + keyword + "%'"  sp

        result = cursor.execute(sorgu)

        if result == 0:
            flash("No article found matching the searched title","warning")
            return redirect(url_for("articles"))
        else:
            articles = cursor.fetchall()

            return render_template("articles.html",articles = articles)

        
if __name__ == "main": 
    app.run(debug=True)

