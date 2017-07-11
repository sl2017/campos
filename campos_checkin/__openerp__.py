# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Campos Checkin',
    'description': """
        CampOS Check In functionality""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': [
        'campos_jobber_final',
        'campos_transportation',
    ],
    'data': [
        'wizards/campos_checkin_wiz.xml',
        'security/campos_checkin.xml',
        'views/campos_event_participant.xml',
    ],
    'demo': [
    ],
}
