# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Campos CKR',
    'description': """
        CKR handling""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': ['campos_event', 
                'model_field_access', 
                'warning_box'
    ],
    'data': [
        'wizards/campos_ckr_fetch_wiz.xml',
        'wizards/campos_ckr_sentin_wiz.xml',
        'security/campos_ckr_check.xml',
        'views/campos_ckr_check.xml',
        'data/ckr_check_templates.xml',
    ],
    'demo': [
    ],
}
