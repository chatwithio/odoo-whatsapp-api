# -*- coding: utf-8 -*-
{
    'name': 'odoo-whatsapp-api',
    'summary': "360 Dialog WhatsApp Integration",
    'description': """""",
    'author': 'Santiago Apel',
    'website': '',
    "support": "apelsantiago@gmail.com",
    'category': 'Mail',
    'version': '15',
    'depends': ['mail','crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/whatsapp_views.xml',
        'views/whatsapp_adaptation_model_views.xml',
        'data/activity_type_data.xml',
        'views/res_config_settings_view.xml',
        'views/whatsapp_template_views.xml',
        'views/mail_template_views.xml',
        'wizards/mail_compose_message_views.xml',
    ],
    'license': "OPL-1",
    'auto_install': False,
    'installable': True,
}
