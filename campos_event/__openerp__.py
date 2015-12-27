# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Event,
#     an Odoo module.
#
#     Copyright (c) 2015 Stein & Gabelgaard ApS
#                        http://www.steingabelgaard.dk
#                        Hans Henrik Gaelgaard
#
#     CampOS Event is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     CampOS Event is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with CampOS Event.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "CampOS Event",

    'summary': """
                Scout Camp Management Solution""",

    # 'description': put the module description in README.rst

    'author': "Hans Henrik Gabelgaard",
    'website': "http://www.steingabelgaard.dk",

    # Categories can be used to filter modules in modules listing
    # Check http://goo.gl/0TfwzD for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'event',
        'website',
        'portal',
        'survey',
        'website_event_register_free',
        'base_suspend_security',
        
    ],

    # always loaded
    'data': [
        'security/campos_event_security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.csv',
        
        'data/campos.municipality.csv',
        'data/campos.scout.org.csv',
        
        'views/templates.xml',
        'views/participant_view.xml',
        'views/committee_view.xml',
        'views/municipality_view.xml',
        "views/scout_org_view.xml",
        "views/res_partner_view.xml",
        "views/job_view.xml",
        "views/job_template.xml",
        "views/mail_templates.xml",
        "views/confirm_template.xml",
        "views/event_view.xml",
        #"views/portal_menu.xml",
        "views/res_users_view.xml",
        'views/campos_menu.xml',
        'views/event_partner_reg_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
