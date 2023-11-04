from flask import Flask, render_template, request, session, url_for, redirect
import sqlite3
app: Flask = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    if 'username' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template(
        'Searching.html', search_text="", user_name = current_username)

@app.route('/viewcart', methods=["POST"])
def view_cart():
    current_cart = []
    if 'cart' in session:
        current_cart = session.get("cart", [])
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template(
        "cart_update.html",
        carts=current_cart, user_name = current_username)

@app.route('/update_cart', methods=['POST'])
def update_cart_1():
    cart = session.get('cart', [])
    new_cart = []
    for product in cart:
        product_id = str(product['id'])
        if f'quantity-{product_id}' in request.form:
            quantity = int(request.form[f'quantity-{product_id}'])
            if quantity == 0 or f'delete={product_id}' in request.form:
                continue
            product['quantity'] = quantity
        new_cart.append(product)
    session['cart'] = new_cart
    return redirect(url_for('view_cart'))

@app.route('/proceed_cart', methods=['POST'])
def proceed_cart():
    if 'current_user' in session:
        user_id = session['current_user']['id']
        user_email = session['current_user']['email']
    else:
        user_id = 0

    if 'cart' in session:
        shopping_cart = session.get("cart", [])
        sqldbname = "db/userData.db"
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        #Define order information
        order_number = "Order Number"
        purchase_date = "Purchase Date"
        payment_details = "Payment Details"
        order_status = 1

        cursor.execute('''insert into "orders" (user_id, user_email, order_number, purchase_date, payment_details, order_status, user_id) values (?,?,?,?,?)''',
                       (user_id, user_email, order_number, purchase_date, payment_details, order_status, ))
        order_id = cursor.lastrowid
        print(order_id)
        conn.commit()
        conn.close()

        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        for product in shopping_cart:
            product_id = product['id']
            price = product['price']
            quantity = product['quantity']
            cursor.execute('''insert into order_details (order_id, product_id, price, quantity) values (?,?,?,?)''',
                           (order_id, product_id, price,  quantity))
            
        conn.commit()
        conn.close()

        if 'cart' in session:
            current_cart = session.pop("cart", [])
        else:
            print("No current_cart in session.")
        order_url = url_for('orders', order_id=order_id, _external=True)
        return f'Redirecting to order page: <a href="{order_url}">{order_url}</a>'
    
@app.route('/orders/', defaults={'order_id': None}, methods=['GET'])
@app.route('/orders/<int:order_id>', methods=['GET'])
def orders(order_id):
    sqldbname = "db/orders.db"
    user_id = session.get('current_user', {}).get('id')
    if user_id:
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        if order_id:
            cursor.execute('select * from "orders" where id = ? and user_id = ?', (order_id, user_id))
            order = cursor.fetchone()
            cursor.execute('select * from order_details where order_id = ?', (order_id,))
            order_details = cursor.fetchall()
            conn.close()
            return render_template('orders_details.html', order=order, order_details=order_details)
        else:
            cursor.execute('select * from "orders" where user_id = ?', (user_id,))
            user_orders = cursor.fetchall()
            conn.close()
            return render_template('orders.html', orders=user_orders)
        return "User not logged in."
    
if __name__ == '__main__':
    app.run(debug=True)