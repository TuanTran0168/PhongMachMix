from flask import session, render_template, request, redirect
from saleapp import app, dao, admin, login, utils, controllers
from flask_login import current_user

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
    if request.method == ('POST'):
        SDT_dang_ky_kham = request.form['user_dang_ky_kham']

        benh_nhan = dao.load_users_by_phone_number(SDT_dang_ky_kham)
        if benh_nhan:
            benh_nhan_da_dang_ky = dao.load_chi_tiet_danh_sach_kham_today(benh_nhan[0][0])

            # Nếu bệnh nhân có lịch sử bệnh rồi thì khôg tạo nữa
            # load lịch sử bệnh lên kiểm tra bằng id user
            if benh_nhan_da_dang_ky:
                err_msg = "Bạn đã đăng ký rồi"
            else:
                ngay_kham = dao.load_danh_sach_kham_by_today()
                if ngay_kham:
                    dao.save_chi_tiet_danh_sach_kham(ngay_kham[0][0], benh_nhan[0][0])
                    err_msg = 'Đăng ký thành công'
                    lsb_for_one_user = dao.load_lich_su_benh(user_id=benh_nhan[0][0])
                    if lsb_for_one_user:
                        pass
                        # err_msg = "Lịch sử bệnh đã tồn tại"
                    else:
                        dao.create_lich_su_benh(user_id=benh_nhan[0][0])
                else:
                    err_msg = "Chưa có danh sách để đăng ký"
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
        if danh_sach_kham_hom_nay:  # có danh sách rồi
            err_msg = "Đã tạo danh sách khám cho hôm nay rồi"
        else:
            create_list = request.form['create_list']
            dao.create_danh_sach_kham(create_list)
            return redirect('/nurse')
    return render_template("nurse.html", err_msg=err_msg)


@app.route("/save_chi_tiet_danh_sach_kham", methods=['get', 'post'])  # đường dẫn chứa cái trang cần lấy data
def save_chi_tiet_danh_sach_kham():  # cái action của form sẽ có tên như này
    err_msg = ''
    if request.method == ('POST'):
        get_user_in_danh_sach_kham = []
        dsk = dao.load_DSK_today()
        if dsk:
            chi_tiet_dsk = dao.load_chi_tiet_DSK_today(dsk[0][0])
            if chi_tiet_dsk:
                n = len(chi_tiet_dsk)
                for i in range(0, n):
                    pk_today_for_one_user = dao.load_phieu_kham(user_id=chi_tiet_dsk[i][2])
                    if pk_today_for_one_user:
                        err_msg = "Đã tạo phiếu cho user này rồi"
                    else:
                        pk = dao.create_phieu_kham_auto(user_id=chi_tiet_dsk[i][2])
                        err_msg = "Tạo thành công phiếu khám"
            else:
                err_msg = "Chưa có bệnh nhân nào đăng ký khám"


        save_chi_tiet_dsk = request.form['save_chi_tiet_dsk']  # Lấy này test coi bấm đc k

    return render_template("nurse.html", err_msg=err_msg)


# biến toàn cục mà sao không xài được :)))))
user_id_in_phieu_kham = 0
ma_phieu_kham_today = 0
@app.route("/doctor_get_user_by_user_id", methods=['get', 'post'])  # đường dẫn chứa cái trang cần lấy data
def doctor_get_user_by_user_id():  # cái action của form sẽ có tên như này
    err_msg = ''
    if request.method == ('POST'):
        user_id = request.form["doctor_get_user_by_user_id"]  # Lấy id user bằng nhập trên web
        phieu_kham_da_duoc_tao = dao.load_phieu_kham(user_id)
        if phieu_kham_da_duoc_tao:

            pk_today_for_one_user = dao.load_phieu_kham_today_by_user_id(user_id)  # tìm phiếu khám của user đó
            global ma_phieu_kham_today
            ma_phieu_kham_today = pk_today_for_one_user[0][0]
            if pk_today_for_one_user:
                global user_id_in_phieu_kham
                user_id_in_phieu_kham = pk_today_for_one_user[0][5]  # Lấy id của user trong phiếu đó
                user_in_phieu_kham = dao.load_users_by_user_id(user_id_in_phieu_kham)  # Lấy user trong phiếu đó
                # LƯU THUỐC CHO BỆNH NHÂN
                if user_in_phieu_kham:
                    ten_thuoc = request.form["medicine"]
                    so_luong_thuoc = request.form["so_luong_thuoc"]
                    thuoc = dao.load_medicines_by_name(ten_thuoc)
                    if thuoc:
                        dao.save_chi_tiet_phieu_kham(so_luong_thuoc=so_luong_thuoc, thuoc_id=thuoc[0][0],
                                                     phieu_kham_id=pk_today_for_one_user[0][0])

                        # return so_luong_thuoc
                        return redirect("/doctor")
                    else:
                        err_msg = "Không có thuốc này trong cơ sở dữ liệu"
                else:
                    err_msg = "Bệnh nhân này không có phiếu khám"
            else:
                err_msg = "Không tìm được mã bệnh nhân trong danh sách các phiếu khám"
        else:
            err_msg = "Phiếu khám chưa được tạo"
    return render_template("doctor.html", err_msg=err_msg)

