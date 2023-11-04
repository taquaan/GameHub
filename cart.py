from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
app = Flask(__name__)
app.secret_key = "FelixPham"
sqldbname = "db/website.db"

@app.route('/')
def index():
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("Select * from storages")
    data = cursor.fetchall()
    conn.close()
    return render_template(
        'shoppingcart.html', table=data
    )

@app.route('/searchData', methods=['POST'])
def searchData():
    search_text = request.form['searchInput']
    html_table = load_data_from_db(search_text)
    print(html_table)
    return render_template(
        'shoppingcart.html',
        search_text=search_text,
        table=html_table
    )

def load_data_from_db(search_text):
    if search_text != "":
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        sqlcommand = ("Select * from storages "
                      "where brand like '%")+search_text+"%'"
        sqlcommand = sqlcommand + ("or model like '%")+search_text+"%'"
        cursor.execute(sqlcommand)
        data = cursor.fetchall()
        conn.close()
        return data

def load_data(search_text):
    import pandas as pd
    df = pd.read_csv('gradedata.csv')
    dfX = df
    if search_text != "":
            dfX = df[(df["fname"] == search_text) |
                     (df["lname"] == search_text)]
            print (dfX)
    html_table = dfX.to_html(classes='data',
                             escape=False)
    return html_table

@app.route("/cart/add", methods=['POST'])
def add_to_cart():
    sqldbname = "db/website.db"
    product_id = request.form["product_id"]
    quantity = int(request.form["quantity"])
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("SELECT model, price, picture, details "
                   "FROM storages WHERE id = ?",
                   (product_id,))
    product = cursor.fetchone()
    conn.close()
    product_dict = {
        "id": product_id,
        "name": product[0],
        "price": product[1],
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

@app.route("/viewcart",methods=["POST"])
def view_cart():
    current_cart=[]
    if 'cart' in session:
        current_cart = session.get("cart",[])
    return render_template("cart.html",carts=current_cart)
# #connect to db
# def connect_db():
#     conn = sqlite3.connect(sqldbname)  # Replace 'your_database.db' with your actual database file name
#     conn.row_factory = sqlite3.Row
#     return conn

# # Route to display the filtered data
# @app.route('/filter', methods=['GET', 'POST'])
# def filter_data():
#     if request.method == 'POST':
#         selected_filters = request.form.getlist('filter')  # Assuming you have checkbox inputs with the name 'filter'
#         conn = connect_db()
#         cursor = conn.cursor()
#         query = "SELECT * FROM storages WHERE RAM IN ({})".format(','.join(['?'] * len(selected_filters)))
#         cursor.execute(query, selected_filters)
#         result = cursor.fetchall()
#         conn.close()
#         return render_template('shoppingcart.html', data=result)
#     else:
#         return render_template('shoppingcart.html')

if __name__ == '__main__':
    app.run(port=8000, debug=True)
