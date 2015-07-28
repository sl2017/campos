# -*- coding: utf-8 -*-
##############################################################################
#
#    CampOS Setup
#    Copyright (C) 2015 Hans Henrik Gabelgaard
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': "CampOS Standard Setup",

    'summary': """
        Our Standard Odoo Config""",

    'description': """
        Loads Danish as secondary languages
        Enables "Technical features" for Administrator and sets the timezone
        to Europe/Copenhagen
        Removes the Odoo online bindings

        Requires the following OCA repos:
            server-tools


    """,

    'author': "Hans Henrik Gabelgaard",
    'website': "dk.linkedin.com/in/hanshenrikgabelgaard",


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'disable_openerp_online',
                'admin_technical_features',
                'campos_event',
                ],

    # always loaded
    'data': [
        'lang.xml',
    ],
    'application': True,
}
