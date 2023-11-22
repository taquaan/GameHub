from flask import (Flask, render_template, request, redirect, session, url_for, jsonify, flash)
import sqlite3, uuid
from datetime import datetime

app = Flask(__name__)
sqldbuser = 'db/userData.db'
sqldbgame = 'db/game-db.db'
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

# RESET SESSION FUNCTION (WILL RESET LOGIN)
@app.route('/reset_session')
def reset_session():
    session.clear()
    return redirect(url_for('index'))

# INDEX FUNCTION
@app.route("/")
def index():
    conn = sqlite3.connect(sqldbgame)
    cursor = conn.cursor()
    cursor.execute("Select * from GameDB")
    data = cursor.fetchall()
    conn.close()
    return render_template("index.html", table=data)

# GENERATE ORDER ID FUNCTION
def generate_order_id():
    # Generate a UUID and remove dashes to create a custom order ID
    return str(uuid.uuid4()).replace('-', '')

# SEARCH FUNCTION
@app.route('/search')
def search():
    conn = sqlite3.connect(sqldbgame)
    cursor = conn.cursor()
    cursor.execute("Select * from GameDB")
    data = cursor.fetchall()
    conn.close()
    return render_template(
        'search.html', table=data
    )

# SEARCH FUNCTION WITH DATA
@app.route('/searchData', methods=['POST'])
def searchData():
    search_text = request.form['searchInput']
    html_table, output_message = load_data_from_db(search_text)
    if html_table != None:
      return render_template(
          'search.html',
          search_text=search_text,
          table=html_table,
          output_message=output_message if search_text else None
      )
    else:
      return redirect(url_for('search'))

# FILTER FUNCTION
@app.route('/filter', methods=['POST'])
def filterData():
    filter_values = request.form.getlist('filter')
    html_table, output_message = load_filtered_data_from_db(filter_values)
    print(filter_values)
    return render_template(
        'search.html',
        table=html_table,
        output_message=output_message
    )


# LOAD DATA FROM DB WITH FILTER
def load_filtered_data_from_db(search_text):
    conn = sqlite3.connect(sqldbgame)
    cursor = conn.cursor()
    sqlcommand = ("SELECT * FROM GameDB "
                  "WHERE Tags LIKE ? "
                  "OR Publisher LIKE ?")
    search_text = search_text[0]  # Assuming search_text is a list with a single element
    cursor.execute(sqlcommand, ('%' + search_text + '%', '%' + search_text + '%'))
    data = cursor.fetchall()
    conn.close()
    if len(data) == 0:
        output_message = "No Matching Games Found"
        return data, output_message
    else:
        return data, None
    

# LOAD DATA FROM DB
def load_data_from_db(search_text):
    if search_text != "":
        conn = sqlite3.connect(sqldbgame)
        cursor = conn.cursor()
        sqlcommand = ("Select * from GameDB "
                      "where GameTitle like '%")+search_text+"%'"
        sqlcommand = sqlcommand + ("or GameTitle like '%")+search_text+"%'"
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

# LOGIN FUNCTION
@app.route("/login", methods=["GET","POST"])
def login():
    error = False
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        if check_exists(username, password):
            session['username'] = username
            session['logged_in'] = True
            # Redirect to the next URL or a default page
            url_fallback = session.pop('url_fallback', None)
            if url_fallback != None:
                return redirect(url_fallback)
            else:
                return redirect(url_for('index'))
        else:
            error = True
    return render_template('login.html', error=error)

# Check if the input data is correct
def check_exists(username, password):
  result = False;
  conn = sqlite3.connect(sqldbuser)
  cursor = conn.cursor()
  sqlcommand="Select * from users where username = '"+username+"' or email = '"+username+"' and password = '"+password+"'"
  cursor.execute(sqlcommand)
  data=cursor.fetchall()
  print(type(data))
  if len(data)>0:
    result=True
  conn.close()
  return result

# LOGOUT FUNCTION
@app.route("/logout")
def logout():
    username = None
    session['username'] = username
    session['logged_in'] = False
    return redirect(url_for('index'))

# REGISTER FUNCTION
#Create the ID for a new user
def generateID(table):
    max_id = 0
    conn = sqlite3.connect(sqldbuser)
    cursor = conn.cursor()
    sqlcommand = "Select Max(id) from "+table+""
    cursor.execute(sqlcommand)
    max_id = cursor.fetchone()[0]
    if max_id == None:
      max_id = 0
    return max_id

