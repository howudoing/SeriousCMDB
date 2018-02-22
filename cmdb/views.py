from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cmdb.dashboard import AssetDashboard
from cmdb import tables, admin, models, core
import django
import json
# Create your views here.

@login_required
def index(request):
    return render(request, 'index.html')

def acc_login(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.valid_end_time:
                if django.utils.timezone.now() > user.valid_begin_time and django.utils.timezone.now() < user.valid_end_time:
                    auth.login(request, user)
                    request.session.set_expiry(60*30)
                    return HttpResponseRedirect('/')
                else:
                    return render(request, 'login.html', {'login_err': 'User account is expired, please contact with your Administrator!'})
            elif django.utils.timezone.now() > user.valid_begin_time:
                auth.login(request, user)
                request.session.set_expiry(60 * 30)
                return HttpResponseRedirect('/')
        else:
            return render(request, 'login.html', {'login_err': 'Wrong username or password!'})
    return render(request, 'login.html')

def acc_logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')

@login_required
def get_dashboard_data(request):
    dashboard_data = AssetDashboard(request)
    dashboard_data.serialize_page()
    return HttpResponse(json.dumps(dashboard_data.data))

@login_required
def asset_list(request):
    asset_obj_list = tables.table_filter(request, admin.AssetAdmin, models.Asset)
    print(asset_obj_list)
    ordered_res = tables.get_asset_orderby(request, asset_obj_list, admin.AssetAdmin)
    print("------------->", ordered_res)
    paginator = Paginator(ordered_res[0], admin.AssetAdmin.list_per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    table_obj = tables.TableHandler(request, models.Asset, admin.AssetAdmin, page_obj, ordered_res)
    return render(request, 'cmdb/assets.html', {'table_obj': table_obj,
                                                'paginator': paginator})


def asset_report(request):
    print(request)
    if request.method == "POST":
        asset_obj = core.Asset(request)
        if asset_obj.data_valid():
            asset_obj.data_save()
        return HttpResponse(json.dumps(asset_obj.response))
    # return HttpResponse('_____________asset report_____________')

def asset_with_no_asset_id(request):
    if request.method == "POST":
        # ass_handler = core.Asset(request)
        # res = ass_handler.get_asset_id_by_sn()
        # return HttpResponse(json.dumps(res))
        asset_obj = core.Asset(request)
        if asset_obj.data_valid_without_id():
            asset_obj.data_save()
        return HttpResponse(json.dumps(asset_obj.response))
    # return HttpResponse('_____________asset with no id_______________')1
