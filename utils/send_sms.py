from .get_cfg import get_cfg
from twilio.rest import Client

cfg = get_cfg()

client = Client(cfg['TWILIO']['SID'], cfg['TWILIO']['TOKEN'])
message = f"http://{cfg['PI']['HOST']}:{cfg['PI']['PORT']}\n{cfg['ANDROID']['MESSAGE']}"

def send_sms():   
    client.messages.create(
        from_ = cfg['TWILIO']['FROM_NUM'],
        to = cfg['TWILIO']['TO_NUM'],
        body = message
    )
