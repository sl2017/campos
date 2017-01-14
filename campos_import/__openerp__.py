# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CampOS Import',
    'description': """
        Participant import helper module""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': ['campos_welcome',
                'campos_final_registration',
    ],
    'data': [
        'security/sale_order.xml',
        'views/sale_order.xml',
             'wizards/campos_import_participant_wiz.xml',
             'wizards/campos_import_member_wiz.xml',
             'wizards/campos_import_manager_wiz.xml',
             'views/campos_event_participant.xml',
             'views/event_registration.xml',
             'security/campos_import_member_profile.xml',
             'security/ir.model.access.csv',
             'security/ir.rule.csv',
    ],
    'demo': [
    ],
}
