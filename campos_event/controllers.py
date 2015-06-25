# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of CampOS Event, an Odoo module.
#
#     Copyright (c) 2015 Stein & Gabelgaard ApS
#                        http://www.steingabelgaard.dk
#                        Hans Henrik Gaelgaard
#
#     CampOS Event is free software: you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     CampOS Event is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with CampOS Event.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import http

# class CampOsEvent(http.Controller):
#     @http.route('/camp_os_event/camp_os_event/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/camp_os_event/camp_os_event/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('camp_os_event.listing', {
#             'root': '/camp_os_event/camp_os_event',
#             'objects': http.request.env['camp_os_event.camp_os_event'].search([]),
#         })

#     @http.route('/camp_os_event/camp_os_event/objects/<model("camp_os_event.camp_os_event"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('camp_os_event.object', {
#             'object': obj
#         })
