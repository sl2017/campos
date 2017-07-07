# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CampOS Participant Access',
    'description': """
        CampOS Participant Access""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': [
                'campos_event',
                'campos_final_registration',
    ],
    'data': [
        'views/event_registration.xml',
        'security/campos_clc_stat.xml',
        'views/campos_clc_stat.xml',
        'security/campos_event_participant.xml',
        'views/campos_event_participant.xml',
        'data/mail_templates.xml',
    ],
    'demo': [
    ],
}
