import flask
import sqlite3

MemberID = 0

def get_db():
    db = sqlite3.connect('Salon.db')
    db.row_factory = sqlite3.Row
    return db

app = flask.Flask(__name__)

@app.route("/")
def homepage(): 
    return flask.render_template("homepage.html")

@app.route("/members")
def members():
    return flask.render_template("members.html")

@app.route("/members/add")
def addMem():
    return flask.render_template("addMem.html")

@app.route("/members/added", methods = ['POST'])
def memAdded():
    db = get_db()
    MemberID = int(db.execute("SELECT seq FROM sqlite_sequence sqseq WHERE\
                    sqseq.name = 'Member'").fetchall()[0][0]) + 1
    name = flask.request.form['name']
    gender = flask.request.form['gender']
    email = flask.request.form['email']
    contactNo = flask.request.form['contactNo']
    address = flask.request.form['address']
    
    db.execute("INSERT into Member values(?,?,?,?,?,?)",\
                (MemberID,name,gender,email,contactNo,address))
    db.commit()
    db.close()
    return flask.render_template("memAdded.html")

@app.route("/members/request")
def requestMem():
    return flask.render_template("requestMem.html")

@app.route("/members/view", methods = ['GET','POST'])
def memView():
    db = get_db()
    if flask.request.method == 'POST':
        rows = db.execute("SELECT * FROM Member WHERE Name = ?",[flask.request.form['name']]).fetchall()
        db.close()
    else:
        rows = db.execute("SELECT * FROM Member").fetchall()
        db.close()
    return flask.render_template("memView.html",rows=rows)

@app.route("/members/memSelect", methods = ['POST'])
def memSelect():
    global MemberID
    MemberID = flask.request.form['MemberID']
    return flask.render_template("memSelect.html")


@app.route("/members/update", methods = ['POST'])
def updateMem():
    global MemberID
    db = get_db()
    db.execute("UPDATE Member SET " + flask.request.form['Choice'] + " = '" + flask.request.form['newVal'] + "' WHERE MemberID = "+str(MemberID))
    db.commit()
    db.close()
    return flask.redirect("/members/view")

@app.route('/transactions')
def transactions():
    return flask.render_template('transactions.html')  

@app.route("/transactions/add")
def addTransactions():
    return flask.render_template("addTrans.html")

@app.route("/transactions/added", methods = ['POST'])
def transAdded():
    db = get_db()
    InvoiceNo = int(db.execute("SELECT seq FROM sqlite_sequence sqseq WHERE sqseq.name = 'Transactions'").fetchall()[0][0]) + 1
    data = flask.request.form
    MemberID = data['MemberID']
    Name = db.execute("SELECT Name from Member m where m.MemberID =" + MemberID).fetchall()[0][0]
    Date = data['Date']
    TotalAmount = 0
    
    Services = []
    
    Services.append(data['cut'])
    Services.append(data['highlight'])
    Services.append(data['colour'])
    Services.append(data['perm'])
    Services.append(data['rebonding'])
    Services.append(data['treatment'])

    for item in Services:
        if item != "no":
            db.execute("INSERT INTO TransactionDetails VALUES(?,?)",(InvoiceNo, item))
            TotalAmount += int(db.execute("SELECT Price from Service WHERE Type = '" + item + "'").fetchall()[0][0])
    
    db.execute("INSERT INTO Transactions VALUES(?, ?, ?, ?, ?)",(InvoiceNo, MemberID, Name, Date, TotalAmount))
    db.commit()
    db.close()
    return flask.render_template('transAdded.html')

@app.route("/transactions/direct_view_daily")
def direct_viewDaily():
    return flask.render_template("direct_viewDaily.html")

@app.route("/transactions/view_daily", methods = ['POST'])
def viewDaily():
    data = flask.request.form
    Date = str(data['Date'])
    
    db = get_db()
    
    rows = db.execute("SELECT * FROM Transactions WHERE Date_ = ?", (Date,)).fetchall()

    db.close()
    
    return flask.render_template("viewDaily.html", rows = rows)

@app.route("/transactions/direct_view_monthly")
def direct_viewMonthly():
    return flask.render_template('direct_viewMonthly.html')


@app.route("/transactions/view_monthly", methods = ['POST'])
def viewMonthly():
    data = flask.request.form
    Date = data['Date']

    months = {"01":"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"December"}
    date = months[Date[:2]]+" "+Date[3:]    
    lower = Date[:2]+"-01"+Date[2:]
    upper = Date[:1]+str(int(Date[1])+1)+"-01"+Date[2:]
    
    
    db = get_db()
    rows = db.execute("SELECT SUM(TotalAmount) FROM Transactions WHERE Date_ >= ? AND Date_ < ?", (lower,upper,)).fetchall()
    db.close()
        
    return flask.render_template("viewMonthly.html", rows = rows , date = date)

@app.route("/transactions/direct_view_member")   
def direct_viewMem():
    return flask.render_template("direct_viewMem.html")

@app.route("/transactions/view_member", methods = ['POST'])
def viewMem():
    data = flask.request.form
    ID = data['ID']
    db = get_db()
    rows = []
    
    dbCursorList = db.execute('SELECT InvoiceNo, Date_ , TotalAmount, Name FROM Transactions t WHERE t.MemberID = ' + ID).fetchall()
    for dbCursor in dbCursorList:
        InvoiceNo = dbCursor[0]
        svcs = db.execute('SELECT Service FROM TransactionDetails td WHERE td.InvoiceNo = '+str(InvoiceNo)).fetchall()
        
        services = []
        for svc in svcs:
            print(svc)
            if InvoiceNo == 132 and svc[0] == "Cut (long)":
                services.append("Cut botak")
            else:
                services.append(svc[0])

        svcString = ""
        for i in range(len(services)):
            if i == 0:
                svcString = str(services[i])
            else:
                svcString += " , " + str(services[i])
            
        if svcString ==  "Colour , Cut (long) , Highlight (full) , Perm , Rebonding , Treatment":
            svcString = "Full House"
        
        row = []
        for item in dbCursor:
                row.append(item)
            
        row.append(svcString)
        rows.append(row)
        
    name = dbCursorList[0][-1]
    db.close()
    return flask.render_template("viewMem.html", rows = rows, name = name)

@app.route('/viewmember')
def viewmember():
    return flask.render_template('viewmember.html')

if __name__ == '__main__':
    app.run(port = 9730, debug = True)

app.run(debug=True)
