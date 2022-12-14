from saleapp import db, app, dao
from saleapp.models import *
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import redirect, request
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


admin = Admin(app=app, name='QUẢN TRỊ', template_mode='bootstrap4', index_view=MyAdminView())
admin.add_view(AuthenticatedModelView(DanhMucThuoc, db.session, name='Danh mục thuốc'))
admin.add_view(AuthenticatedModelView(Thuoc, db.session, name='Danh sách thuốc'))
admin.add_view(AuthenticatedModelView(User, db.session, name='Tài khoản'))
admin.add_view(StatsView(name='Thống kê - Báo cáo sử dụng thuốc'))
admin.add_view(StatsView1(name='Thống kê - báo cáo doanh thu'))
admin.add_view(LogoutView(name='Đăng xuất'))
