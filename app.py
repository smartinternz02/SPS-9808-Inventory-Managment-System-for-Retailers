from flask import Flask, render_template, redirect, request, url_for, flash, session, Markup
from flask_migrate import Migrate
from flask_login import login_user, login_required, logout_user
from forms import *
from models import User, db, login_manager, Customer, Stock, Cart, Billing
from sqlalchemy import func
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkeyformyappdonttrytohack'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/inventoryapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'rahulprojectmail@gmail.com'
app.config['MAIL_PASSWORD'] = 'Inventory@app1234'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


db.init_app(app)
Migrate(app, db)

login_manager.init_app(app)

login_manager.login_view = "login"


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.errorhandler(404)
@login_required
def page_not_found(e):
    user = session['user']
    return render_template('404.html', user=user), 404


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = User.query.filter_by(email=form.email.data).first()
        if email is None:
            username = User.query.filter_by(username=form.username.data).first()
            if username is None:
                register = User(firstname=form.firstname.data, lastname=form.lastname.data,
                                email=form.email.data, username=form.username.data, password=form.password.data)
                db.session.add(register)
                db.session.commit()
                flash('Congrats you have registered successfully!, Please check your inbox')
                welcome = form.firstname.data + ' ' + form.lastname.data + ' Welcome to Inventory Management System'
                msg = Message(
                    'Welcome',
                    sender='rahulprojectmail@gmail.com',
                    recipients=[form.email.data]
                )
                msg.body = welcome
                mail.send(msg)

                return redirect(url_for('login'))
            else:
                flash('Username already exists, please try again!')
                return redirect(url_for('register'))
        else:
            flash('Email already exists, please try logging in!')
            return redirect(url_for('register'))

    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.check_password(form.password.data):
                session['user'] = form.username.data
                login_user(user)
                next = request.args.get('next')
                if next == None or not next[0] == '/':
                    next = url_for('dashboard')
                return redirect(next)
        flash('Username/password not found!')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    user = session['user']
    heading = 'Dashboard'
    user_name = db.session.query(User.id).filter(User.username == user).first()
    c_rows = db.session.query(Customer).filter_by(user_id=user_name.id).count()
    s_rows = db.session.query(Stock).filter_by(user_id=user_name.id).count()
    final_amount = Billing.query.with_entities(func.sum(Billing.total_amount).label("totalamount")).filter_by(user_id=user_name.id).first()
    totalamt = final_amount.totalamount
    return render_template('dashboard.html', user=user, heading=heading,
                           totalamt=totalamt, c_rows=c_rows, s_rows=s_rows)


@app.route('/inventory')
@login_required
def inventory():
    user = session['user']
    heading = 'Inventory'
    prod_name = db.session.query(User.id).filter(User.username == user).first()
    view_products = Stock.query.filter_by(user_id=prod_name.id)
    return render_template('inventory.html', user=user, heading=heading, view_products=view_products)


@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    form = AddProduct()
    user = session['user']
    heading = 'Add New Product'

    if form.validate_on_submit():
        user_name = db.session.query(User).filter(User.username == user).first()

        item_name = form.item_name.data
        item_price = form.item_price.data
        item_qty = form.item_qty.data
        item = Stock.query.filter_by(item_name=item_name, user_id=user_name.id).first()
        if item:
            flash('Product already exists')
            return redirect(url_for('addproduct'))
        else:
            add_product = Stock(item_name=item_name, item_price=item_price, item_qty=item_qty, user_id=user_name.id)
            db.session.add(add_product)
            db.session.commit()
            flash(Markup('Product added successfully! To view products <a href="/inventory" '
                         'class="alert-link">click here</a>'))
            return redirect(url_for('addproduct'))
    return render_template('addproduct.html', form=form, heading=heading)


@app.route('/updateproduct/<string:id>', methods=['GET', 'POST'])
@login_required
def updateproduct(id):
    user = session['user']
    heading = 'Update Product Details'
    product = Stock.query.filter_by(id=id).one()
    form = AddProduct(obj=product)
    if form.validate_on_submit():
        product = Stock.query.get(id)
        form.populate_obj(product)
        db.session.commit()
        flash('Product details updated Successfully')
        return redirect(url_for('inventory'))
    return render_template('addproduct.html', form=form,  user=user, heading=heading)