# Check if there already has that username
def user_exists(username, email):
    conn = sqlite3.connect(sqldbuser)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ? OR email = ?", (username, email))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Save the information of new user to DB
def saveToDB(username, email, password):
    if user_exists(username, email):
        # User with the given username already exists
        return None
    table = 'users'
    new_id = generateID(table) + 1
    conn = sqlite3.connect(sqldbuser)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(id, username, email, password, number_of_games, number_of_badges, number_of_friends) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (new_id, username, email, password, 0, 0, 0))
    conn.commit()
    conn.close()
    return new_id
  
@app.route("/register", methods=["GET","POST"])
def register():
  session['logged_in'] = False
  if request.method == "POST":
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"] 
    # Add user to DB
    new_id = saveToDB(username, email, password)
    if new_id:
        # User added successfully
        # Set the header to logged_in
        session['username'] = username
        session['logged_in'] = True
        # Show successfully register notification
        return render_template("register.html", success=True)
    else:
        # User with the given username or email already exists
        return render_template("register.html", success=False, error="User with the given username or email already exists.")
  return render_template("register.html")

# PRODUCT PAGE FUNCTION
@app.route('/product-<int:GameID>')
def product_page(GameID):
    conn = sqlite3.connect(sqldbgame)
    cursor = conn.cursor()
    cursor.execute('SELECT Cover, Thumbnail1, Thumbnail2, Thumbnail3, Thumbnail4, Trailer, TrailerThumbnail, GameTitle, DiscountPer, OldPrice, NewPrice FROM GameDB WHERE GameID = ?', (GameID,))
    thumbnails = cursor.fetchone()
    if thumbnails:
      game_info = {
        'cover_art': thumbnails[0],
        'thumbnail_1': thumbnails[1],
        'thumbnail_2': thumbnails[2],
        'thumbnail_3': thumbnails[3],
        'thumbnail_4': thumbnails[4],
        'trailer': thumbnails[5],
        'trailer_thumb': thumbnails[6],
      }
    cursor.execute('SELECT GameTitle, DiscountPer, OldPrice, NewPrice, SupportedOS, InAppPur, Genre, Publisher FROM GameDB WHERE GameID = ?', (GameID,))
    data = cursor.fetchone()
    if data:
      game_info_2 = {
        'game_title': data[0],
        'discount': data[1],
        'old_price': data[2],
        'new_price': data[3],
        'supported_os': data[4],
        'in_app': data[5],
        'genre': data[6],
        'publisher': data[7],
      }
      game_info = {**game_info, **game_info_2}
    action_msg = session.pop('action_msg', None)
    return render_template(
        'product-page.html', GameID=GameID, **game_info, message=action_msg)

