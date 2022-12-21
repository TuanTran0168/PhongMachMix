import json

from saleapp import db, app, dao
from saleapp.models import *
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, request, render_template
from flask_login import logout_user, current_user
from wtforms import TextAreaField
from wtforms.widgets import TextArea


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')

        return super().__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class ProductView(AuthenticatedModelView):
    column_searchable_list = ['name', 'description']
    column_filters = ['name', 'price']
    can_view_details = True
    column_exclude_list = ['image', 'description']
    can_export = True
    column_export_list = ['id', 'name', 'description', 'price']
    column_labels = {
        'name': 'Tên sản phẩm',
        'description': 'Mô tả',
        'price': 'Giá'
    }
    page_size = 5
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'description': CKTextAreaField
    }


class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        statsMedicine = dao.stats_by_medic(kw=request.args.get('kw'),
                                           from_date=request.args.get('from_date'),
                                           to_date=request.args.get('to_date'))
        return self.render('admin/stats.html', statsMedicine=statsMedicine)


class StatsView1(AuthenticatedView):
    @expose('/')
    def index(self):
        statsRevenue = dao.stats_by_revenue(month=request.args.get('month'))
        return self.render('admin/stats1.html', statsRevenue=statsRevenue)


class LogoutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class MyAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        statsProduct = dao.count_product_by_cate()
        userRoleStats = dao.count_user()
        return self.render('admin/index.html', userRoleStats=userRoleStats, statsProduct=statsProduct)


class RuleView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


# class MyRuleView(RuleView):
#     @expose('/', methods=['get', 'post'])
#     def quy_dinh(self):
#         err_msg = ""
#         with open("data/quy_dinh.json", "r") as file:
#             quy_dinh = json.load(file)
#
#         with open("data/quy_dinh.json", "w") as file:
#             if request.method.__eq__("POST"):
#                 tien_kham = request.form["tien_kham"]
#                 so_benh_nhan = request.form["so_benh_nhan"]
#
#                 if tien_kham <= 0:
#                     err_msg = "Số tiền khám phải lớn hơn 0"
#                     file.write(json.dumps(quy_dinh))
#                     return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)
#                 else:
#                     quy_dinh["tien_kham"] = tien_kham
#                     file.write(json.dumps(quy_dinh))
#                 #     ====================================================================
#                 if so_benh_nhan <= 0:
#                     err_msg = "Số bệnh nhân phải lớn hơn 0"
#                     file.write(json.dumps(quy_dinh))
#                     return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)
#                 else:
#                     quy_dinh["so_benh_nhan"] = so_benh_nhan
#                     file.write(josn.dumps(quy_dinh))
#             else:
#                 file.write(json.dumps(quy_dinh))
#
#         return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)

class MyRuleView(RuleView):
    @expose('/', methods=['get', 'post'])
    def quy_dinh(self):
        err_msg = ""
        with open("data/quy_dinh.json", "r") as file:
            quy_dinh = json.load(file)

        with open("data/quy_dinh.json", "w") as file:
            if request.method.__eq__("POST"):
                tien_kham = request.form["tien_kham"]
                so_benh_nhan = request.form["so_benh_nhan"]
                # file.write(json.dumps(quy_dinh))
                if tien_kham and so_benh_nhan:
                    if int(tien_kham) < 0 or int(so_benh_nhan) < 0:
                        err_msg = "Số tiền khám hoặc số bệnh nhân phải lớn hơn 0"
                        file.write(json.dumps(quy_dinh))
                        return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)
                    else:
                        quy_dinh["tien_kham"] = tien_kham
                        quy_dinh["so_benh_nhan"] = so_benh_nhan
                        file.write(json.dumps(quy_dinh))
                        return self.render("admin/rule.html", quy_dinh=quy_dinh, err_msg=err_msg)
                else:
                    err_msg = "Chưa nhập đủ"
                    file.write(json.dumps(quy_dinh))
                #     ====================================================================
            file.write(json.dumps(quy_dinh))
        return self.render('admin/rule.html', quy_dinh=quy_dinh, err_msg=err_msg)


admin = Admin(app=app, name='QUẢN TRỊ', template_mode='bootstrap4', index_view=MyAdminView())
admin.add_view(AuthenticatedModelView(DanhMucThuoc, db.session, name='Danh mục thuốc'))
admin.add_view(AuthenticatedModelView(Thuoc, db.session, name='Danh sách thuốc'))
admin.add_view(AuthenticatedModelView(User, db.session, name='Tài khoản'))
admin.add_view(MyRuleView(name="Quy định"))
admin.add_view(StatsView(name='Thống kê - Báo cáo sử dụng thuốc'))
admin.add_view(StatsView1(name='Thống kê - báo cáo doanh thu'))
admin.add_view(LogoutView(name='Đăng xuất'))
