# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import re
from odoo.exceptions import ValidationError

class MailComposeMessageWAValue(models.TransientModel):
    _name = 'mail.compose.message.wa.value'

    value = fields.Text()

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    whatsapp = fields.Boolean()
    whatsapp_template_id = fields.Many2one('wa.message.template')
    custom_wa_text = fields.Text()

    @api.onchange('whatsapp_template_id', 'whatsapp')
    def default_value_ids(self):
        vals_list = [(5,)]
        if self.whatsapp_template_id:
            params = self.whatsapp_template_id.get_params_values(self.res_id)
            for par in params:
                vals_list.append((0, 0, {'value': par}))
        self.wa_value_ids = vals_list

    wa_value_ids = fields.Many2many('mail.compose.message.wa.value')

    @api.depends('whatsapp_template_id')
    def get_output_wa_text(self):
        for record in self:
            res = ""
            if record.whatsapp_template_id:
                params = record.whatsapp_template_id.get_params_values(self.res_id)
                res = record.whatsapp_template_id.get_sending_txt(params)
            record.output_wa_text = res
    output_wa_text = fields.Text(compute=get_output_wa_text)

    @api.depends('res_id', 'model', 'whatsapp')
    def get_wa_number(self):
        for record in self:
            res = False
            if record.whatsapp:
                config = self.env['wa.message.model.adaptation'].search([('model_id.model', '=', self.model)])
                if not config:
                    raise ValidationError(_("There is no model adaptation config for ") + self._name)
                if config:
                    res = config[0].get_phone_number(res_id=self.res_id)
            record.whatsapp_number = res
    whatsapp_number = fields.Char(compute=get_wa_number)

    def action_send_mail(self):
        if self.whatsapp:
            phone = self.whatsapp_number.replace(" ", "").replace('-', "").replace('+', "")
            if not self.whatsapp_template_id:
                text = self.custom_wa_text
                self.env['wa.message'].send_message(res_id=self.res_id, res_model=self.model, phone_number=phone, text=text)
            else:
                self.env['wa.message'].send_message_template(res_id=self.res_id, res_model=self.model, phone_number=phone, template_id=self.whatsapp_template_id)
        else:
            return super(MailComposeMessage, self).action_send_mail()