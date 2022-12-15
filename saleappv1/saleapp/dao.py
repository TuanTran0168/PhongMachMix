from saleapp.models import *
from saleapp import db
from flask_login import current_user
from sqlalchemy import func
import hashlib


def load_diseases():
    return Benh.query.all()

def load_categories():
    return DanhMucThuoc.query.all()

def load_users():
    return User.query.all()


def load_products(danhMucThuoc_id=None, kw=None):
    query = Thuoc.query.filter(Thuoc.trangThai.__eq__(True))

    if danhMucThuoc_id:
        query = query.filter(Thuoc.danhMucThuoc_id.__eq__(danhMucThuoc_id))

    if kw:
        query = query.filter(Thuoc.tenThuoc.contains(kw))

    return query.all()


def get_product_by_id(product_id):
    return Thuoc.query.get(product_id)


def auth_user(username, password):
    # password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    return User.query.filter(User.tenDangNhap.__eq__(username.strip()),
                             User.matKhau.__eq__(password)).first()


def register(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(tenUser=name, tenDangNhap=username.strip(), matKhau=password, anhDaiDien=avatar)
    db.session.add(u)
    db.session.commit()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_receipt(cart):
    if cart:
        r = PhieuKham(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = ChiTietPhieuKham(quantity=c['quantity'], price=c['price'],
                                 receipt=r, product_id=c['id'])
            db.session.add(d)

        db.session.commit()


def count_product_by_cate():
    return db.session.query(DanhMucThuoc.id, DanhMucThuoc.tenDanhMuc, func.count(Thuoc.id)) \
        .join(Thuoc, Thuoc.danhMucThuoc_id.__eq__(DanhMucThuoc.id), isouter=True) \
        .group_by(DanhMucThuoc.id).order_by(-DanhMucThuoc.tenDanhMuc).all()


def count_user_by_role(userRoleStats):
    if userRoleStats:
        count = 0
        for r1 in userRoleStats.values():
            for r2 in userRoleStats.values():
                if r1.__eq__(r2):
                    count = count + 1
    return count


def count_user():
    return db.session.query(User.user_role, func.count(User.id)).group_by(User.user_role).all()


def stats_revenue_by_user(kw=None, from_date=None, to_date=None):
    query = db.session.query(User.tenUser, PhieuKham.ngayKham, func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
        .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id)) \
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id))

    if kw:
        query = query.filter(Thuoc.tenThuoc.contains(kw))

    if from_date:
        query = query.filter(PhieuKham.ngayKham.__ge__(from_date))

    if to_date:
        query = query.filter(PhieuKham.ngayKham.__le__(to_date))

    return query.group_by(User.tenUser, PhieuKham.ngayKham).all()


# def stats_revenue_by_prod(kw=None, from_date=None, to_date=None):
#     query = db.session.query(PhieuKham.ngayKham, func.count(ChiTietDanhSachKham.id),  \
#                              func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
#         .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id), isouter=True)
#
#     if kw:
#         query = query.filter(Thuoc.tenThuoc.contains(kw))
#
#     if from_date:
#         query = query.filter(PhieuKham.ngayKham.__ge__(from_date))
#
#     if to_date:
#         query = query.filter(PhieuKham.ngayKham.__le__(to_date))
#
#     return query.group_by(Thuoc.id, ChiTietPhieuKham.soLuongThuoc ).order_by(Thuoc.id).all()

# Bản gốc của thống kê báo cáo thuốc
# def stats_by_medic(kw=None, from_date=None, to_date=None):
#     query = db.session.query(Thuoc.id, Thuoc.tenThuoc, Thuoc.donViThuoc, ChiTietPhieuKham.soLuongThuoc,
#                              ChiTietPhieuKham.phieuKham_id, \
#                              func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc)) \
#         .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id), isouter=True)
#
#     if kw:
#         query = query.filter(Thuoc.tenThuoc.contains(kw))
#
#     if from_date:
#         query = query.filter(PhieuKham.ngayKham.__ge__(from_date))
#
#     if to_date:
#         query = query.filter(PhieuKham.ngayKham.__le__(to_date))
#
#     return query.group_by(Thuoc.id, ChiTietPhieuKham.phieuKham_id, ChiTietPhieuKham.soLuongThuoc).order_by(
#         ChiTietPhieuKham.phieuKham_id, Thuoc.id).all()

# Hàng thử nghiệm của thống kê báo cáo thuốc (Thành công, thành hàng real)
def stats_by_medic(kw=None, from_date=None, to_date=None):
    query = db.session.query(Thuoc.id, Thuoc.tenThuoc, Thuoc.donViThuoc,
                             func.sum(ChiTietPhieuKham.soLuongThuoc)) \
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id), isouter=True)

    if kw:
        query = query.filter(Thuoc.tenThuoc.contains(kw))

    if from_date:
        query = query.filter(PhieuKham.ngayKham.__ge__(from_date))

    if to_date:
        query = query.filter(PhieuKham.ngayKham.__le__(to_date))

    return query.group_by(Thuoc.id).order_by(-Thuoc.id).all()


