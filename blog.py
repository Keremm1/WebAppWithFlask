#https://flask.palletsprojects.com/en/2.2.x/patterns/flashing/
#https://www.geeksforgeeks.org/python-functools-wraps-function/
#https://flask.palletsprojects.com/en/2.2.x/patterns/wtforms/
#https://flask.palletsprojects.com/en/2.2.x/patterns/viewdecorators/
#https://cdn.ckeditor.com/
#https://getbootstrap.com/docs/4.1/content/tables/
#https://getbootstrap.com/docs/4.0/components/list-group/
#https://bootsnipp.com/tags/search
#https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
#https://pythonbasics.org/flask-cookies/
from sqlite3 import Cursor
from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps #fonksiyonlar için kullandığımız bir fonksiyonu alıyoruz,yararlı decortarleri ve fonksiyonlara(örn:reduce) importla ulaşabiliriz

#Kullanıcı Giriş Decoratörü
def login_required(f):
    @wraps(f) #decorate edilen fonksiyon __name__ ve __doc__ u wrapper özelliklerine sahip olur fakat bu decorate ile bunu çözebiliriz 
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs) #login olduysa fonksiyon normal bir şekilde çalışsın
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın...","danger") #login yapılmadıysa login sayfasına yönlendirelim ve flash mesajı erkana basılsın(giriş yapmaya zorluyoruz)
            return redirect(url_for("login"))
    return decorated_function
#login_required fonksiyonu bir kez yazıldı ve artık kullanıcı girişi kontrolü gereken her request için kullanabiliriz(efektiflik) mesela bu sistemi kullanmadan her fonksiyonda sessionu kontrol etmeye çalışırsak kötü bir yöntem olur ve bu daha fazla koda yol açar ve kodumuz kirlenir



#Kullanıcı Kayıt Formu Oluşturma
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min=4,max=25),validators.DataRequired(message="Alan Zorunludur!")]) #başka eklenecek parametreler1ve bu paramtereler eklenecek veriler de mevcut bunlara wtformsun dokumantasyonundan bakarak kendimiz geliştirebiliriz(mesela validators lengthi ile girilen değerin uzunluğunu kısalığını belirttik aynı zamanda DataRequired da alanı doludrmak zorunlu gibi bir anlam içeren bir parametredir) stringfield bir class ve string değer girilecek yerlerde kullanılabilir 
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min=4,max=35)])
    email = StringField("Mail Adresi",validators=[validators.Email(message="Lütfen Geçerli Bir Email Adresi Girin...")])#girilen mail adresinin geçerli olup olmadığını değilse gösterilen mesajı göstermeyi böyle yapabiliriz
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message= "Lütfen Bir Parola Belirleyin"),
        validators.EqualTo(fieldname= "confirm",message="Parolanız Uyuşmuyor...")
    ])#confirm fieldi ile password fieldini karşılaştırır eğer karşılaştırma da eşleşmiyorlarsa mesaj bastıran bir koddur
    confirm = PasswordField("Parola Doğrula")

class LoginForm(Form):
    username = StringField("Kullanıcı Adı:")
    password = PasswordField("Şifre:")

app = Flask(__name__)
app.secret_key = "ybblog" #flash mesajlarını yayınlayabilmemiz için uygulamanın secret keyi olmalıdır
#(konfigürasyon) mysql e tanıtmamız gereken bilgiler var
app.config["MYSQL_HOST"]= "localhost" #buraya mysqlin çalıştığı hostu girmemiz gerekiyor şu an localhostta çalışıyoruz
app.config["MYSQL_USER"]= "root" #default olarak root geliyor
app.config["MYSQL_PASSWORD"] = "" #default olarak boş gelir
app.config["MYSQL_DB"] = "kbblog" #mysql veritabanı ismimizi vermeliyiz
app.config["MYSQL_CURSORCLASS"] = "DictCursor"    #flask ve mysql konfigurasyonu tamamlandı yani artık flaskımız mysql veritabanının nerede olduğunu biliyor(flaska mysqlimizi tanıttık) #bu belirtilen dictcursor biz verileri çekmek istediğimizde hangi tipte çektiğimizi belirtmemizi sağlar

mysql = MySQL(app) #konfigürasyon tamamlandı

