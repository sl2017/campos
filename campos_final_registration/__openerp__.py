# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Pre-registration,
#     an Odoo module.
#
##############################################################################
{
    'name': "CampOS Final Registration",

    'summary': """Scout Camp Final Registration Module""",

    'description': """Scout Camp Final Registration Module""",

    'author': "Ernst Madsen",

    # Categories can be used to filter modules in modules listing
    # Check http://goo.gl/0TfwzD for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['campos_preregistration'],

    # always loaded
    'data': ['views/finalregistration.xml'],
    # only loaded in demonstration mode
    'demo': [ ],
}
