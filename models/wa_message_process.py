# -*- coding: utf-8 -*-
from odoo import fields, models, _
import requests
import json
from odoo.exceptions import ValidationError

class WaMessageModelAdaptation(models.Model):
    _name = "wa.message.model.adaptation"
    _order = "create_date"

    model_id = fields.Many2one('ir.model')
    model_name = fields.Char(related='model_id.model')
    activity_user_field_id = fields.Many2one('ir.model.fields')
    activity_default_user_id = fields.Many2one('res.users')
    phone_field_ids = fields.Many2many('ir.model.fields')

    def get_phone_number(self, res_id=False):
        rec = self.env[self.model_name].browse(res_id)[0]
        phone = False
        for phone_field in self.phone_field_ids.filtered(lambda x: x.relation =='res.partner'):
            partner = rec[phone_field.name]
            if partner:
                if partner.mobile:
                    phone = partner.mobile
                    break
                elif partner.phone:
                    phone = partner.phone
                    break
        if not phone:
            for phone_field in self.phone_field_ids.filtered(lambda x: x.relation != 'res.partner'):
                field = rec[phone_field.name]
                if field:
                    phone = field
                    break
        if not phone:
            raise ValidationError(_(f'Not phone number found for id {res_id} - {self.model_name}'))
        else:
            return phone


class WaMessageQueue(models.Model):
    _name = "wa.message"
    _order = "create_date DESC"

    res_id = fields.Char()
    res_model = fields.Char()
    status_code = fields.Char()
    dialog_message_id = fields.Char()
    json_response = fields.Char()
    json_payload = fields.Char()
    wa_message_template_id = fields.Many2one('wa.message.template')
    company_id = fields.Many2one('res.company')

    def get_config(self):
        company = self.env.user.company_id
        return {
            'dialog_api_key': company.dialog_api_key,
            'dialog_namespace': company.dialog_namespace,
            'webhook_url': company.webhook_url,
            'developer_mode': company.developer_mode,
        }

    def log_note(self, message_content):
        active_rec = self.env[self.res_model].browse(int(self.res_id))
        for rec in active_rec:
            txt = "WhatsApp Message Sent | "
            response = json.loads(self.json_response)
            payload = json.loads(self.json_payload)
            txt += payload['to'] + "<br/>"
            if self.status_code == "200" or self.status_code == "201":
                if self.status_code == "200":
                    txt += " Status: OK"
                else:
                    txt += " Status: SENT"
                txt += "<br/> Content: " + message_content
            else:
                if 'error' in response.keys():
                    error = response['error']
                    if type(error) != str:
                        if 'message' in error.keys():
                            error = error['message']
                    else:
                        error = response['error']
                elif 'meta' in response.keys() and 'developer_message' in response['meta'].keys():
                    error = response['meta']['developer_message']
                else:
                    error = "Error indefinido. Contactar Admin"
                txt += " ERROR: " + error
                config = self.env['wa.message.model.adaptation'].search([('model_id.model', '=', self.res_model)])
                if not config:
                    raise ValidationError(_("There is no model adaptation config for ") + self._name)
                user = rec[config.activity_user_field_id.name]
                if not user:
                    user = config.activity_default_user_id
                if not user:
                    user = self.env.user
                rec.activity_schedule('odoo-whatsapp-api.message_error_activity', user_id=user.id, note=error, date_deadline=fields.Date.today())
            rec.message_post(body=txt)

    def config_testing_webhook(self):
        config = self.get_config()
        developer_mode = config['developer_mode']
        if developer_mode:
            url = "https://waba-sandbox.360dialog.io/v1/configs/webhook"
        else:
            url = "https://waba.360dialog.io/v1/configs/webhook"
        payload = {"url": config['webhook_url'] + "/whatsapp/webhook"}
        headers = {
            'D360-Api-Key': config['dialog_api_key'],
            'Content-Type': "application/json",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        print(response.status_code)
        print(response.json())

    def messaging_health_status(self):
        config = self.get_config()
        developer_mode = config['developer_mode']
        if developer_mode:
            url = "https://waba.360dialog.io/v1/health_status"
        else:
            url = "https://waba.360dialog.io/v1/health_status"
        headers = {
            'D360-Api-Key': config['dialog_api_key'],
            'Content-Type': "application/json",
        }
        response = requests.get(url, headers=headers)
        print(response.status_code)
        print(response.json())

    def send_message(self, res_id, res_model, phone_number, text):
        config = self.get_config()
        developer_mode = config['developer_mode']
        if developer_mode:
            url = "https://waba-sandbox.360dialog.io/v1/messages"
        else:
            url = "https://waba.360dialog.io/v1/messages"
        # Create the payload with the injected phone number and text
        payload = {
            "to": phone_number,
            "recipient_type": "individual",
            "type": "text",
            "messaging_product": "whatsapp",
            "text": {
                "body": text
            }
        }
        headers = {
            'D360-API-KEY': config['dialog_api_key'],
            'Content-Type': "application/json",
        }
        # Convert the payload dictionary to a JSON string
        payload_json = json.dumps(payload)
        # Send the POST request with the payload and headers
        response = requests.post(url, json=payload, headers=headers)
        dialog_message = False
        if 'messages' in response.json().keys():
            dialog_message = response.json()['messages'][0]['id']
        message_vals = {
            'res_id': res_id,
            'res_model': res_model,
            'status_code': response.status_code,
            'dialog_message_id': dialog_message,
            'json_payload': payload_json,
            'json_response': json.dumps(response.json()),
            'company_id': self.env.user.company_id.id
        }
        wa = self.env['wa.message'].create(message_vals)
        wa.log_note(text)

    def send_message_template(self, res_id, res_model, phone_number, template_id):
        config = self.get_config()
        developer_mode = config['developer_mode']
        if developer_mode:
            url = "https://waba-sandbox.360dialog.io/v1/messages"
        else:
            url = "https://waba.360dialog.io/v1/messages"
        active_rec = self.env[res_model].browse(res_id)
        parameters = []
        for param in template_id.get_params_values(res_id):
            parameters.append({
                "type": "text",
                "text": param
            })
        payload = {
                "to": phone_number,
                "type": "template",
                "messaging_product": "whatsapp",
                "template": {
                    "namespace": config['dialog_namespace'],
                    "language":  {"code": template_id.lang_code or "en", "policy": "deterministic"},
                    "name": template_id.dialog_reference,
                    "components": [{
                            "type": "body",
                            "parameters": parameters
                        }
                    ]
                }
            }
        payload_json = json.dumps(payload)
        headers = {
            'D360-Api-Key': config['dialog_api_key'],
            'Content-Type': "application/json",
        }
        response = requests.post(url, json=payload, headers=headers)
        dialog_message = False
        if 'messages' in response.json().keys():
            dialog_message = response.json()['messages'][0]['id']
        message_vals = {
            'res_id': res_id,
            'res_model': res_model,
            'status_code': response.status_code,
            'dialog_message_id': dialog_message,
            'json_payload': payload_json,
            'json_response': json.dumps(response.json()),
            'company_id': self.env.user.company_id.id,
            'wa_message_template_id': template_id.id
        }
        wa = self.env['wa.message'].create(message_vals)
        wa.log_note(template_id.get_sending_txt(template_id.get_params_values(res_id)))
