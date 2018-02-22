from django.db.models import Count
from django.utils import timezone
import time

def table_filter(request, model_admin, model_class):
    filter_conditions = {}
    for condition in model_admin.list_filter:
        if request.GET.get(condition):
            field_type_name = model_class._meta.get_field(condition).__repr__()

            if 'ForeignKey' in field_type_name:
                filter_conditions['%s_id' % condition] = request.GET.get(condition)
            elif 'DateField' in field_type_name:
                filter_conditions['%s__gt' % condition] = request.GET.get(condition)
            else:
                filter_conditions[condition] = request.GET.get(condition)


    print("filter conditions",  filter_conditions)
    return model_class.objects.filter(**filter_conditions)

def get_asset_orderby(request, model_obj_list, model_admin):
    orderby_field = request.GET.get("orderby")
    if orderby_field:
        orderby_field = orderby_field.strip()
        orderby_column_index = model_admin.list_display.index(orderby_field.strip('-'))
        objs = model_obj_list.order_by(orderby_field)
        if orderby_field.startswith('-'):
            orderby_field = orderby_field.strip('-')
        else:
            orderby_field = '-%s' % orderby_field
        return [objs, orderby_field, orderby_column_index]
    else:
        return [model_obj_list, orderby_field, None]



class TableHandler:
    def __init__(self,request, model_class, model_admin, page_obj, order_res_list):
        self.request = request
        self.model_class = model_class
        self.model_admin = model_admin
        self.page_obj = page_obj
        self.order_res_list = order_res_list

        self.choice_fields = model_admin.choice_fields
        self.fk_fields = model_admin.fk_fields
        self.list_display = model_admin.list_display
        self.list_filter = self.get_list_filter(model_admin.list_filter)

        self.orderby_field = order_res_list[1]
        self.orderby_col_index = order_res_list[2]

        self.dynamic_fk = getattr(model_admin,'dynamic_fk') if \
            hasattr(model_admin, 'dynamic_fk') else None
        self.dynamic_list_display = getattr(model_admin,'dynamic_list_display') if \
            hasattr(model_admin,'dynamic_list_display') else ()
        self.dynamic_choice_fields = getattr(model_admin,'dynamic_choice_fields') if \
            hasattr(model_admin,'dynamic_choice_fields') else ()
        self.m2m_fields = getattr(model_admin, 'm2m_fields') if \
            hasattr(model_admin, 'm2m_fields') else ()

    def get_list_filter(self, list_filter):
        filters = []
        for i in list_filter:
            column_obj = self.model_class._meta.get_field(i)
            data = {
                'verbose_name': column_obj.verbose_name,
                'column_name': i
            }
            if column_obj.get_internal_type() not in ('DateField', 'DateTimeField'):
                try:
                    choices = column_obj.get_choices()
                except AttributeError as e:
                    choices_list = column_obj.model.objects.values(i).annotate(count=Count(i))
                    choices = [[obj[i], obj[i]] for obj in choices_list]
                    choices.insert(0, ['', '----------'])
            else:
                today_obj = timezone.datetime.now()
                choices = [
                    ('', '----------'),
                    (today_obj.strftime("%Y-%m-%d"), '今天'),
                    ((today_obj - timezone.timedelta(days=7)).strftime("%Y-%m-%d"), '过去7天'),
                    ((today_obj - timezone.timedelta(days=today_obj.day)).strftime("%Y-%m-%d"), '本月'),
                    ((today_obj - timezone.timedelta(days=90)).strftime("%Y-%m-%d"), '过去3个月'),
                    ((today_obj - timezone.timedelta(days=180)).strftime("%Y-%m-%d"), '过去6个月'),
                    ((today_obj - timezone.timedelta(days=365)).strftime("%Y-%m-%d"), '过去一年'),
                    ((today_obj - timezone.timedelta(seconds=time.time())).strftime("%Y-%m-%d"), 'ALL'),
                ]
            data['choices'] = choices
            print('----------->', choices)
            if self.request.GET.get(i):
                data['selected'] = self.request.GET.get(i)
            filters.append(data)

        return filters




