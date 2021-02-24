import smtplib
from datetime import timedelta, date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, flash, redirect, url_for, render_template, request, session

from books import Books
from branch import Branch
from database import CursorFromConnectionFromPool
from database import Database
from user import User

Database.initialise(user='postgres',
                    password='8408905902',
                    database='libraryexample',
                    host='localhost')
app = Flask(__name__)
app.secret_key = "lmsprojse1minipres"
app.permanent_session_lifetime = timedelta(minutes=20)


def new_book(branch, copies, name, author, publisher, language, edition):
    for i in range(int(copies)):
        isbn = Books.newisbn(name, author, publisher, language, edition)
        copy_no = (Books.newcopy(isbn)) + 1

        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "insert into public.books(isbn,copy_no,name,author,language,publisher,branch_id,edition,issued_by) values(%s,%s,%s,%s,%s,%s,%s,%s,0);",
                (isbn, copy_no, name, author, language, publisher, branch, edition))


@app.route('/')
@app.route('/home')
def hello_world():
    with CursorFromConnectionFromPool() as cursor:
        cursor.execute(
            "SELECT  name,author FROM public.books WHERE suggest = (SELECT MIN(suggest) FROM public.books) and issued_by=0;")
        data = cursor.fetchone()
    strx = str(data)
    strx = strx.replace('[', '')
    strx = strx.replace(']', '')
    strx = strx.replace('(', '')
    strx = strx.replace(')', '')
    strx = strx.replace('"', '')
    strx = strx.replace("'", "")
    strx = strx.replace(",", '|')

    x = strx.split("|")

    name = x[0]
    author = x[1]
    return render_template("home.html", name=name, author=author)


@app.route('/login', methods=["POST", "GET"])
def login():
    if "user" in session:
        return redirect(url_for("user", email=session["user"]))
    if request.method == "POST":

        if "adminsesh" in session:
            return redirect(url_for("adminp"))
        else:
            password = request.form["psw"]
            email = request.form["email"]
            if User.check_user(email, password):
                flash("login successful")
                if User.check_admin(email, password):
                    session["adminsesh"] = email
                    return redirect(url_for("adminp"))
                else:
                    session["user"] = email
                    return redirect(url_for("user", email=email))
            else:
                return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        if "user" in session:
            return redirect(url_for("user"))
        elif "adminsesh" in session:
            return redirect(url_for("adminp"))
        else:
            email = request.form["email"]
            userc = User(first_name=request.form["firstname"],
                         last_name=request.form["lastname"],
                         password=request.form["psw"],
                         email=request.form["email"],
                         phone_number=request.form["pnumber"],
                         id=None)
            userc.new_user()
            userc.id = userc.assignid(userc.email)
            session["user"] = userc.id
            flash("login successful")
            return redirect(url_for("user", email=email))
    else:
        return render_template("signup.html")


@app.route("/admin", methods=["GET", "POST"])
def adminp():
    if "adminsesh" in session:
        flash("login successful")
        data=User.get_all_users()
        return render_template("admin.html",data=data)

    else:
        return render_template("login.html")

