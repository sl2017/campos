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


from openerp import tools
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as controllers
from openerp.addons.website.models.website import slug

class CampOsEvent(http.Controller):
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

    @http.route('/campos/jobber/signup', type='http', auth="public", website=True)
    def jobber_signup(self, **kwargs):
        error = {}
        default = {}
        
        committee = request.registry['campos.committee']
        committee_ids = committee.search(request.cr, SUPERUSER_ID, [], context=request.context)
        committees = committee.browse(request.cr, SUPERUSER_ID, committee_ids, context=request.context)
        
        if 'website_campos_jobber_signup_error' in request.session:
            error = request.session.pop('website_campos_jobber_signup_error')
            default = request.session.pop('website_campos_jobber_signup_default')
            
        return request.render("campos_event.jobber_signup", {
            'committees': committees,
            'error': error,
            'default': default,
        })
        
        
    @http.route('/campos/jobber/thankyou', methods=['POST'], type='http', auth="public", website=True)
    def jobs_thankyou(self, **post):
        error = {}
        for field_name in ["name", "phone", "email"]:
            if not post.get(field_name):
                error[field_name] = 'missing'
        if error:
            request.session['website_campos_jobber_signup_error'] = error
            
            request.session['website_campos_jobber_signup_default'] = post
            return request.redirect('/campos/jobber/signup')

        # public user can't create applicants (duh)
        env = request.env(user=SUPERUSER_ID)
        value = {
            'staff' : True,
            'scoutgroup': False,
            'participant' : False,
             
        }
        for f in ['email', 'name', 'phone']:
            value[f] = post.get(f)
        
        partner_id = env['res.partner'].create(value).id
        
        value = {
                 'event_id' : 1,
                 'partner_id' : partner_id,
                 'contact_partner_id' : partner_id,
                 'econ_partner_id' : partner_id,
                 
                 } 
        reg_id = env['event.registration'].create(value).id
        value = {
                 'partner_id' : partner_id,
                 'registration_id' : reg_id,
                 }
        for f in ['workwish', 'committee_id']:
            value[f] = post.get(f)
        
        part_id = env['campos.event.participant'].create(value).id
        return request.render("campos_event.jobber_thankyou", {})    