import random
from cmdb import models
from django.db.models import Count

class AssetDashboard:
    def __init__(self, request):
        self.request = request
        self.asset_list = models.Asset.objects.all()
        self.data = {}

    def serialize_page(self):
        self.data['asset_categories'] = self.get_asset_categories()
        self.data['asset_status_statics'] = self.get_asset_status_statistics()
        self.data['business_load'] = self.get_business_load()

    def get_asset_categories(self):
        dataset = {
            'names': [],
            'data': []
        }
        prefetch_data = {
            models.Server: None,
            models.NetworkDevice: None,
            models.SecurityDevice: None,
            models.Software: None,
        }

        for key in prefetch_data:
            data_list = list(key.objects.values('sub_asset_type').annotate(total=Count('sub_asset_type')))
            # print(key.sub_asset_type_choices)
            # print(data_list)
            for index, sub_asset_record in enumerate(data_list):
                for db_val, sub_asset_name in key.sub_asset_type_choices:
                    if sub_asset_record['sub_asset_type'] == db_val:
                        data_list[index]['name'] = sub_asset_name

            for item in data_list:
                dataset['names'].append(item['name'])
                dataset['data'].append(item['total'])
        return dataset

    def get_asset_status_statistics(self):
        pass

    def get_business_load(self):
        pass