@app.route('/deleteproduct/<string:id>')
@login_required
def deleteproduct(id):
    Stock.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Product has been deleted!')
    return redirect(url_for('inventory'))


@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    heading = 'Customers'
    user = session['user']
    user_name = db.session.query(User.id).filter(User.username == user).first()
    view_customers = Customer.query.filter_by(user_id=user_name.id)
    return render_template('customers.html', view_customers=view_customers, user=user, heading=heading)


@app.route('/addcustomer', methods=['GET', 'POST'])
@login_required
def addcustomer():
    form = AddCustomer()
    user = session['user']
    heading = 'Add New Customer'

    if form.validate_on_submit():
        user_name = db.session.query(User).filter(User.username == user).first()

        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        address = form.address.data
        customer = Customer.query.filter_by(email=email, user_id=user_name.id).first()
        if customer:
            flash(Markup('Customer already exists'))
            return redirect(url_for('addcustomer'))
        else:
            add_customer = Customer(firstname=firstname, lastname=lastname, email=email, address=address,
                                    user_id=user_name.id)
            db.session.add(add_customer)
            db.session.commit()
            flash(Markup('Customer added successfully! To view customerss <a href="/customers" class="alert-link">'
                         'click here</a>'))
            return redirect(url_for('addcustomer'))
    return render_template('addcustomer.html', form=form, user=user, heading=heading)


@app.route('/updatecustomer/<string:id>', methods=['GET', 'POST'])
@login_required
def updatecustomer(id):
    user = session['user']
    heading = 'Add New Customer'
    customer = Customer.query.filter_by(id=id).one()
    form = AddCustomer(obj=customer)
    if form.validate_on_submit():
        customer = Customer.query.get(id)
        form.populate_obj(customer)
        db.session.commit()
        flash('Customer details updated Successfully')
        return redirect(url_for('customers'))
    return render_template('addcustomer.html', form=form, user=user, heading=heading)


@app.route('/deletecustomer/<string:id>')
@login_required
def deletecustomer(id):
    Customer.query.filter_by(id=id).delete()
    db.session.commit()
    flash('Customer has been deleted!')
    return redirect(url_for('customers'))


@app.route('/invoices')
@login_required
def invoices():
    user = session['user']
    heading = 'Invoices'
    user_name = db.session.query(User.id).filter(User.username == user).first()
    view_customers = Customer.query.filter_by(user_id=user_name.id).all()
    return render_template('invoices.html', user=user, heading=heading, view_customers=view_customers)


@app.route('/billing/<string:id>', methods=['GET', 'POST'])
@login_required
def billing(id):
    user = session['user']
    user_name = db.session.query(User.id).filter(User.username == user).first()
    final_amount = Cart.query.with_entities(func.sum(Cart.total_amount).label("totalamount")).filter_by(customer_id=id).first()

    totalamt = final_amount.totalamount
    if totalamt is None:
        flash('Invoice is Empty! Click on Create Bill to create new one!')
        return redirect(url_for('customers'))
    else:
        customer_name = db.session.query(Customer.email).filter(Customer.id == id).first()
        bill = Billing(customer_name=customer_name[0], total_amount=totalamt, user_id=user_name.id)
        db.session.add(bill)

        Cart.query.filter_by(customer_id=id).delete()

        db.session.commit()
        emailid = customer_name[0]
        msg = Message(
            'Bill Generated',
            sender='rahulprojectmail@gmail.com',
            recipients=[emailid]
        )
        msg.body = 'Your bill amount is: ' + str(totalamt)
        mail.send(msg)

        # flash('Bill has been generated!!')

        return render_template('billing.html', cost=totalamt, customer_name=customer_name[0], user=user)


@app.route('/reports')
@login_required
def reports():
    user = session['user']
    heading = 'Reports'
    user_name = db.session.query(User.id).filter(User.username == user).first()
    view_bill = Billing.query.filter_by(user_id=user_name.id).all()
    final_amount = Billing.query.with_entities(func.sum(Billing.total_amount).label("totalamount")).filter_by(user_id=user_name.id).first()
    totalamt = final_amount.totalamount
    return render_template('reports.html', user=user, heading=heading, view_bill=view_bill, totalamt=totalamt)