# GAME INFO API
@app.route('/api/<int:GameID>', methods=['GET'])
def get_game_info(GameID):
    # Basic Game Info
    conn = sqlite3.connect(sqldbgame)
    cursor = conn.cursor()
    cursor.execute('SELECT GameTitle, Cover, Description, DiscountPer, OldPrice, NewPrice, InAppPur, Developer, Publisher, ReleaseDate, SupportedOS, Tags, UpdateLogs, OverallReview, OverallReviewText, ESRBLabel, ESRBContent, ESRBInteract, Features, FeatureNotice, Genre FROM GameDB WHERE GameID = ?', (GameID,))
    data = cursor.fetchone()
    if data:
      game_info = {
        'game_title': data[0],
        'genre': data[20],
        'cover_art': data[1],
        'description': data[2],
        'discount': data[3],
        'old_price': data[4],
        'new_price': data[5],
        'in_app': data[6],
        'developer': data[7],
        'publisher': data[8],
        'release_date': data[9],
        'supported_os': data[10],
        'tags': data[11],
        'update_logs': data[12],
        'review_score': data[13],
        'review_text': data[14],
        'esrb': data[15],
        'esrb_content': data[16],
        'esrb_interact': data[17],
        'features': data[18],
        'feature_notice': data[19],
      }
      if game_info['new_price'] == 0:
        game_info['new_price'] = 'Free'
      else:
        game_info['new_price'] = "{:,}đ".format(data[5]).replace(",", ".")
      if game_info['old_price'] != None:
        game_info['old_price'] = "{:,}đ".format(data[4]).replace(",", ".")
    else:
      return 'Error 404. Game not found!', 404
    # System Requirements
    sys_list = ['OS', 'Processor', 'Memory', 'Graphics', 'DirectX', 'Network', 'Storage', 'Notes'] 
    prefixes = ['Min', 'Rec']
    sys_prelist = []
    for item in sys_list:
       for prefix in prefixes:
          sys_prelist.append(f"{prefix}{item}")
    system_requirements = {}
    for item in sys_prelist:
      if 'Windows' in game_info['supported_os']:
        cursor.execute(f"SELECT {item}Win FROM GameDB WHERE GameID = ?", (GameID,))
        result = cursor.fetchone()
        if result:
          system_requirements[f'{item}Win'] = result[0]
      if 'macOS' in game_info['supported_os'] and 'DirectX' not in item:
        cursor.execute(f"SELECT {item}Mac FROM GameDB WHERE GameID = ?", (GameID,))
        result = cursor.fetchone()
        if result:
          system_requirements[f'{item}Mac'] = result[0]
      if 'Linux' in game_info['supported_os'] and 'DirectX' not in item:
        cursor.execute(f"SELECT {item}Linux FROM GameDB WHERE GameID = ?", (GameID,))
        result = cursor.fetchone()
        if result:
          system_requirements[f'{item}Linux'] = result[0]
      cursor.execute('SELECT LanguageAudio, LanguageText, Copyright, Bit64Required FROM GameDB WHERE GameID = ?', (GameID,))
      result = cursor.fetchone()
      if result:
          system_requirements['LanguageAudio'] = result[0]
          system_requirements['LanguageText'] = result[1]
          system_requirements['Copyright'] = result[2]
          system_requirements['Bit64Required'] = result[3]
    conn.close()
    return jsonify(game_info, system_requirements)

# INSTANT BUY FUNCTION
@app.route('/buy', methods=['POST'])
def buy():
    # Get data from the form
    game_id = request.form.get('game_id')
    game_title = request.form.get('game_title')
    game_cover = request.form.get('game_cover')
    if request.form.get('old_price') != "None":
      old_price = int(request.form.get('old_price'))
    else:
      old_price = None
    discount_per = float(request.form.get('discount_per'))
    new_price = int(request.form.get('new_price'))
    in_app = request.form.get('in_app')
    supported_os = request.form.get('supported_os')
    # Create a dictionary representing the item
    item = {
        'id': game_id,
        'title': game_title,
        'old_price': old_price,
        'discount_per': discount_per,
        'new_price': new_price,
        'in_app': in_app,
        'quantity': 1, # You can adjust this as needed
        'game_cover': game_cover,
        'supported_os': supported_os,
    }
    # Get the current cart or create an empty one
    session['instant_cart'] = [item]
    # Generate a custom order ID
    order_uuid = generate_order_id()
    # Store the order ID in the session
    session['instant_order_id'] = order_uuid
    # Check if user is logged in or not
    if 'username' not in session or not session['logged_in']:
        session['url_fallback'] = url_for('instant_checkout',order_uuid=order_uuid)
        return redirect(url_for('login'))
    return redirect(url_for('instant_checkout',order_uuid=order_uuid))

@app.route('/checkout-<order_uuid>')
def instant_checkout(order_uuid):
    # Retrieve the user's cart from the session
    cart = session.get('instant_cart', [])
    # Calculate total price
    total_price = sum(item['new_price'] for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price, order_uuid=order_uuid)

