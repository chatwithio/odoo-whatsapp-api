import logging
from odoo import http
from odoo.http import request
import json

_logger = logging.getLogger(__name__)


class WhatsappWebhookController(http.Controller):
    @http.route('/whatsapp/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def whatsapp_webhook(self):
        payload = request.jsonrequest
        _logger.info("Received WhatsApp webhook: %s", json.dumps(payload))
        # Process the incoming data here
        return True