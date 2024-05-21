from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    dialog_api_key = fields.Char(
        string="360 Dialog Api Key",
        help="API key 360 Dialog para WhatsApp",
        related='company_id.dialog_api_key',
        readonly=False,
    )
    dialog_namespace = fields.Char(
        string="360 NameSpace",
        help="NameSpace 360 Dialog para WhatsApp",
        related='company_id.dialog_namespace',
        readonly=False,
    )
    webhook_url = fields.Char(
        string="360 WebHook Address",
        help="NameSpace 360 Dialog para WhatsApp",
        related='company_id.webhook_url',
        readonly=False,
    )
    developer_mode = fields.Boolean(
        related='company_id.developer_mode',
        readonly=False,
    )


class Company(models.Model):
    _inherit = "res.company"

    dialog_api_key = fields.Char(
        string="360 Dialog Api Key",
    )
    dialog_namespace = fields.Char(
        string="360 NameSpace",
    )
    webhook_url = fields.Char(
        string="360 NameSpace",
    )
    developer_mode = fields.Boolean(
        string="Developer Mode",
    )

