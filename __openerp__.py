# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    "name" : "dds_camp",
    "version" : "1.0",
    "author" : "Hans Henrik Gabelgaard",
    "website" : "http://www.blushoejspejderne.dk/",
    "category" : "Generic Modules/Others",
    "depends" : ["base", "event", "mail","better_zip","portal","report_xls"],
    "description" : "DDS Camp",
    "init_xml" : [],
    "demo_xml" : [],
    'data': [
             #'security/ir.model.access.csv',
             ],
    "update_xml" : ["dds_camp_view.xml",
                    "event_view.xml",
                    
                    "wizard/bmimport_view.xml",
                    "portal_view.xml", 
                    "wizard/portal_wizard.xml",
                    "report/participants_list_xls.xml",
		      "wizard/welcome_view.xml"
                    ],
    "installable": True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
