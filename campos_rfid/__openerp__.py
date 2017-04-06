# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CampOS RFID',
    'description': """
        CampOS RFID Interface""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': ['mail', 'campos_jobber_final'
    ],
    'data': [
        'security/campos_rfid_device.xml',
        'views/campos_rfid_device.xml',
    ],
    'demo': [
    ],
}
