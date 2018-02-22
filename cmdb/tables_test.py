from django.db.models import Count
import os
import django
import sys

pathname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pathname)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SeriousCMDB.settings")
django.setup()

from cmdb import models, tables, admin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class TableHandler:
    def __init__(self, model_class, model_admin, page_obj=None, order_res_list=None, request=None,):
        self.request = request
        self.model_class = model_class
        self.model_admin = model_admin
        self.page_obj = page_obj
        self.order_res_list = order_res_list

        self.choice_fields = model_admin.choice_fields
        self.fk_fields = model_admin.fk_fields
        self.list_display = model_admin.list_display
        self.list_filter = model_admin.list_filter

        # self.orderby_field = order_res_list[1]
        # self.orderby_col_index = order_res_list[2]

        self.dynamic_fk = getattr(model_admin,'dynamic_fk') if \
                hasattr(model_admin, 'dynamic_fk') else None
        self.dynamic_list_display = getattr(model_admin,'dynamic_list_display') if \
            hasattr(model_admin,'dynamic_list_display') else ()
        self.dynamic_choice_fields = getattr(model_admin,'dynamic_choice_fields') if \
            hasattr(model_admin,'dynamic_choice_fields') else ()
        self.m2m_fields = getattr(model_admin, 'm2m_fields') if \
            hasattr(model_admin, 'm2m_fields') else ()

table_handler = TableHandler(models.Asset, admin.AssetAdmin)


#
#
asset_obj_list = models.Asset.objects.all()
print(asset_obj_list)
paginator = Paginator(list(asset_obj_list), admin.AssetAdmin.list_per_page)

print(paginator.page(1))

for i in paginator.page(1):
    print(i)
    for index, column_name in enumerate(admin.AssetAdmin.list_display):
        column_data = i._meta.get_field(column_name).value_from_object(i)
        print(column_data)
# try:
#     page_obj = paginator.page(page)
# except PageNotAnInteger:
#     page_obj = paginator.page(1)
# except EmptyPage:
#     page_obj = paginator.page(paginator.num_pages)



# print(table_handler.list_filter)
#
# for i in table_handler.list_filter:
#     col_obj = table_handler.model_class._meta.get_field(i)
#     print(col_obj.verbose_name)
#     print(col_obj.get_internal_type())
#     if col_obj.get_internal_type() not in ('DateField', 'DatetimeField'):
#         choices = col_obj.get_choices()
#         print(choices)
#         choices_list = col_obj.model.objects.values(i).annotate(count=Count(i))
#         print(choices_list)
#         choices = [[obj[i], obj[i]] for obj in choices_list]
#         print(choices)
#     print("-------------")
#
#
# from django.utils import timezone
# import time
#
# #     print("filter conditions",  filter_conditions)
# #     return model_class.objects.filter(**filter_conditions)
# #
# # list_filter = admin.AssetAdmin.list_filter
# # for condition in list_filter:
# #     field_type_name = models.Asset._meta.get_field(condition).__repr__()
# #     print(field_type_name)
#
# today_obj = timezone.datetime.now()
# print(today_obj)
#
# print(today_obj.strftime("%Y-%m-%d"))
# print(timezone.timedelta(days=today_obj.day))
# print(today_obj - timezone.timedelta(seconds=time.time()))
