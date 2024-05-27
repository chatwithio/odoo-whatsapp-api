# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
import requests
import json
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class WaWebHookMessages(models.Model):
    _name = 'wa.webhook.messages'
    _order = "create_date DESC"

    json_content = fields.Char()
    @api.depends('json_content')
    def message_process(self):
        for record in self:
            payload = json.loads(record.json_content)
            if "statuses" in payload.keys():
                for status in payload['statuses']:
                    message_id = status['id']
                    status = status['status']
                    wa_message = self.env['wa.message'].sudo().search([('dialog_message_id', '=', message_id)])
                    if wa_message:
                        wa_message[0].status = status
                        wa_message[0].webhook_message_ids = [(4, record.id)]
            record.trigger_message_process = False if record.trigger_message_process else True
    trigger_message_process = fields.Boolean(compute=message_process, store=True)


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

    message_content = fields.Text()
    res_id = fields.Char()
    res_model = fields.Char()
    status_code = fields.Char()
    mail_message_id = fields.Many2one('mail.message')
    status = fields.Selection(selection=[
        ('in_progress', 'In Progress'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ])
    dialog_message_id = fields.Char()
    json_response = fields.Char()
    json_payload = fields.Char()
    wa_message_template_id = fields.Many2one('wa.message.template')
    company_id = fields.Many2one('res.company')
    webhook_message_ids = fields.Many2many('wa.webhook.messages')

    def get_config(self):
        company = self.env.user.company_id
        return {
            'dialog_api_key': company.dialog_api_key,
            'dialog_namespace': company.dialog_namespace,
            'webhook_url': company.webhook_url,
            'developer_mode': company.developer_mode,
        }

    def schedule_error_activity(self, error_message):
        if self.res_model and self.res_id:
            active_rec = self.env[self.res_model].browse(int(self.res_id))
        config = self.env['wa.message.model.adaptation'].search([('model_id.model', '=', self.res_model)])
        if not config:
            raise ValidationError(_("There is no model adaptation config for ") + self._name)
        for rec in active_rec:
            user = rec[config.activity_user_field_id.name]
            if not user:
                user = config.activity_default_user_id
            if not user:
                user = self.env.user
            rec.activity_schedule('odoo-whatsapp-api.message_error_activity', user_id=user.id, note=error_message, date_deadline=fields.Date.today())
    @api.depends('status')
    def log_note(self):
        for record in self:
            if record.res_model and record.res_id:
                active_rec = self.env[record.res_model].browse(int(record.res_id))
            for rec in active_rec:
                if record.status:
                    message_text = f"WhatsApp Message {dict(self._fields['status']._description_selection(self.env)).get(record.status)} | "
                else:
                    message_text = ''
                response = json.loads(record.json_response)
                payload = json.loads(record.json_payload)
                if payload:
                    message_text += payload['to'] + "<br/>"
                if record.message_content:
                    message_text += "<br/> Content: " + record.message_content
                if record.status == 'failed':
                    messages_to_process = []
                    messages_to_process.append(response)
                    for webhook_message in record.webhook_message_ids:
                        messages_to_process.append(json.loads(webhook_message.json_content))
                    error_message = ''
                    for message in messages_to_process:
                        if 'statuses' in message.keys():
                            for status in message['statuses']:
                                if 'errors' in status.keys():
                                    for error in status['errors']:
                                        if 'details' in error.keys():
                                            error_message += error['details'] + "  ||  "
                                        elif 'title' in error.keys():
                                            error_message += error['title'] + "  ||  "
                                        else:
                                            error_message += 'Unknown Error. Reach Admin  ||  '
                    record.schedule_error_activity(error_message)
                if record.mail_message_id:
                    record.mail_message_id.body = message_text
                else:
                    new_message = rec.message_post(body=message_text)
                    record.mail_message_id = new_message.id
            record.trigger_log_note = False if record.trigger_log_note else True
    trigger_log_note = fields.Boolean(compute=log_note, store=True)
    def config_testing_webhook(self):
        config = self.get_config()
        developer_mode = config['developer_mode']
        if developer_mode:
            url = "https://waba-sandbox.360dialog.io/v1/configs/webhook"
        else:
            url = "https://waba.360dialog.io/v1/configs/webhook"
        payload = {"url": config['webhook_url'] + "/api/v1/whatsapp/webhook"}
        headers = {
            'D360-Api-Key': config['dialog_api_key'],
            'Content-Type': "application/json",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        _logger.info("WhatsApp webhook configured: %s", response.json())

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
        _logger.info("WhatsApp Health Test: %s", response.json())

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
            'status': 'delivered' if response.status_code == 200 else 'in_progress',
            'dialog_message_id': dialog_message,
            'json_payload': payload_json,
            'json_response': json.dumps(response.json()),
            'company_id': self.env.user.company_id.id,
            'message_content': text
        }
        wa = self.env['wa.message'].create(message_vals)

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
            'status': 'delivered' if response.status_code == '200' else 'in_progress',
            'dialog_message_id': dialog_message,
            'json_payload': payload_json,
            'json_response': json.dumps(response.json()),
            'company_id': self.env.user.company_id.id,
            'wa_message_template_id': template_id.id,
            'message_content': template_id.get_sending_txt(template_id.get_params_values(res_id)),
        }
        wa = self.env['wa.message'].create(message_vals)
