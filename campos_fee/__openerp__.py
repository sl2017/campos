# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Campos Fee',
    'description': """
        CampOS Fee Calculations""",
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Stein & Gabelgaard ApS',
    'website': 'www.steingabelgaard.dk',
    'depends': [
        'campos_event',
        'campos_final_registration',
    ],
    'data': [
        'views/campos_municipality.xml',
        'security/campos_fee_agegroup.xml',
        'views/campos_fee_agegroup.xml',
        'views/event_registration.xml',
        'views/campos_event_participant.xml',
        'data/product.attribute.csv',
        'data/product.attribute.value.csv',
        'data/campos.municipality.csv',
    ],
    'demo': [
    ],
}
