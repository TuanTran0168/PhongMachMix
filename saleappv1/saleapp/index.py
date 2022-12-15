from flask import session, render_template, request, redirect
from saleapp import app, dao, admin, login, utils, controllers


app.add_url_rule('/', 'index', controllers.index)
app.add_url_rule('/products/<int:product_id>', 'product-detail', controllers.details)
app.add_url_rule('/login-admin', 'login-admin', controllers.login_admin, methods=['post'])
app.add_url_rule('/login', 'login-user', controllers.login_my_user, methods=['get', 'post'])
app.add_url_rule('/logout', 'logout', controllers.logout_my_user)
app.add_url_rule('/register', 'register', controllers.register, methods=['get', 'post'])
app.add_url_rule('/cart', 'cart', controllers.cart)
app.add_url_rule('/api/cart', 'add-cart', controllers.add_to_cart, methods=['post'])
app.add_url_rule('/api/cart/<product_id>', 'update-cart', controllers.update_cart, methods=['put'])
app.add_url_rule('/api/cart/<product_id>', 'delete-cart', controllers.delete_cart, methods=['delete'])
app.add_url_rule('/api/pay', 'pay', controllers.pay)
app.add_url_rule('/api/products/<int:product_id>/comments', 'comments', controllers.comments)
app.add_url_rule('/api/products/<int:product_id>/comments', 'add-comment', controllers.add_comment, methods=['post'])

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

@app.route("/nurse")
def nurse():
    return render_template("nurse.html")

@app.route("/cashier", methods=['get', 'post'])
def cashier():
    # xử lý
    err_msg = ''
    # nhập id của phieuKham
    if request.method == ('POST'):
        phieuKham_id = request.form['submit_phieuKham_id']
        # truy vấn user ở db lên
        # list_phieu_kham = dao.load_medical_form_today()
        # for pk in list_phieu_kham:
        #     if phieuKham_id.__eq__(pk[0]):
        #         bill_cua_user = dao.bill_for_one_user_by_id(pk[5])
        #         dao.save_bill_for_user(pk[1], pk[2], bill_cua_user[0], pk[5])
        phieu_kham = dao.load_medical_form_for_one_user_today_by_phieuKham_id(phieuKham_id)
        bill_cua_user = dao.bill_for_one_user_by_id(phieu_kham[0][5])
        dao.save_bill_for_user(phieu_kham[0][1], phieu_kham[0][2], bill_cua_user[4], phieu_kham[0][5])
        return redirect('/cashier')

    return render_template("cashier.html", err_msg=err_msg)

@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


@app.context_processor
def common_attribute():
    categories = dao.load_categories()
    return {
        'categories': categories,
        'cart': utils.cart_stats(session.get(app.config['CART_KEY']))
    }

@app.context_processor
def get_disease():
    diseases = dao.load_diseases()
    return {
        'diseases': diseases
    }


if __name__ == '__main__':
    app.run(debug=True)
