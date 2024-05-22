import logging
from odoo import http
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
        # Process the incoming data here
        return True