#Kayıt Olma
@app.route("/register",methods= ["GET","POST"]) #yani bu urlmiz hem get request hem de post request alabilir demek bu belirtilmezse gelen post request hata verecektir
def register():
    form = RegisterForm(request.form) #eğer obje oluşturulurken sınıf içerisine bir değer girmezsek form boş olacaktır, bundan dolayı sayfaya hem post hem de get request attık ve bu requesti sınıf içine request.form olarak aldık ki form doldurulduğunda obje form ile beraber doldurumuş olsun(post request atıldığından post requestten aldığım formu göndermiş olduğum anlamına geliyor)
    if request.method == "POST" and form.validate(): #butona bastığımızda submit etömiştik yani bu blok post request atıldığı için bi repsonse gönderemediğinden hata verecektir buraya ise bu butona basılınca dönecek requesti belirlemeliyiz, form.validate() formda bir problem yoksa(Validate ile alakalı olarak) True değerini dönderecektir
        name = form.name.data
        username = form.username.data
        email = form.email
        password = sha256_crypt.encrypt(form.password.data) #datayı şifreleyerek göndermek için
        cursor = mysql.connection.cursor() #MySql den oluşturduğumuz mysql objesi üzerinde bir imleç oluşturuyoruz 
        #id auto increment olduğundan belirtilmesi gerekmez
        #sql hakkında daha fazla bilgi web3school sql dan
        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)" #%s sayesinde girilen değerler direkt olarak gönderilir eşitlenen özelliğe
        cursor.execute(sorgu,(name,email,username,password)) #buraya girilen değerler string %s yerine geçerler
        mysql.connection.commit() #uyguladık değişiklikleri
        cursor.close()
        flash("Başarıyla kayıt oldunuz","success")#soldaki parametre mesajı sağdaki str ise kategorini gösteriyor yani mesela yeşil gösteriyor, bu fonksiyon sayesinde get_flashed_messages a gider bu mesaj ve gerekli sayfada(messages.html) buradan mesajlar çekilir
        return redirect(url_for("login"))#return redirect("/") kodu da iş görür #response olarak farklı ulr adresine gitmek istediğimizi belirtiyoruz, url_for ile de içine yazılan fonksiyonla ilişkili olan urlye("/") gitmek istediğimizi belirtmiş oluyoruz
        #farkettim ki fonksiyonlar kod başlatıldığında flask sunucu tarafında oluşturuluyormuş direkt çünkü login bu kodun öncesinde değilve çalıştı 
    else: #"Get" normalde gönderdiğimiz requesttir
        return render_template("register.html",form=form) #normalde nasıl tempalteye değer gönderiyorask formu da o şkeilde gönderebiliriz
#http requestin get request mi yoksa post request mi olduğunu anlamak için rerquest modülü ile anlayabiliriz

#kayıt olma
@app.route("/login",methods = ["GET","POST"]) #bu sayfa da da get ve post request yapacağımız için belirtiyoruz
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
            username = form.username.data
            password_entered = form.password.data
            cursor = mysql.connection.cursor()
            sorgu = "Select * From users where username = %s"
            result = cursor.execute(sorgu,(username,)) #eğer bu sorgu sonucunda bu değer varsa result 0'dan farklı eğer yoksa 0 olacaktır.
            
            if result >0:
                data = cursor.fetchone() #bilgiler alındı data adresine verildi
                real_password = data["password"] #parola alındı
                if sha256_crypt.verify(password_entered,real_password): #kaydederken passwordu şifreleyerek göndermiştik bu yüzden böyle bir kodla iki parolanın aynı olupolmadığını kontrol etmiş oluruz(True veya False döndürür)
                    flash("Başarıyla Giriş Yaptınız...","success")
                    session["logged_in"] = True #Giriş yaptığımız için değeri True olacak ve aynı zamanda bu sessionu diğer html sayfalarında da rahatlıkla değer olarak kullanabiliriz yani bu sessionu return etmemize gerek yok
                    session["username"] = username
                    return redirect(url_for("index"))
                else:
                    flash("Parolanızı Yanlış Girdiniz...","danger")
                    return redirect(url_for("login"))
            else:   
                flash("Böyle Bir Kullanıcı Bulunmuyor.","danger")
                return redirect(url_for("login"))
    else:
        return render_template("login.html",form=form)




#Logout İşlemi
@app.route("/logout")
def logout():
    session.clear() #sessionu öldürür sıfırlar artık logged_in değiliz
    return redirect(url_for("index")) #hiçbir html sayfası göstermeden ana sayfaya döneriz(hızlı bir şekilde logout döner)



#kontrol paneli oluşturma
@app.route("/dashboard")
@login_required #giriş kontrolü yapıyoruz eğer login değilse kullanıcı site çalıştırılmaz ve login ekranına dönülür
def dashboard():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s"

    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:
        
        #flash("Henüz Makaleniz Bulunmuyor.")

        return render_template("dashboard.html")
    #dashboard urlsine sadece giriş yapan kullanıcılara response etmek isteriz login yapmayıp host/dahsboard ile girmeye çalışan requestleri engellemeye çalışmalıyız(eğer kullanıcı girişi varsa çalıştırsın yoksa çalıştırmasın decoratoru kullanmamız gerekecek)


