# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class WaMessageTemplate(models.Model):
    _name = "wa.message.template"

    name = fields.Char(string="Name")
    content = fields.Text(string="Content")
    dialog_reference = fields.Char(string="360 Dialog Reference")
    params_ids = fields.One2many('wa.message.template.params', 'template_id')
    model_id = fields.Many2one('ir.model')
    model_name = fields.Char(related="model_id.name")
    lang_code = fields.Char()

    def get_params_values(self, res_id=False):
        res = []
        rec = self.env[self.model_id.model].browse(res_id)
        if rec:
            for param in self.params_ids:
                if param.type == 'custom_text':
                    res.append(param.custom_text)
                else:
                    txt = False
                    if param.field_id.ttype == 'char':
                        txt = rec[param.field_id.name]
                    elif param.field_id.ttype == 'many2one':
                        txt = rec[param.field_id.name].display_name
                    else:
                        raise ValidationError(_("Field Type Error. Reach Admin"))
                    if not txt:
                        txt = param.not_found_content
                    res.append(txt)
        return res

    @api.constrains('content', 'params_ids')
    def check_len_inputs(self):
        content = self.content
        params = self.params_ids
        # Count the number of placeholders in the text
        placeholder_count = content.count('[]')
        # Validate that the length of the parameters list matches the placeholder count
        if len(params) != placeholder_count:
            raise ValidationError(_(
                f"Number of parameters ({len(params)}) does not match the number of placeholders ({placeholder_count})"))

    def get_sending_txt(self, params):
        content = self.content
        # Count the number of placeholders in the text
        placeholder_count = content.count('[]')
        # Validate that the length of the parameters list matches the placeholder count
        if len(params) != placeholder_count:
            raise ValidationError(_(
                f"Number of parameters ({len(params)}) does not match the number of placeholders ({placeholder_count})"))
        # Replace each placeholder with the corresponding parameter
        for param in params:
            content = content.replace('[]', param, 1)
        return content



class WaMessageTemplateParams(models.Model):
    _name = "wa.message.template.params"
    _order = "sequence"

    sequence = fields.Integer()
    model_id = fields.Many2one(related="template_id.model_id")
    model_name = fields.Char(related="model_id.name")
    template_id = fields.Many2one('wa.message.template')
    type = fields.Selection(selection=[('custom_text', 'Custom text'), ('model_field', 'Model Field')])
    field_id = fields.Many2one('ir.model.fields')
    custom_text = fields.Text()
    not_found_content = fields.Char()


