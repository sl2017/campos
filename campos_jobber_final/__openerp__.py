# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CampOS Jobber Final',
    'description': """
        Final registration for jobbers""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': ['campos_final_registration'],
    'data': [
        'security/campos_jobber_accom_group.xml',
        'views/campos_jobber_accom_group.xml',
        'views/campos_committee.xml',
        'security/campos_jobber_accom_type.xml',
        'views/campos_jobber_accom_type.xml',
        'security/campos_jobber_canteen.xml',
        'views/campos_jobber_canteen.xml',
        'security/campos_canteen.xml',
        'views/campos_canteen.xml',
        'views/event_registration.xml',
        'security/campos_jobber_accomodation.xml',
        #'views/campos_jobber_accomodation.xml',
        'views/campos_event_participant.xml',
    ],
    'demo': [
    ],
}