@app.route('/book/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        name = request.form["name"]
        isbn = request.form["isbn"]
        author = request.form["author"]
        language = request.form["language"]
        publisher = request.form["publisher"]
        edition = request.form["edition"]

        resultsr = Books.search(name, isbn, author, language, publisher, edition)

        return render_template('search.html', resultsr=resultsr)
    return render_template('search.html')


@app.route("/book/<bookname>", methods=["GET", "POST"])
def book(bookname):
    data = Books.search(isbn=bookname)
    strx = str(data)
    strx = strx.replace('[', '')
    strx = strx.replace(']', '')
    strx = strx.replace('(', '')
    strx = strx.replace(')', '')
    strx = strx.replace('"', '')
    strx = strx.replace("'", "")
    strx = strx.replace(",", '|')

    x = strx.split("|")
    isbn = x[0]
    name = x[1]
    author = x[2]
    language = x[3]
    publisher = x[4]
    edition = x[5]
    branch = x[6]

    startdate = date.today()
    EndDate = date.today() + timedelta(days=7)

    if request.method == "POST":

        if "user" in session:
            email = session["user"]
            print(email)
            with CursorFromConnectionFromPool() as cursor:

                cursor.execute("select returndate,issuedbyisbn from public.users where email=%s;", (email,))

                returndate = cursor.fetchone()
                print(returndate)
                strx = str(returndate)
                strx = strx.replace('[', '')
                strx = strx.replace(']', '')
                strx = strx.replace('(', '')
                strx = strx.replace(')', '')
                strx = strx.replace('"', '')
                strx = strx.replace("'", "")
                strx = strx.replace(",", '|')
                strx = strx.replace(" ", "")

                x = strx.split("|")

                returndate = x[0]
                returnisbn = x[1]
                print(type(returnisbn))
                print(type(returndate))
                if returndate == '0' and returnisbn == '0':
                    print(returndate)
                    print(returnisbn)
                    if Books.copiesavailable(isbn):
                        with CursorFromConnectionFromPool() as cursor:
                            cursor.execute("UPDATE public.users SET issuedbyisbn=%s WHERE email=%s", (isbn, email))
                            cursor.execute("update public.users set returndate=%s where email=%s", (EndDate, email))
                        fromaddr = "librarymanagementsys01@gmail.com"
                        toaddr = email
                        msg = MIMEMultipart()
                        msg['From'] = fromaddr
                        msg['To'] = toaddr
                        msg["Subject"] = "You issue request for {} is underway".format(name)
                        branch = Branch.searchbranch(branch)
                        body = "You have been issued {} by {} from {} till {}. Please collect this book from branch {} at {}. Please return the book to the same branch it was issued from.".format(
                            name, author, startdate, EndDate, branch[0], branch[1])
                        msg.attach(MIMEText(body, 'plain'))
                        email = smtplib.SMTP('smtp.gmail.com', 587)
                        email.starttls()
                        email.login(fromaddr, "seprojsubmit")
                        message = msg.as_string()
                        email.sendmail(fromaddr, toaddr, message)
                        Books.issuethis(isbn)
                        flash("Book has been issued, email confirmation has been sent to you")
                        return redirect(url_for("book", bookname=isbn))
                    else:
                        flash("Issue failed, no copies in stock, please inquire again in 1 week")
                        return redirect(url_for("user", email=session[""]))
                else:
                    flash("You already have a book issued, please return that book to issue a new one")
                    return redirect(url_for("user", email=session[""]))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("book.html", bookname=bookname, isbn=isbn, name=name, author=author, language=language,
                               publisher=publisher, edition=edition)


@app.route("/user/<email>", methods=["POST", "GET"])
def user(email):
    if "user" in session:
        with CursorFromConnectionFromPool() as cursor:

            cursor.execute("select returndate,issuedbyisbn from public.users where email=%s;", (email,))
            returndate = cursor.fetchone()

            strx = str(returndate)
            strx = strx.replace('[', '')
            strx = strx.replace(']', '')
            strx = strx.replace('(', '')
            strx = strx.replace(')', '')
            strx = strx.replace('"', '')
            strx = strx.replace("'", "")
            strx = strx.replace(",", '|')
            strx = strx.replace(" ", "")

            x = strx.split("|")

            returndate = x[0]
            returnisbn = x[1]
            print(x)
            if returndate == '0' and returnisbn == '0':
                return render_template("user.html",
                                       message="You have not issued any book, you can issue books through the Search menu.")

            else:
                query = "sel"+"ect name, author,branch_id from public.books where isbn='"+returnisbn+"' and issued_by=1;"
                print(query)
                cursor.execute(query)
                data = cursor.fetchone()
                strx = str(data)
                strx = strx.replace('[', '')
                strx = strx.replace(']', '')
                strx = strx.replace('(', '')
                strx = strx.replace(')', '')
                strx = strx.replace('"', '')
                strx = strx.replace("'", "")
                strx = strx.replace(",", '|')

                x = strx.split("|")
                name = x[0]

                author = x[1]
                branch = x[2]
                cursor.execute("select branch_name, branch_address from public.branch where branch_id=%s", (branch,))
                data = cursor.fetchone()
                strx = str(data)
                strx = strx.replace('[', '')
                strx = strx.replace(']', '')
                strx = strx.replace('(', '')
                strx = strx.replace(')', '')
                strx = strx.replace('"', '')
                strx = strx.replace("'", "")
                strx = strx.replace(",", '|')

                x = strx.split("|")
                branch_name = x[0]
                branch_address = x[1]
                return render_template("user.html", name=name, author=author, branchname=branch_name,
                                       branchaddress=branch_address, date=returndate)




    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("you have been logged out!", "info")
    session.pop("user", None)
    session.pop("adminsesh", None)
    return redirect(url_for("login"))


@app.route("/addbook", methods=["GET", "POST"])
def addbook():
    if request.method == "POST":
        if "adminsesh" in session:

            name = request.form["name"]
            copies = request.form["copy"]
            author = request.form["author"]
            language = request.form["language"]
            publisher = request.form["publisher"]
            branch = request.form["branch"]
            edition = request.form["edition"]

            new_book(branch, copies, name, author, publisher, language, edition)

            flash("books added")
            return redirect(url_for("adminp"))
        else:
            return redirect(url_for("login"))
    else:
        return render_template("addbook.html")



@app.route("/returnbook",methods=["GET","POST"])
def returnbook():
    if request.method=="POST":
        if "adminsesh" in session:
            isbn=request.form["isbn"]
            email=request.form["email"]
            Books.returnthis(isbn)
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("UPDATE public.users SET issuedbyisbn=0 WHERE email=%s", (email,))
                cursor.execute("update public.users set returndate=0 where email=%s", (email,))
            flash("book returned")
            return redirect(url_for("adminp"))
    else:
        return render_template("returnbook.html")

if __name__ == '__main__':
    app.run(port=5000, debug=True)
