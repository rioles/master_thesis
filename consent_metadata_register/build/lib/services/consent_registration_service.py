from return_object import ReturnObject, my_dict
from models.permission_identity import PermissionIdentity
from datetime import datetime


class ConsentRegistration:
    def __init__(self, request_data, return_object):
        self.request_data = request_data
        self.return_object = return_object

    def register_consent(self):
        consent_attribut = self.return_object.create_consent_attribut_object()[0]
        data_controler_object = self.return_object.create_data_controller()
        data_processor = self.return_object.create_data_processor()
        data_provider = self.return_object.create_data_provider()

        data_controler_object.save()
        data_processor.save()
        data_provider.save()

        permission_object = []
        for element in consent_attribut:
            permission_dict = {}
            permission_dict["id_data_subject"] = self.request_data["user_anip"]
            permission_dict["expiration_date"] = self.request_data["expiration_date"]
            permission_dict["beginning_date"] = self.request_data["beginning_date"] if "beginning_date" in self.request_data else datetime.now()
            permission_dict["data_provider_id"] = data_provider.id
            permission_dict["data_controller_id"] = data_controler_object.id
            permission_dict["consent_attribute_id"] = element.id
            permission_dict["consent_date"] = datetime.now()

            permission_object = PermissionIdentity(**permission_dict)

            element.save()
            permission_object.save()
            permission_object.append(permission_object.to_dict())
            print("permission object", permission_object)

        return permission_object
			
b = ReturnObject(my_dict)			
a = ConsentRegistration(my_dict, b)

print(a.register_consent())			
			
			
			
			
	
