import json
from cmdb import models
from django.core.exceptions import ObjectDoesNotExist

class Asset:
    def __init__(self, request):
        self.request = request
        self.mandatory_fields = ['sn', 'asset_id', 'asset_type']
        self.response = {
            'error': [],
            'info': [],
            'warning': []
        }
        self.data = self.__get_post_data()
        self.asset_obj = None
        self.waiting_approval = False

    def __get_post_data(self):
        try:
            data = self.request.POST.get("asset_data")
            data = json.loads(data)
            return data
        except Exception as e:
            self.response_msg('error', 'GetAssetDataFailed', str(e))


    def response_msg(self, msg_type, key, msg):
        if msg_type in self.response:
            self.response[msg_type].append({key: msg})
        else:
            raise ValueError

    def data_valid(self):
        if self.data:
            try:
                self.__mandatory_check(self.data)
                if not self.response["error"]:
                    return True
                else:
                    return False
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))
        # else:
        #     self.response_msg('error', 'AssetDataInvalid', 'The reported asset data is not valid or provided!')

    def data_valid_without_id(self):
        if self.data:
            try:
                asset_obj = models.Asset.objects.get_or_create(sn=self.data.get("sn"), name=self.data.get("sn"))
                self.data["asset_id"] = asset_obj[0].id
                self.__mandatory_check(self.data)
                if not self.response["error"]:
                    return True
                else:
                    return False
            except ValueError as e:
                self.response_msg('error', 'AssetDataInvalid', str(e))

    def __mandatory_check(self, data, only_check_sn=False):
        for field in self.mandatory_fields:
            if field not in data:
                self.response_msg("error", "MandataryCheckFailed",
                                  "Field [%s] is not founded in the reported data" % field)
                return False
        try:
            if not only_check_sn:
                self.asset_obj = models.Asset.objects.get(id=int(data["asset_id"]), sn=data["sn"])
            else:
                self.asset_obj = models.Asset.objects.get(sn=data["sn"])
            return True
        except ObjectDoesNotExist as e:
            self.response_msg("error", "AssetDataInvalid",
                              "Cannot find asset object in DB with asset id [%s] and SN [%s]" % (data["asset_id"], data["sn"]))
            self.waiting_approval = True
            return False

    # def __asset_obj_exist_in_db(self, only_check_sn=False):
    #     try:
    #         if not only_check_sn:
    #             self.asset_obj = models.Asset.objects.get(id=int(self.data["asset_id"]), sn=self.data["sn"])
    #         else:
    #             self.asset_obj = models.Asset.objects.get(sn=self.data["sn"])
    #         return True
    #     except ObjectDoesNotExist as e:
    #         self.response_msg("error", "AssetDataInvalid",
    #                           "Cannot find asset object in DB with asset id [%s] and SN [%s]" % (self.data["asset_id"], self.data["sn"]))
    #         self.waiting_approval = True
    #         return False
    # #
    # def __is_new_asset(self):
    #     pass

    def __create_asset(self):
        func = getattr(self, '__create_%s'% self.data["asset_type"])
        func()

    def __update_asset(self):
        func = getattr(self, '__update_%s' % self.data["asset_type"])
        func()

    def data_save(self):
        if self.waiting_approval:  #新资产则创建
            self.__create_asset()
        else:
            self.__update_asset()

    def __create_server(self):
        self.__create_server_info()
        self.__create_or_update_manufactory()

        self.__create_cpu_component()
        self.__create_disk_component()
        self.__create_nic_component()
        self.__create_ram_component()
        log_msg = "Asset [<a href='/admin/cmdb/asset/%s/' target='_blank'>%s</a>] has been created!" %(
            self.asset_obj.id, self.asset_obj
        )
        self.response_msg('info', 'NewAssetOnline', log_msg)

    def __update_server(self):
        pass

    def __verify_field(self, data_set, field_key, data_type, required=True):
        field_val = data_set.get(field_key)
        if field_val:
            try:
                data_set[field_key] =  data_type(field_val)
            except ValueError as e:
                self.response_msg("error", "InvalidField",
                                  "Data type of field [%s] is invalid, the data type should be [%s]" %(
                                      field_key, data_type))
        elif required == True:
            self.response_msg("error", "LackOfField",
                              "The field [%s] has no value provided in your reporting data [%s]" % (
                                  field_key, data_set))

    def __create_server_info(self, ignore_errs=False):
        try:
            self.__verify_field(self.data, 'model', str)
            if not len(self.response["error"]) or ignore_errs == True:
                data_set = {
                    'asset_id': self.asset_obj.id,
                    'os_type': self.data.get('os_type'),
                    'os_distribution': self.data.get('os_distribution'),
                    'os_release': self.data.get('os_release'),
                }
                obj = models.Server(**data_set)
                obj.asset.model = self.data.get('model')
                obj.save()
                return obj
        except Exception as e:
            self.response_msg("error", "ObjectCreationException", "Object [server] %s"% str(e))

    def __create_or_update_manufactory(self, ignore_errs=False):
        try:
            self.__verify_field(self.data, "manufactory", str)
            manufactory = self.data.get("manufactory")
            if not len(self.response["error"]) or ignore_errs == True:
                obj_exist = models.Manufactory.objects.filter(manufactory = manufactory)
                if obj_exist:
                    obj = obj_exist[0]
                else:
                    obj = models.Manufactory(manufactory=manufactory)
                    obj.save()
                self.asset_obj.manufactory = obj
                self.asset_obj.save()
        except Exception as e:
            self.response_msg("error", "ObjectCreationException", "Object [manufactory] %s" % str(e))

    def __create_cpu_component(self, ignore_errs=False):
        try:
            self.__verify_field(self.data, "model", str)
            self.__verify_field(self.data, "cpu_count", int)
            self.__verify_field(self.data, "cpu_core_count", int)
            if not len(self.response["error"]) or ignore_errs==True:
                data_set = {
                    "asset_id": self.asset_obj.id,
                    "cpu_model": self.data.get("cpu_model"),
                    "cpu_count": self.data.get("cpu_count"),
                    "cpu_core_count": self.data.get("cpu_core_count"),
                }
                obj = models.CPU(**data_set)
                obj.save()
                log_msg = "Asset[%s] --> has added new [cpu] component with data [%s]" % (self.asset_obj, data_set)
                return obj
        except Exception as e:
            self.response_msg("error", "ObjectCreationException", "Object [cpu] %s" % str(e))

    def __create_disk_component(self):
        disk_info = self.data.get("disk")
        if disk_info:
            for disk in disk_info:
                try:
                    self.__verify_field(disk, "diskname", str)
                    self.__verify_field(disk, "disksize", str)
                    if not len(self.response["error"]):
                        data_set = {
                            "asset_id": self.asset_obj.id,
                            "sn": disk.get("diskname"),
                            "capacity": disk.get("disksize"),
                        }
                        obj = models.Disk(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg("error", "ObjectCreationException", "Object [disk] %s" % str(e))

    def __create_nic_component(self):
        nic_info = self.clean_data.get("nic")
        if nic_info:
            for nic_item in nic_info:
                try:
                    self.__verify_field(nic_item, "macaddress", str)
                    if not len(self.response["error"]):
                        data_set = {
                            "asset_id": self.asset_obj.id,
                            "name": nic_item.get("name"),
                            "ipaddress": nic_item.get("ipaddress"),
                            "macaddress": nic_item.get("macaddress"),
                            "netmask": nic_item.get("netmask"),
                        }
                        obj = models.NIC(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg("error", "ObjectCreationException", "Object [nic] %s" % str(e))

    def __create_ram_component(self):
        ram_info = self.data.get("ram")
        if ram_info:
            for ram_item in ram_info:
                try:
                    self.__verify_field(ram_item, 'capacity', int)
                    if not len(self.response["error"]):
                        data_set = {
                            "asset_id": self.asset_obj.id,
                            "model": ram_item.get("model"),
                            "slot": ram_item.get("slot"),
                            "sn": ram_item.get("sn"),
                            "capacity": ram_item.get("capacity"),
                        }
                        obj = models.RAM(**data_set)
                        obj.save()
                except Exception as e:
                    self.response_msg("error", "ObjectCreationException", "Object [ram] %s" % str(e))
        else:
            self.response_msg("error", "LackOfData", "RAM info is not provided in your reporting data")

    # def get_asset_id_by_sn(self):
    #     if self.__mandatory_check(self.data, only_check_sn=True):
    #         response = {"asset_id": self.asset_obj.id}
    #     else:
    #         if self.waiting_approval == True:
    #             response = {"needs_approval": "this is a new asset, needs IT admin's approval to create the new asset id"}
    #             # self.save_new_asset_to_approval_zone()
    #             print(response)
    #         else:
    #             response = self.response
    #     return response
