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
                'campos_final_registration',
    ],
    'data': [
        'wizards/campos_activity_mass_signup_wiz.xml',
        'views/event_registration.xml',
        'wizards/campos_activity_signup_wiz.xml',
        'security/campos_activity_activity.xml',
        'views/campos_activity_activity.xml',
        'security/campos_activity_pitag.xml',
        'views/campos_activity_pitag.xml',
        'security/campos_activity_location.xml',
        'views/campos_activity_location.xml',
        'security/campos_activity_tag.xml',
        'views/campos_activity_tag.xml',
        'security/campos_activity_ticket.xml',
        'views/campos_activity_ticket.xml',
        'security/campos_activity_instanse.xml',
        'views/campos_activity_instanse.xml',
        'security/campos_activity_period.xml',
        'views/campos_activity_period.xml',
        'security/campos_activity_audience.xml',
        'views/campos_activity_audience.xml',
        'security/campos_activity_type.xml',
        'views/campos_activity_type.xml',
        'views/campos_event_participant.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