@app.route("/")
def index():
    articles = [
        {"id":1,"title":"Deneme 1","content":"Deneme 1 'in İçeriği"},
        {"id":2,"title":"Deneme 2","content":"Deneme 2 'nin İçeriği"},
        {"id":3,"title":"Deneme 3","content":"Deneme 3'ün İçeriği"}
    ]
    numbers = [1,2,3,4,5] #demet de olabilir (iterable yapıda olmasıı yeterli)
    return render_template("index.html",answer = "hayır",islem = 2,numbers = numbers,articles=articles)




@app.route("/about")
def about():
    return render_template("about.html")



#dinamic url --> article'dan sonra girilen değer adında bir url dinamik olarak oluşturulur kendimiz belirtmek zorunda değiliz ve o idye göre response döndürülür
#ve Makale Detay Sayfası
@app.route("/article/<string:id>") #idyi ve id ye gelen değerin string olduğunu belirtiyoruz
def detail(id): #o değeri fonksiyonda parameter olarak almalıyız 
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        #flash("Böyle Bir Makale Bulunmuyor","warning")
        return render_template("article.html")
    #return "Article Id:" + id
     

#Makale Ekleme
@app.route("/addarticle",methods=["GET","POST"]) #izni verdik
def addarticle():
    form = ArticleForm(request.form)
    if request.method =="POST":
        title = form.title.data
        content = form.content.data
        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(title,session["username"],content)) #demetin içindeki değerleri tek tek sorgu içerisine %s yazan yerlere yerleştiriyor

        mysql.connection.commit()

        cursor.close()

        flash("Makale Başarıyla Eklendi","success")

        return redirect(url_for("dashboard"))
    else:
        return render_template("addarticle.html",form=form)
#Makale Form
class ArticleForm(Form):
    title = StringField("Makale Başlığı:",validators=[validators.Length(min=5,max=100)])
    content = TextAreaField(validators=[validators.length(min=10)]) #İçerik daha büyük bir alana sahip olması gerekteğinden Textareafield'ı kullandık.

#Makale Sayfası
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles"

    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall() #öncesinde tek değer aldığımız için fetchone metodunu kullanmıştık burada hepsini aldığımız için fetchall metodunu kullanmamız gerekecektir, MYSQL_CURSORCLASS ımız dict türünde olduğu için döndürülen değer dict değerinde olacak
        return  render_template("articles.html",articles=articles)
    else:
        #flash("Makale bulunmamaktadır","danger")
        return render_template("articles.html")


@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where author = %s and Id = %s" #böyle bir kullanıcı ve belirttiği id'de bir makale vvarsa result sıfırdan büyük çıkacağından işlem gerçekleşecektir ama biri tutmazsa gerçekleşmeyecek flash mesaj patlayacak

    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from articles where Id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        flash("Makale Başarıyla Silindi...","success")
        return redirect(url_for("dashboard"))
    elif result == 0:#else:
        sorgu3 = "Select * from articles where Id = %s"
        result = cursor.execute(sorgu3,(id,))
        if result > 0: 
            flash("Bu işlem için yetkiniz yok...","warning")    
        else:    
            flash("Böyle bir makale yok...","warning")
        return redirect(url_for("index"))



#Makale Güncelleme
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
                flash("Bu işlem için yetkiniz yok...","warning")  
                return redirect(url_for("index"))  
            else:    
                flash("Böyle bir makale yok...","warning")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm() #forma zaten sahibiz bilgileri o formdan çekmemiz gerekecek

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
        flash("*** Makale Başarıyla Güncellendi ***","success")
        return redirect(url_for("dashboard"))


#Arama Url
@app.route("/search",methods=["GET","POST"]) #sadece POST requeste izin vermemiz gerekiyor çünkü ara butonuna basıldığında başka sayfaya gitmek istemiyoruzz
def search():
    if request.method == "GET": #url ile /search yazıldığında ana sayfaya yönlendirmek istiyorum
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword") #post request sonucunda gelen form'dan keyowrd inputu aldığımızı belirtiyoruz(yani inpuuta yazılan değeri alıyoruz)

        cursor = mysql.connection.cursor()

        sorgu = "SELECT * from articles where title like '%" + keyword + "%'"  #sqldeki like operatörleri yardımıyla belirtilen ker değerini bulunduran verilerin seçilmesini sağlıyoruz buradaki %\'ler başına veya sonuna her şeyin gelebileceğini simgeler kaynak: https://www.w3schools.com/sql/sql_like.asp

        result = cursor.execute(sorgu)

        if result == 0:
            flash("Aranan başlığa uygun makale bulunamadı","warning")
            return redirect(url_for("articles"))
        else:
            articles = cursor.fetchall()

            return render_template("articles.html",articles = articles)
app.run(debug=True)