#ADD TO CART FUNCTION
@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    # Get data from the form
    game_id = request.form.get('game_id')
    game_title = request.form.get('game_title')
    game_cover = request.form.get('game_cover')
    if request.form.get('old_price') != "None":
      old_price = int(request.form.get('old_price'))
    else:
      old_price = None
    discount_per = float(request.form.get('discount_per'))
    new_price = int(request.form.get('new_price'))
    in_app = request.form.get('in_app')
    supported_os = request.form.get('supported_os')
    # Create a dictionary representing the item
    item = {
        'id': game_id,
        'title': game_title,
        'old_price': old_price,
        'discount_per': discount_per,
        'new_price': new_price,
        'in_app': in_app,
        'quantity': 1,  # You can adjust this as needed
        'game_cover': game_cover,
        'supported_os': supported_os,
    }
    # Check if user is logged in or not
    if 'username' not in session or not session['logged_in']:
        session['url_fallback'] = url_for('product_page', GameID=game_id)
        return redirect(url_for('login'))
    # Get the current cart or create an empty one
    cart = session.get('cart', [])
    # Check if the item is already in the cart
    for cart_item in cart:
        if cart_item['id'] == game_id:
            # Item is already in the cart, update quantity or handle as needed
            cart_item['quantity'] += 1
            session['action_msg'] = f'{game_title} is already in your cart.'
            session['cart'] = cart  # Update the cart in the session
            return redirect(url_for('product_page', GameID=game_id))
    # Check if the 'wishlist' key exists in the session
    if 'wishlist' in session:
        wishlist = session['wishlist']
        # Check if the item is in the wishlist
        if any(cart_item['id'] == game_id for cart_item in wishlist):
            # Filter the cart to exclude the item with the specified game_id
            item_to_move = next((item for item in wishlist if item['id'] == game_id), None)
            # Check if the item was found in the cart
            if item_to_move:
                # Remove the item from the cart
                wishlist.remove(item_to_move)
                # Check if the 'wishlist' key exists in the session
                current_cart = session.get('cart', [])
                # Add the item to the wishlist
                current_cart.append(item_to_move)
                # Update the cart and wishlist in the session
                session['cart'] = current_cart
                session['wishlist'] = wishlist
                session['action_msg'] = f'{game_title} moved to cart successfully.'
            return redirect(url_for('product_page', GameID=game_id))
    # Item is not in the cart, add it
    cart.append(item)
    session['cart'] = cart
    session['action_msg'] = f'{game_title} has been added to your cart.'
    return redirect(url_for('product_page', GameID=game_id))

#VIEW CART FUNCTION
@app.route('/cart')
def view_cart():
    if 'username' not in session or not session['logged_in']:
        session['url_fallback'] = url_for('cart')
        return redirect(url_for('login'))
    current_cart = []
    discount = 0
    total_price = 0
    og_total_price = 0
    num_items = 0
    if 'cart' in session:
        current_cart = session.get("cart", [])
        for item in current_cart:
          if item['old_price'] != None:
            og_total_price += int(item['old_price'])
          else:
            og_total_price += int(item['new_price'])
          total_price += int(item['new_price'])
          discount = max(0, og_total_price - total_price)
          num_items = len(current_cart)
    action_msg = session.pop('action_msg', None)
    return render_template(
        "cart.html", cart=current_cart, total_price=total_price, og_total=og_total_price, discount=discount, num_items=num_items, message=action_msg)

#MOVE TO CART FUNCTION
@app.route('/move_to_cart', methods=['POST'])
def move_to_cart():
    wishlist = session.get("wishlist", [])
    game_id = request.form.get('game_id')
    # Check if the 'wishlist' key exists in the session
    if 'wishlist' in session:
        # Filter the cart to exclude the item with the specified game_id

        item_to_move = next((item for item in wishlist if item['id'] == game_id), None)
        # Check if the item was found in the cart
        if item_to_move:
            game_title = request.form.get('game_title')
            # Remove the item from the cart
            wishlist.remove(item_to_move)
            # Check if the 'wishlist' key exists in the session
            current_cart = session.get('cart', [])
            # Add the item to the wishlist
            current_cart.append(item_to_move)
            # Update the cart and wishlist in the session
            session['cart'] = current_cart
            session['wishlist'] = wishlist
            session['action_msg'] = f'{game_title} moved to cart successfully.'
    return redirect(url_for('view_wishlist'))

#REMOVE FROM CART FUNCTION
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    current_cart = session.get("cart", [])
    game_id = request.form.get('game_id')
    # Check if the 'cart' key exists in the session
    if 'cart' in session:
        game_title = request.form.get('game_title')
        # Filter the cart to exclude the item with the specified game_id
        current_cart = [item for item in current_cart if item['id'] != game_id]
        # Update the cart in the session
        session['cart'] = current_cart
        session['action_msg'] = f'{game_title} removed from the cart successfully.'
    return redirect(url_for('view_cart'))

