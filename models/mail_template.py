from odoo import fields, models, _
from odoo.exceptions import ValidationError

class MailTemplate(models.Model):
    _inherit = "mail.template"

    wa_dialog_template = fields.Boolean(string="360 Dialog Template")
    wa_message_template_id = fields.Many2one('wa.message.template', string="WhatsApp Template")

class MailThread(models.AbstractModel):
    """ Update MailThread to add the support of bounce management in mass mailing traces. """
    _inherit = 'mail.thread'

    def message_post_with_template(self, template_id, **kwargs):
        template = self.env['mail.template'].browse(template_id)
        if template and template.wa_message_template_id:
            config = self.env['wa.message.model.adaptation'].search([('model_id.model', '=', template.wa_message_template_id.model_id.model)])
            if not config:
                raise ValidationError(_("There is no model adaptation config for " ) + self._name)
            phone = config[0].get_phone_number(res_id=self.id).replace(" ", "").replace("+", "").replace("-", "")
            self.env['wa.message'].send_message_template(res_id=self.id, res_model=self._name, phone_number=phone,
                                                         template_id=template.wa_message_template_id)
        else:
            return super(MailThread, self).message_post_with_template(template_id, **kwargs)
