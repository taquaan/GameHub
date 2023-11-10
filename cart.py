from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
app = Flask(__name__)
app.secret_key = "FelixPham"
sqldbname = "db/data.sqlite"

#khoi tao trang bat dau
@app.route('/')
def home():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("Select * from mytable;")
    data = cursor.fetchall()
    conn.close()
    return render_template(
        'Home.html', table=data
    )

#khoi tao search func
@app.route('/Search')
def index():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("Select * from mytable")
    data = cursor.fetchall()
    conn.close()
    return render_template(
        'Searching.html', table=data
    )



#Search func
@app.route('/searchData', methods=['POST'])
def searchData():
    search_text = request.form['searchInput']
    html_table,output_message = load_data_from_db(search_text)
    print(html_table)
    return render_template(
        'Searching.html',
        search_text=search_text,
        table=html_table,
        output_message=output_message if search_text else None
    )


#loaddatatudb
def load_data_from_db(search_text):
    if search_text != "":
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        sqlcommand = ("Select * from mytable "
                      "where Name like '%")+search_text+"%'"
        sqlcommand = sqlcommand + ("or Name like '%")+search_text+"%'"
        cursor.execute(sqlcommand)
        data = cursor.fetchall()
        conn.close()
        if len(data) == 0: #vong lap check game ton tai
            output_message = "No Matching Games Found"
            return data,output_message
        else:
            return data,None
    else: 
      return None,None

#Hien thi cac Game va Add to cart func
@app.route("/cart/add", methods=['POST'])
def add_to_cart():
    sqldbname = "db/data.sqlite"
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("SELECT Name, Pric, Img_url_1 "
                   "FROM mytable WHERE Name = ?",
                   (product_id,))
    product = cursor.fetchone()
    conn.close()
    product_dict = {
        "id": product_id,
        "Name": product[0],
        "Pric": product[1],
        "quantity": quantity
    }
    cart = session.get("cart", [])
    found = False
    for item in cart:
        if item["id"] == product_id:
            item["quantity"] += quantity
            found = True
            break
    if not found:
        cart.append(product_dict)
    session["cart"] = cart
    rows = len(cart)
    outputmessage = (f'"Product added to cart successfully!"'
                     f"</br>Current: "+str(rows)+" products"
                     f'<br>Continue Search! <a href="/">search page</a>'
                     f'<br>View Shopping Cart! <a href="/view_cart">View Cart</a>')

    return outputmessage



#Update cart
@app.route("/update_cart", methods=['POST'])
def update_cart():
    cart = session.get('cart',[])
    new_cart = []
    for product in cart:
        product_id = str(product['id'])
        if f'quantity-{product_id}' in request.form:
            quantity = int(request.form[f'quantity-{product_id}'])
            if quantity == 0 or f'delete={product_id}' in request.form:
                continue
            product['quantity']=quantity
        new_cart.append(product)
    session['cart']=new_cart
    return redirect(url_for('view_cart'))    

@app.route("/view_cart",methods=["POST"])
def view_cart():
    current_cart=[]
    if 'cart' in session:
        current_cart = session.get("cart",[])
    return render_template("cart.html",carts=current_cart)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