#ADD TO WISHLIST FUNCTION
@app.route('/add-to-wishlist', methods=['POST'])
def add_to_wishlist():
    # Get data from the form
    game_id = request.form.get('game_id')
    game_title = request.form.get('game_title')
    game_cover = request.form.get('game_cover')
    if request.form.get('old_price') != "None":
      old_price = int(request.form.get('old_price'))
    else:
      old_price = None
    discount_per = float(request.form.get('discount_per'))
    new_price = int(request.form.get('new_price'))
    in_app = request.form.get('in_app')
    supported_os = request.form.get('supported_os')
    # Create a dictionary representing the item
    item = {
        'id': game_id,
        'title': game_title,
        'old_price': old_price,
        'discount_per': discount_per,
        'new_price': new_price,
        'in_app': in_app,
        'quantity': 1,  # You can adjust this as needed
        'game_cover': game_cover,
        'supported_os': supported_os,
    }
    # Check if user is logged in or not
    if 'username' not in session or not session['logged_in']:
        session['url_fallback'] = url_for('product_page', GameID=game_id)
        return redirect(url_for('login'))
    # Get the current cart or create an empty one
    wishlist = session.get('wishlist', [])
    # Check if the item is already in the cart
    for wishlist_item in  wishlist:
        if wishlist_item['id'] == game_id:
            # Item is already in the cart, update quantity or handle as needed
            wishlist_item['quantity'] += 1
            session['action_msg'] = f'{game_title} is already in your wishlist.'
            session['wishlist'] = wishlist  # Update the cart in the session
            return redirect(url_for('product_page', GameID=game_id))

    # Check if the 'cart' key exists in the session
    if 'cart' in session:
        current_cart = session['cart']
        # Filter the cart to exclude the item with the specified game_id
        item_to_move = next((item for item in current_cart if item['id'] == game_id), None)
        # Check if the item was found in the cart
        if item_to_move:
            # Remove the item from the cart
            current_cart.remove(item_to_move)
            # Check if the 'wishlist' key exists in the session
            wishlist = session.get('wishlist', [])
            # Add the item to the wishlist
            wishlist.append(item_to_move)
            # Update the cart and wishlist in the session
            session['cart'] = current_cart
            session['wishlist'] = wishlist
            session['action_msg'] = f'{game_title} moved to wishlist successfully.'
            return redirect(url_for('product_page', GameID=game_id))
    # Item is not in the cart, add it
    wishlist.append(item)
    session['wishlist'] = wishlist
    session['action_msg'] = f'{game_title} has been added to your wishlist.'
    return redirect(url_for('product_page', GameID=game_id))

#MOVE TO WISHLIST FUNCTION
@app.route('/move_to_wishlist', methods=['POST'])
def move_to_wishlist():
    current_cart = session.get("cart", [])
    game_id = request.form.get('game_id')
    # Check if the 'cart' key exists in the session
    if 'cart' in session:
        # Filter the cart to exclude the item with the specified game_id
        item_to_move = next((item for item in current_cart if item['id'] == game_id), None)
        # Check if the item was found in the cart
        if item_to_move:
            game_title = request.form.get('game_title')
            # Remove the item from the cart
            current_cart.remove(item_to_move)
            # Check if the 'wishlist' key exists in the session
            wishlist = session.get('wishlist', [])
            # Add the item to the wishlist
            wishlist.append(item_to_move)
            # Update the cart and wishlist in the session
            session['cart'] = current_cart
            session['wishlist'] = wishlist
            session['action_msg'] = f'{game_title} moved to wishlist successfully.'
    return redirect(url_for('view_cart'))

#REMOVE FROM WISHLIST FUNCTION
@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    wishlist = session.get("wishlist", [])
    game_id = request.form.get('game_id')
    # Check if the 'wishlist' key exists in the session
    if 'wishlist' in session:
        game_title = request.form.get('game_title')
        # Filter the wishlist to exclude the item with the specified game_id
        wishlist = [item for item in wishlist if item['id'] != game_id]
        # Update the wishlist in the session
        session['wishlist'] = wishlist
        session['action_msg'] = f'{game_title} removed from the wishlist successfully.'
    return redirect(url_for('view_wishlist'))

#CHECKOUT FUNCTION
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Check if the user is logged in
    if 'username' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    # Retrieve the user's cart from the session
    cart = session.get('cart', [])
    # Calculate total price
    total_price = sum(item['new_price'] for item in cart)
    # Generate a unique order_id (you can use uuid or any other method)
    order_uuid = generate_order_id()
    session['order_id'] = order_uuid
    return render_template('checkout.html', cart=cart, total_price=total_price, order_uuid=order_uuid)