@app.context_processor
def load_users_by_user_id_view():
    user_id_view = dao.load_users_by_user_id(user_id_in_phieu_kham)
    return {
        "user_id_view": user_id_view
    }
@app.context_processor
def load_thuoc_trong_chi_tiet_pk():
    thuoc_trong_ctpk = dao.load_thuoc_in_chi_tiet_phieu_kham_today(
        user_id_in_phieu_kham)  # Không xài đc id lấy ở trên (user_id_in_phieu_kham)
    return {
        'thuoc_trong_ctpk': thuoc_trong_ctpk
    }


# Hàm này lưu luôn lịch sử bệnh
@app.route("/doctor_save_phieu_kham", methods=['get', 'post'])
def doctor_save_phieu_kham():
    err_msg = ''

    if request.method == ('POST'):
        phieu_kham_id = ""
        check_pk_id_numString = ""
        check_pk_id = ""
        # phieu_kham_id = request.form["ma_phieu_kham"]
        phieu_kham_id = ma_phieu_kham_today
        check_pk_id = dao.load_phieu_kham_id_today_by_phieu_kham_id(phieu_kham_id=phieu_kham_id)

        # return err_msg
        if check_pk_id:
            check_pk_id_numString = str(check_pk_id[0][0])
            trieu_chung = request.form["trieu_chung"]
            chuan_doan = request.form["chuan_doan"]
            if trieu_chung and chuan_doan:
                dao.update_phieu_kham(phieu_kham_id=check_pk_id_numString, trieu_chung=trieu_chung, chuan_doan=chuan_doan)
                benh_id = dao.load_benh_id_by_ten_benh(chuan_doan)
                lsb_id = dao.load_lich_su_benh_id_by_phieu_kham_id(check_pk_id_numString)

                dao.save_chi_tiet_lich_su_benh(lich_su_benh_id=lsb_id[0][0], benh_id=benh_id[0][0])
                err_msg = "Lưu thành công phiếu khám có mã phiếu là " + check_pk_id_numString
            else:
                err_msg = "Chưa nhập chuẩn đoán và triệu chứng"
        else:
            err_msg = "Không tồn tại phiếu khám này"
    return render_template("doctor.html", err_msg=err_msg)


# @app.route("/doctor_get_user_by_user_id", methods=['get', 'post'])  # đường dẫn chứa cái trang cần lấy data
# def doctor_get_user_by_user_id():  # cái action của form sẽ có tên như này
#     err_msg = ''
#     if request.method == ('POST'):
#         doctor_get_user_by_user_id = request.form["doctor_get_user_by_user_id"]
#         user_in_phieu_kham = dao.load_phieu_kham(doctor_get_user_by_user_id)
#         if user_in_phieu_kham:
#             return redirect("/doctor")
#             # return user_in_phieu_kham[0][6]
#         else:
#             err_msg = "Bệnh nhân này không có phiếu khám"
#     return render_template("doctor.html", err_msg=err_msg, user_in_phieu_kham=user_in_phieu_kham)

@app.context_processor
def load_medicines():
    medicines = dao.load_medicines()
    return {
        'medicines': medicines
    }


@app.context_processor
def load_phieu_kham():
    phieu_kham = dao.load_phieu_kham()
    return {
        'phieu_kham': phieu_kham
    }

