# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Pre-registration,
#     an Odoo module.
#
##############################################################################
{
    'name': "CampOS Preregistration",

    'summary': """Scout Camp Preregistration Module""",

    'description': """Scout Camp Preregistration Module""",

    'author': "Jeppe Axelsen, Ernst Madsen",

    # Categories can be used to filter modules in modules listing
    # Check http://goo.gl/0TfwzD for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['campos_event'],

    # always loaded
    'data': ['views/preregistration.xml',
             'views/mail_templates.xml',
             'security/campos_preregistration_security.xml',
             'security/ir.model.access.csv',
             'security/ir.rule.csv',
             ],
    # only loaded in demonstration mode
    'demo': [ ],
}