#PROCEED TO CHECKOUT FUNCTION
@app.route('/proceed-checkout-<order_uuid>', methods=['GET', 'POST'])
def proceed_checkout(order_uuid):
    # Retrieve the user's cart from the session
    if order_uuid == session['order_id']:
      cart = session.get('cart', [])
    else:
      cart = session.get('instant_cart', [])
    # Calculate total price
    total_price = sum(item['new_price'] for item in cart)
    if request.method == 'POST':
        # Get user id
        username = session['username']
        conn = sqlite3.connect(sqldbuser)
        cursor = conn.cursor()
        sqlcommand="Select id from users where username = '"+username+"' or email = '"+username+"'"
        cursor.execute(sqlcommand)
        user_id = int(''.join(map(str, cursor.fetchone())))
        # Save the order
        order = save_order(user_id, order_uuid, total_price, cart)
        # Clear the cart after successful payment
        session['cart'] = []
        session['checkout_success'] = True
        flash('Payment successful. Thank you for your purchase!', 'success')
        return redirect(url_for('success'))
    return render_template('checkout.html', cart=cart, total_price=total_price)

#WISHLIST FEATURE
@app.route('/wishlist')
def view_wishlist():
    wishlist = []
    total_price = 0
    if 'wishlist' in session:
        wishlist = session.get("wishlist", [])
        for item in wishlist:
            total_price += float(item['new_price'])
    if 'username' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    action_msg = session.pop('action_msg', None)
    return render_template(
        "wishlist.html", wishlist=wishlist, total_price=total_price, message=action_msg)

#SAVE ORDER FEATURE
def save_order(user_id, order_uuid, total_price, cart):
    order_date = str(datetime.now())
    table = 'orders'
    order = {
        'user_id': user_id,
        'order_uuid': order_uuid,
        'order_date': order_date,
        'total_price': total_price,
        'cart': cart
    }
    # Save order items (items in the cart) to the database
    for item in cart:
        # Save the order to the database
        order_id = generateID(table) + 1
        game_id = int(item['id'])
        game_title = str(item['title'])
        game_price = int(item['new_price'])
        conn = sqlite3.connect(sqldbuser)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Orders(id, userID, orderUUID, orderDate, orderTotal, gameID, gameName, gamePrice) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (order_id, user_id, order_uuid, order_date, total_price, game_id, game_title, game_price))
        conn.commit()
        conn.close()
    return order

# FUNCTION FOR ADMIN PAGE
# Load data form UserDB
def load_data_from_user(username):
  if username != "":
    # Trỏ tới UserDB
    conn = sqlite3.connect(sqldbuser)
    cursor = conn.cursor()
    sqlcommand = ("Select * from users where username like '%" + username + "%' or username like '%" + username + "%'")
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    conn.close()
    # Kiểm tra xem user có tồn tại không và trả lại dữ liệu
    if len(data) == 0:
      no_user_message = "No user name '" + username + "'"
      return data, no_user_message
    else:
      return data, None
  
# ADMIN PAGE
@app.route("/admin")
def admin():
  if 'username' not in session or not session['logged_in']:
      
      return redirect(url_for('login'))
  return render_template("admin.html")

# Admin Search User
@app.route("/searchUser", methods=['POST'])
def searchUser():
  delete_success = False
  search_user = request.form['SearchUser']
  user_table, output_message = load_data_from_user(search_user)
  return render_template("admin.html", delete_success=delete_success, 
        search_user=search_user,
        table=user_table,
        output_message=output_message if search_user else None
        )

# Delete User from UserDB
def delete_user_from_db(user_id):
  if user_id != "":
    # Trỏ tới UserDB
    conn = sqlite3.connect(sqldbuser)
    cursor = conn.cursor()
    sqlcommand = ("delete from users where id = " + user_id)
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    return "User deleted successfully"

# Load page delete user
@app.route('/deleteUser', methods=['POST'])
def delete_user():
  user_id = request.form['user_id']
  delete_result = delete_user_from_db(user_id)
  delete_success = True
  return render_template("admin.html", delete_success = delete_success)

# SUCCESS PAGE
@app.route('/success', methods=['GET'])
def success():
    # Check if the session variable is set to True (indicating a successful checkout)
    if session.get('checkout_success'):
        # Clear the session variable to avoid showing success on page refresh
        session.pop('checkout_success', None)
        return render_template("success.html")
    else:
        return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(debug=True)