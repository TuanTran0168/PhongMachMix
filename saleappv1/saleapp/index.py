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

@app.route("/user_dang_ky_kham", methods=['get', 'post'])  # đường dẫn chứa cái trang cần lấy data
def user_dang_ky_kham():
    err_msg = ''
    # if request.method == ('POST'):
    SDT_dang_ky_kham = request.form['user_dang_ky_kham']
    benh_nhan = dao.load_users_by_phone_number(SDT_dang_ky_kham)
    if benh_nhan:
        ngay_kham = dao.load_danh_sach_kham_by_today()
        dao.save_chi_tiet_danh_sach_kham(ngay_kham[0][0], benh_nhan[0][0])
    else:
        err_msg = "Không tồn tại user trong cơ sở dữ liệu"
    return render_template("index.html", err_msg=err_msg)

@app.route("/create_danh_sach_kham_for_nurse", methods=['get', 'post'])  # đường dẫn chứa cái trang cần lấy data
def create_danh_sach_kham_for_nurse():  # cái action của form sẽ có tên như này
    err_msg = ''
    if request.method == ('POST'):
        # danh_sach_kham = dao.load_danh_sach_kham()
        # ngay_khamString = str(danh_sach_kham[0][2])
        # today = datetime.now()
        # todayString = str(today)
        # if ngay_khamString.__eq__(todayString):

        danh_sach_kham_hom_nay = dao.load_danh_sach_kham_by_today()
        if danh_sach_kham_hom_nay: #có danh sách rồi
            err_msg = "Đã tạo rồi"
        else:
            create_list = request.form['create_list']
            dao.create_danh_sach_kham(create_list)
            return redirect('/nurse')
    return render_template("nurse.html", err_msg=err_msg)

@app.route("/save_chi_tiet_danh_sach_kham", methods=['get', 'post'])  # đường dẫn chứa cái trang cần lấy data
def save_chi_tiet_danh_sach_kham():  # cái action của form sẽ có tên như này
    err_msg = ''
    if request.method == ('POST'):
        save_chi_tiet_dsk = request.form['save_chi_tiet_dsk']
        return save_chi_tiet_dsk
    return render_template("nurse.html", err_msg=err_msg)

@app.route("/nurse", methods=['get', 'post'])  # đường dẫn chứa cái trang cần lấy data
def xac_nhan_danh_sach_kham_by_nurse():
    pass


@app.route("/cashier", methods=['get', 'post'])
def cashier():
    # xử lý
    err_msg = ''
    # nhập id của phieuKham
    if request.method == ('POST'):
        phieuKham_id = request.form['submit_phieuKham_id']
        phieu_kham = dao.load_medical_form_for_one_user_by_phieuKham_id(phieuKham_id)
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

@app.context_processor
def get_danh_sach_kham():
    danh_sach_kham = dao.load_danh_sach_kham()
    return {
        'danh_sach_kham': danh_sach_kham
    }

@app.context_processor
def get_user_in_danh_sach_kham():
    get_user_in_danh_sach_kham = dao.get_user_in_danh_sach_kham()
    return {
        'get_user_in_danh_sach_kham': get_user_in_danh_sach_kham
    }

@app.context_processor
def get_user_in_danh_sach_kham():
    a = dao.load_DSK_today()
    b = dao.load_chi_tiet_DSK_today(a[0][0])
    n = len(b)
    get_user_in_danh_sach_kham = []
    for i in range(0, n):
        get_user_in_danh_sach_kham.append(dao.load_users_by_user_id(b[i][2]))
    # get_user_in_danh_sach_kham = dao.load_users_by_user_id(b[0][2])
    # get_user_in_danh_sach_kham = dao.load_users_by_user_id(b[1][2])
    return {
        'get_user_in_danh_sach_kham': get_user_in_danh_sach_kham
    }



if __name__ == '__main__':
    app.run(debug=True)
