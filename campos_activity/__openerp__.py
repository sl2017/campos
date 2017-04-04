# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Campos Activity',
    'description': """
        CampOS Activity Planning and Booking""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': [ 'mail', 
                'campos_event',
    ],
    'data': [
        'security/campos_activity_ticket.xml',
        #'views/campos_activity_ticket.xml',
        'security/campos_activity_instanse.xml',
        #'views/campos_activity_instanse.xml',
        'security/campos_activity_period.xml',
        #'views/campos_activity_period.xml',
        'security/campos_activity_activity.xml',
        #'views/campos_activity_activity.xml',
    ],
    'demo': [
    ],
}