user_id_in_hoa_don_for_one_user = 0
@app.route("/cashier", methods=['get', 'post'])
def cashier():
    # xử lý
    err_msg = ''
    hd = ""
    # nhập id của phieuKham
    if request.method == ('POST'):
        phieuKham_id = request.form['submit_phieuKham_id']
        check_pk_id = dao.load_phieu_kham_id_today_by_phieu_kham_id(phieu_kham_id=phieuKham_id)
        if check_pk_id:
            global user_id_in_hoa_don_for_one_user
            user_id_in_hoa_don_for_one_user = phieuKham_id
            phieu_kham = dao.load_medical_form_for_one_user_by_phieuKham_id(phieuKham_id)
            bill_cua_user = dao.bill_for_one_user_by_id(phieu_kham[0][5])
            tien_kham = 100000
            tien_thuoc = bill_cua_user[4] + tien_kham
            dao.save_bill_for_user(phieu_kham[0][2], tien_thuoc, phieu_kham[0][5])
            err_msg = "Thanh toán thành công"
        else:
            err_msg = "Không tồn tại phiếu khám này"
        # hd = dao.load_hoa_don_by_phieu_kham_id(phieuKham_id)
        # return redirect('/cashier')

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
    get_user_in_danh_sach_kham = []
    dsk = dao.load_DSK_today()
    if dsk:
        user_id_in_dsk = dao.load_chi_tiet_DSK_today(dsk[0][0])
        n = len(user_id_in_dsk)

        # get_user_in_danh_sach_kham = dao.load_users_by_user_id(b[0][2])
        # get_user_in_danh_sach_kham = dao.load_users_by_user_id(b[1][2])
        for i in range(0, n):
            get_user_in_danh_sach_kham.append(dao.load_users_by_user_id(user_id_in_dsk[i][2]))

    return {
        'get_user_in_danh_sach_kham': get_user_in_danh_sach_kham
    }





@app.context_processor
def load_hoa_don():
    danh_sach_hoa_don = dao.load_hoa_don()
    return {
        "danh_sach_hoa_don": danh_sach_hoa_don
    }

@app.context_processor
def load_hoa_don_for_one_user():
    hoa_don = dao.load_hoa_don_by_phieu_kham_id(user_id_in_hoa_don_for_one_user)  # Bỏ user_id dô là lọc đc lsb của user đó nhưng vì không biết truyền biến kiểu gì nên thôi load hết
    return {
        "hoa_don": hoa_don
    }

user_id_in_lich_su_benh_after_filter = 0
@app.route("/lay_ma_benh_nhan_xem_lich_su_benh", methods=['get', 'post'])
def lay_ma_benh_nhan_xem_lich_su_benh():
    # xử lý
    err_msg = ''
    # nhập id của phieuKham
    if request.method == ('POST'):
        id_benh_nhan = request.form["id_benh_nhan"]
        #dùng id lấy lịch sử bệnh lên, nếu có thì mới làm
        lich_su_benh_for_one_user = dao.load_lich_su_benh_in_view(id_benh_nhan)
        # return str(lich_su_benh_for_one_user[0][1])
        if lich_su_benh_for_one_user:
            global user_id_in_lich_su_benh_after_filter
            user_id_in_lich_su_benh_after_filter = lich_su_benh_for_one_user[0][1]
        else:
            err_msg = "Không tồn tại bệnh nhân này"

    return render_template("lich_su_benh.html", err_msg=err_msg)

@app.route("/lich_su_benh")
def lich_su_benh():
    if current_user.is_authenticated:
        lsb_for_crr = dao.load_lich_su_benh_in_view(current_user.id)
    return render_template("lich_su_benh.html", lsb_for_crr=lsb_for_crr)

# @app.route("/lich_su_benh")
# def load_lich_su_benh():
#     load_lich_su_benh_in_view = dao.load_lich_su_benh_in_view(user_id_in_lich_su_benh_after_filter)
#     if load_lich_su_benh_in_view:
#         return load_lich_su_benh_in_view
#
#     return render_template("lich_su_benh.html", load_lich_su_benh_in_view=load_lich_su_benh_in_view)

@app.context_processor
def load_lich_su_benh():
    load_lich_su_benh_in_view = dao.load_lich_su_benh_in_view(user_id_in_lich_su_benh_after_filter)

    return {
        "load_lich_su_benh_in_view": load_lich_su_benh_in_view
    }

if __name__ == '__main__':
    app.run(debug=True)
