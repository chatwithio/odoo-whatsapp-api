import logging
from odoo import http, models, fields, api
from odoo.http import request
import json

_logger = logging.getLogger(__name__)



class WhatsappWebhookController(http.Controller):
    #
    @http.route('/api/v1/whatsapp/webhook', type='json', auth='none', methods=['POST'], csrf=False, cors="*")
    def whatsapp_webhook(self):
        payload = request.jsonrequest
        #setear db en request.session.db y ponerle el name y dsps ya puedo user el request.env para acceder y modifcar todas las tablas (Pdb) request.env['crm.lead'].sudo().create({'name': 'charlyyyyy'})
        _logger.info("Received WhatsApp webhook: %s", json.dumps(payload))
        request.session.db = 'roconsa_dev'
        request.env['wa.webhook.messages'].sudo().create({'json_content': json.dumps(payload)})
        # Process the incoming data here
        return True


"""
SENT
{
    "statuses": [
        {
            "conversation": {
                "expiration_timestamp": 1716385560,
                "id": "f61cd79403dc53c9934e7a1a70cdbd98",
                "origin": {
                    "type": "marketing"
                }
            },
            "id": "wamid.HBgNNTQ5MjIzNTM3NTk1NRUCABEYEjFBOUFBRjhEMDcyMjAzMzg0NwA=",
            "message": {
                "recipient_id": "5492235375955"
            },
            "pricing": {
                "billable": true,
                "category": "marketing",
                "pricing_model": "CBP"
            },
            "status": "sent",
            "timestamp": "1716342744",
            "type": "message"
        }
    ]
}

DELIVERED
{
    "statuses": [
        {
            "conversation": {
                "id": "f61cd79403dc53c9934e7a1a70cdbd98",
                "origin": {
                    "type": "marketing"
                }
            },
            "id": "gBGHVJIjU3WVXwIJYpfe23HBWLot",
            "message": {
                "recipient_id": "5492235375955"
            },
            "pricing": {
                "billable": true,
                "category": "marketing",
                "pricing_model": "CBP"
            },
            "status": "delivered",
            "timestamp": "1716342744",
            "type": "message"
        }
    ]
}
READ

{
    "statuses": [
        {
            "id": "gBGHVJIjU3WVXwIJYpfe23HBWLot",
            "message": {
                "recipient_id": "5492235375955"
            },
            "status": "read",
            "timestamp": "1716342820",
            "type": "message"
        }
    ]
}

{
    "statuses": [
        {
            "errors": [
                {
                    "code": 470,
                    "href": "https://developers.facebook.com/docs/whatsapp/api/errors/",
                    "title": "Message failed to send because more than 24 hours have passed since the customer last replied to this number"
                }
            ],
            "id": "gBGHVJIjU3WVXwIJS1RaUDCN7-R_",
            "message": {
                "recipient_id": "5492235375955"
            },
            "status": "failed",
            "timestamp": "1716572896",
            "type": "message"
        }
    ]
}

"""