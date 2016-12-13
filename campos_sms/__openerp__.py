# -*- coding: utf-8 -*-

{
    'name': 'CampOS SMS',
    'version': '8.0.0.1',
    'category': 'Association',
    'description': """
SMS extensions for CampOS
=========================

Gateway URL:
If gateway URL is set to "config", it will be fetched from the "sms_gateway_url" parameter in
the config file.

Allowed DBs:
SMS will only be sent, if the database name is in a comma separated list in the config
parameter "sms_allowed_dbs" (e.g. "system1db,system2db").

Prices:
Cost prices and sale prices must be edited before use!

""",
    'author': 'Stein & Gabelgaard',
    'website': 'http://steingabelgaard.dk',
    'depends': ['smsclient', 'campos_event', 'model_field_access'],
    'data': ['security/campos_sms_security.xml',
             'security/ir.model.access.csv',
             'security/ir.rule.csv',
             'data/config.xml',
             'views/sms_config_settings_view.xml',
             'views/smsclient_view.xml',
             'views/sms_confirmed_number_view.xml',
             'views/mass_sms_view.xml',             
             'views/partner_sms_send_view.xml',
             'views/organization_view.xml',
             ],
     'qweb': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
