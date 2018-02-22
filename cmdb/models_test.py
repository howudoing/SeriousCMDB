from django.db.models import Count
import os
import django
import sys

pathname = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(pathname)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SeriousCMDB.settings")
django.setup()

from cmdb import models, tables, admin
#
# dataset = {
#     'names': [],
#     'data': []
# }
# prefetch_data = {
#     models.Server: None,
#     models.NetworkDevice: None,
#     models.SecurityDevice: None,
#     models.Software: None,
# }
#
# for key in prefetch_data:
#     data_list = list(key.objects.values('sub_asset_type').annotate(total=Count('sub_asset_type')))
#     # print(key.sub_asset_type_choices)
#     # print(data_list)
#     for index, sub_asset_record in enumerate(data_list):
#         for db_val, sub_asset_name in key.sub_asset_type_choices:
#             if sub_asset_record['sub_asset_type'] == db_val:
#                 data_list[index]['name'] = sub_asset_name
#
#     for item in data_list:
#          dataset['names'].append(item['name'])
#          dataset['data'].append(item['total'])
#
# print(dataset)
# def asset_list(request):
#     asset_obj_list = tables.table_filter(request, admin.AssetAdmin, models.Asset)
#     print(asset_obj_list)
#
#
# field_type_name = models.Asset._meta.get_field("asset_type").__repr__()
# print(field_type_name)
# if 'db' in field_type_name:
#     print('yes')
#
# asset_obj_list = models.Asset.objects.filter(asset_type='server')
# objs = asset_obj_list.order_by('id')
# print(objs)
#
# orderby_column_index = admin.AssetAdmin.list_display.index('asset_type')
# print(orderby_column_index)
asset_obj = models.Asset.objects.get(sn=456)
print(asset_obj)

print(int(None))