@app.route('/profile', methods=['GET','Post'])
@login_required
def profile():
    # form = RegistrationForm()
    user = session['user']
    heading = 'Profile'
    user_id = db.session.query(User.id).filter(User.username == user).first()	
    user_name = User.query.filter_by(username=user).one()
    # user = Customer.query.filter_by(id=id).one()
    form = ProfileForm(obj=user_name)
    if form.validate_on_submit():
        user_name = User.query.get(user_id)
        form.populate_obj(user_name)
        db.session.commit()
        flash('Customer details updated Successfully')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user, heading=heading, form=form)


@app.route('/viewbill/<string:id>')
@login_required
def viewbill(id):
    user = session['user']
    view_bill = Cart.query.filter_by(customer_id=id).all()
    final_amount = Cart.query.with_entities(func.sum(Cart.total_amount).label("totalamount")).filter_by(customer_id=id).first()
    totalamt = final_amount.totalamount
    if totalamt is None:
        flash('Invoice is Empty!')
        return redirect(url_for('invoices'))
    else:
        for customern in view_bill:
            customerr = customern.customer_name
            return render_template('viewbill.html', view_bill=view_bill, totalamt=totalamt, id=id, user=user, customerr=customerr)


@app.route('/createinvoice/<string:id>', methods=['GET', 'POST'])
@login_required
def createinvoice(id):
    user = session['user']
    form = InvoiceForm()
    customer_fname = db.session.query(Customer.firstname).filter(Customer.id == id).first()
    customer_lname = db.session.query(Customer.lastname).filter(Customer.id == id).first()

    user_name = db.session.query(User.id).filter(User.username == user).first()
    view_products = Stock.query.filter_by(user_id=user_name.id).all()
    form.products.choices = [(products.id, products.item_name) for products in view_products]

    final_amount = Cart.query.with_entities(func.sum(Cart.total_amount).label("totalamount")).filter_by(
        customer_id=id).first()
    totalamt = final_amount.totalamount

    if form.validate_on_submit():
        customer_name = db.session.query(Customer.email).filter(Customer.id == id).first()
        s_products = form.products.data
        product_name = db.session.query(Stock.item_name).filter(Stock.id == s_products).first()

        items = Stock.query.filter_by(id=s_products).first()

        quantity = form.item_qty.data
        if quantity > items.item_qty:
            flash('Not enough stock available of selected product!!')
            return render_template('createinvoice.html', form=form, customer_fname=customer_fname[0],
                                   customer_lname=customer_lname[0], id=id, user=user)
        else:
            product_price = db.session.query(Stock.item_price).filter(Stock.id == s_products).first()

            total = int(quantity) * int(product_price[0])

            invoice = Cart(customer_name=customer_name[0], item_name=product_name[0], item_price=product_price[0],
                              item_quantity=quantity, total_amount=total, user_id=user_name.id, customer_id=id)
            db.session.add(invoice)

            product_quantity = db.session.query(Stock.item_qty).filter(Stock.id == s_products).first()
            available_quantity = product_quantity[0] - quantity

            items.item_qty = available_quantity

            db.session.commit()
            flash('Product added to Cart Successfully!!!')

            user_email = db.session.query(User.email).filter(User.username == user).first()
            useremail = user_email[0]

            if available_quantity < 10:

                prod_name = db.session.query(Stock.item_name).filter(Stock.id == s_products).first()
                flash('Available quantity is less than 10. Total available quantity is: '+ str(available_quantity))
                quantity_alert = 'You will soon run out of quantity of product: ' \
                                 + prod_name[0] + '\nPlease update your stock as soon as possible'
                msg = Message(
                    'Quantity Alert',
                    sender='rahulprojectmail@gmail.com',
                    recipients=[useremail]
                )
                msg.body = quantity_alert
                mail.send(msg)


            final_amt = Cart.query.with_entities(func.sum(Cart.total_amount).label("totalamount")).filter_by(
                customer_id=id).first()
            totalamtn = final_amt.totalamount

            view_bill = Cart.query.filter_by(customer_id=id).all()

            for customern in view_bill:
                customerr = customern.customer_name
                return render_template('createinvoice.html', form=form, customerr=customerr, totalamt=totalamt,
                                       view_bill=view_bill, customer_fname=customer_fname[0],
                                       customer_lname=customer_lname[0], totalamtn=totalamtn, id=id, user=user)
    return render_template('createinvoice.html', view_products=view_products, form=form,
                           customer_fname=customer_fname[0], customer_lname=customer_lname[0],
                           totalamt=totalamt, id=id, user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
