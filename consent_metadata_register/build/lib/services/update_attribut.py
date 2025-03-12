from services.helper_conset import get_updated_consent_data, get_updated_consent_data_all
from celery import current_app
from celery import Celery
from celery.utils.log import get_task_logger
appli = Celery('update_user_consent', broker='amqp://guest@localhost:5672//', backend='rpc://')


@appli.task(name="update_consent_data_task")
def register_data_redis(data_from_redis, data_from_api,id):
    erase_all = data_from_api["erase_all"]
    #print(data_from_api)
    if erase_all == False:
        consent = data_from_api["attr"]
        data_dicts = get_updated_consent_data(data_from_redis, consent)
        add_erase_data_to_redis(data_dicts, id)
        return data_dicts
    else:
        elements = get_updated_consent_data_all(data_from_redis)
        add_erase_data_to_redis(elements, id)
        return elements
