# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Campos Welcome',
    'description': """
        Single Signon and import from Medlemsservice""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': ['auth_oauth',
                'campos_event',
                'auth_blaatlogin',
                'auth_signup',
                'base_geolocalize',
    ],
    'data': [
        "security/campos_welcome_security.xml",
        'wizards/campos_group_signup.xml',
        'views/res_partner.xml',
        'security/campos_remote_system.xml',
        'views/campos_remote_system.xml',
        'views/res_partner.xml',
        'wizards/campos_welcome.xml',
        'views/mail_templates.xml',
    ],
    'demo': [
        'demo/campos_remote_system.xml',
    ],
}
