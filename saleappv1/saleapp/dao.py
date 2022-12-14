from saleapp.models import *
from saleapp import db
from flask_login import current_user
from sqlalchemy import func
import hashlib


def load_diseases():
    return Benh.query.all()


def load_categories():
    return DanhMucThuoc.query.all()


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

    # return db.session.query(User.tenUser, func.count(User.user_role == UserRole.USER),
    #                         func.count(User.user_role == UserRole.CASHIER), \
    #                         func.count(User.user_role == UserRole.NURSE), \
    #                         func.count(User.user_role == UserRole.DOCTOR), \
    #                         func.count(User.user_role == UserRole.ADMIN)).group_by(User.tenUser).all()


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
        print(stats_by_medic())
        print(count_user())
        print(stats_by_revenue())
        a = stats_by_medic()

        print(type(int(a[0][3])))
        # print(count_user_by_role(UserRole.USER))
        # print(count_user_by_role(UserRole.ADMIN))
        # print(count_user_by_role(UserRole.DOCTOR))
