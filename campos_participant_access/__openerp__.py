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
        'security/campos_event_participant.xml',
        'views/campos_event_participant.xml',
        'data/mail_templates.xml',
    ],
    'demo': [
    ],
}