# Ngày, số bệnh nhân, doanh thu
# Tên bệnh nhân, số tiền
def stats_by_revenue(month=None):
    # HoaDon, User
    query = db.session.query(HoaDon.ngayKham, func.count(User.id), func.sum(HoaDon.tongTien)).join(HoaDon,
                                                                                                   HoaDon.user_id.__eq__(
                                                                                                       User.id))
    if month:
        query = query.filter(HoaDon.ngayKham.contains(month))

    return query.group_by(HoaDon.ngayKham).all()

#Bản gốc của tính hóa đơn
# def bill():
#     query = db.session.query(PhieuKham.id,func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc) ) \
#         .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id))\
#         .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id))
#
#     return query.group_by(PhieuKham.id).order_by(PhieuKham.id).all()


#Bản mới của tính hóa đơn (Xịn hơn, Xài cái này) | Bill này tính toàn bộ bill luôn
def bill():
    query = db.session.query(User.id, User.tenUser, PhieuKham.id, PhieuKham.user_id, func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc) ) \
        .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id))\
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id))\
        .join(User, User.id.__eq__(PhieuKham.user_id))

    return query.group_by(User.id, PhieuKham.id).order_by(User.id, PhieuKham.id).all()

def bill_for_one_user_by_id(user_id):
    query = db.session.query(User.id, User.tenUser, PhieuKham.id, PhieuKham.user_id, func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc) ) \
        .join(PhieuKham, PhieuKham.id.__eq__(ChiTietPhieuKham.phieuKham_id))\
        .join(Thuoc, Thuoc.id.__eq__(ChiTietPhieuKham.Thuoc_id))\
        .join(User, User.id.__eq__(PhieuKham.user_id))

    query = query.filter(User.id.__eq__(user_id))

    return query.group_by(User.id, PhieuKham.id).first()

def save_bill_for_user(tenHoaDon, ngayKham, tongTien, user_id):
    b = HoaDon(tenHoaDon = tenHoaDon, ngayKham = ngayKham, tongTien = tongTien, user_id = user_id)
    db.session.add(b)
    db.session.commit()

def load_medical_form_today():
    d = datetime.now()
    s = str(d)[5:10]

    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung, PhieuKham.chuanDoan, PhieuKham.user_id)
    query = query.filter(PhieuKham.ngayKham.contains(s))
    return query.all()

def load_medical_form_for_one_user_today_by_phieuKham_id(phieuKham_id):
    d = datetime.now()
    s = str(d)[5:10]

    query = db.session.query(PhieuKham.id, PhieuKham.tenPhieuKham, PhieuKham.ngayKham, PhieuKham.trieuChung, PhieuKham.chuanDoan, PhieuKham.user_id)
    # query = query.filter(PhieuKham.ngayKham.contains(s))
    query = query.filter(PhieuKham.id.__eq__(phieuKham_id))
    return query.all()

# return User.query.filter(User.tenDangNhap.__eq__(username.strip()),
#                              User.matKhau.__eq__(password)).first()

# def bill():
#     query = db.session.query(PhieuKham.id, func.sum(func.sum(ChiTietPhieuKham.soLuongThuoc * Thuoc.giaThuoc))) \
#         .join(ChiTietPhieuKham, ChiTietPhieuKham.Thuoc_id.__eq__(Thuoc.id)) \
#         .join(ChiTietPhieuKham, ChiTietPhieuKham.phieuKham_id.__eq__(PhieuKham.id))\
#
#     return query.group_by(PhieuKham.id).order_by(PhieuKham.id).all()


def load_comments(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).all()


def save_comment(product_id, content):
    c = Comment(content=content, product_id=product_id, user=current_user)
    db.session.add(c)
    db.session.commit()

    return c


if __name__ == '__main__':
    from saleapp import app

    with app.app_context():
        # print(stats_by_medic())
        # print(count_user())
        # print(stats_by_revenue())
        # b = stats_by_revenue()
        # print(type(b[0][2]))

        # print(bill())
        # print(load_medical_form_today())
        # print(bill_for_one_user_by_id("5"))
        a = load_medical_form_for_one_user_today_by_phieuKham_id(1)
        print(a[0][5])
        print(a)
        # a = stats_by_medic()
        #
        # print(type(int(a[0][3])))
        # print(count_user_by_role(UserRole.USER))
        # print(count_user_by_role(UserRole.ADMIN))
        # print(count_user_by_role(UserRole.DOCTOR))
