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


from openerp import tools, fields
from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.web.http import request
from openerp.addons.website.controllers.main import Website as controllers
from openerp.addons.website.models.website import slug
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


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

    @http.route(
        ['/campos/jobber/signup',
         '/campos/jobber/signup/<model("campos.job"):job>'],
        type='http', auth="public", website=True)
    def jobber_signup(self, job=None, **kwargs):
        error = {}
        default = {'staff_qty_pre_reg': '1'}
        comm_id = False
        scoutorg_id = False
        
        if job:
            comm_id = job.committee_id.id

        committee = request.registry['campos.committee']
        committee_ids = committee.search(
            request.cr,
            SUPERUSER_ID,
            ['|',('website_published', '=', True),('id', '=', comm_id)],
            context=request.context)
        committees = committee.browse(
            request.cr,
            SUPERUSER_ID,
            committee_ids,
            context=request.context)

        scout_org = request.registry['campos.scout.org']
        scout_org_ids = scout_org.search(
            request.cr,
            SUPERUSER_ID,
            [('country_id.code', '=', 'DK')],
            context=request.context)
        scoutorgs = scout_org.browse(
            request.cr,
            SUPERUSER_ID,
            scout_org_ids,
            context=request.context)

        if 'website_campos_jobber_signup_error' in request.session:
            error = request.session.pop('website_campos_jobber_signup_error')
            default = request.session.pop(
                'website_campos_jobber_signup_default')

        return request.render("campos_event.jobber_signup", {
            'committees': committees,
            'error': error,
            'default': default,
            'job' : job,
            'comm_id' : comm_id,
            'scoutorgs' : scoutorgs,
            'scoutorg_id': scoutorg_id,
        })

    @http.route('/campos/jobber/thankyou',
                methods=['POST'], type='http', auth="public", website=True)
    def jobs_thankyou(self, **post):
        error = {}
        for field_name in ["name", "email", "street", "zip", "city"]:
            if not post.get(field_name):
                error[field_name] = 'Missing %s' % field_name
        if not (post.get('phone') or post.get('mobile')):
                error['phone'] = 'Missing phone or mobile number'
                error['mobile'] = 'At least one of phone or mobile is neesed '
        if error:
            request.session['website_campos_jobber_signup_error'] = error

            request.session['website_campos_jobber_signup_default'] = post
            return request.redirect('/campos/jobber/signup')

        # public user can't create applicants (duh)
        env = request.env(user=SUPERUSER_ID)
        value = {
            'staff': True,
            'scoutgroup': False,
            'participant': False,
        }
        for f in ['email', 'name', 'phone', 'street', 'zip', 'city', 'mobile','skype']:
            value[f] = post.get(f)
        partner_id = env['res.partner'].create(value).id

        value = {
            'event_id': 1,
            'partner_id': partner_id,
            'contact_partner_id': partner_id,
            'econ_partner_id': partner_id,
        }
        for f in ['name', 'organization_id', 'staff_qty_pre_reg']:
            value[f] = post.get(f)
        reg_id = env['event.registration'].create(value).id

        value = {
            'partner_id': partner_id,
            'registration_id': reg_id,
            'state' : 'reg',
        }
        for f in ['committee_id', 'job_id', 'my_comm_contact', 'qualifications', 'workas_planner', 'workas_jobber']:
            value[f] = post.get(f)
        if post.get('job_id'):
            job = env['campos.job'].suspend_security().browse(int(post.get('job_id')))
            if job:
                value['committee_id'] = job.committee_id.id
        if post.get('workas_both'):
            value['workas_planner'] = True
            value['workas_jobber'] = True
        part = env['campos.event.participant'].create(value)
        
        template = part.env.ref('campos_event.request_signupconfirm')
        assert template._name == 'email.template'
        try:
            template.send_mail(part.id)
        except:
            pass

        return request.render("campos_event.jobber_thankyou", {'par': part})


    @http.route(
        ['/campos/jobber/joblist',
         '/campos/jobber/joblist/<model("campos.job.tag"):tag>',
         '/campos/jobber/jobcom/<model("campos.committee"):comm>'], 
         type='http', auth="public", website=True)
    def jobber_joblist(self, tag=None, comm=None,  search=None, **kwargs):
        request = http.request
        
        if tag:
            jobs = tag.job_ids
            list_title = _("Jobs tagged: ") + tag.name
        elif comm:
            jobs = request.env['campos.job'].search([('active','=', True),('openjob', '=', True), '|',('committee_id', '=', comm.id),('committee_id', 'child_of', comm.id)])
            list_title = _("Jobs for: ") + comm.name
        elif search:
            jobs = request.env['campos.job'].search([('active','=', True),('openjob', '=', True), '|','|','|','|',('name', 'ilike', search),('teaser', 'ilike', search),('desc', 'ilike', search),('committee_id.display_name', 'ilike', search), ('tag_ids.name', 'ilike', search)])
            list_title = _("Search Result")
        
        else:
            jobs = request.env['campos.job'].search([('active','=', True),('openjob', '=', True)], order='write_date DESC')
            list_title = _("Ledige job")
            
        for j in jobs:
            _logger.info("job %s %s", j.name, j.openjob)
        jobs = jobs.filtered(lambda r: r.openjob == True)
        nav_tags = request.env['campos.job.tag'].search([])
        nav_tags = nav_tags.filtered(lambda r: any([j.openjob for j in r.job_ids]))
        nav_comm = request.env['campos.committee'].search([('parent_id', '=', False),('website_published', '=', True)])
            
        return request.render("campos_event.jobber_latest_jobs", {'jobs' : jobs,
                                                                  'list_title' : list_title,
                                                                  'nav_tags' : nav_tags,
                                                                  'nav_comm' : nav_comm})    
        
    @http.route(
        ['/campos/jobber/view/<model("campos.job"):job>'],
        type='http', auth="public", website=True)
    def jobber_jobview(self, job=None, **kwargs):
        nav_tags = request.env['campos.job.tag'].search([])
        nav_tags = nav_tags.filtered(lambda r: any([j.openjob for j in r.job_ids]))
        nav_comm = request.env['campos.committee'].search([('parent_id', '=', False),('website_published', '=', True)])
        return request.render("campos_event.jobber_job_view", {'job' : job,
                                                               'nav_tags' : nav_tags,
                                                               'nav_comm' : nav_comm})   
        
        
        
    @http.route(
        ['/campos/confirm/<mode>/<token>'],
         type='http', auth="public", website=True)
    def confirm_reg(self, mode=None, token=None, **kwargs):
        request = http.request
        error = {}
        default = {}
        
        if token:
            _logger.info("Token %s", token)
            par = request.env['campos.event.participant'].sudo().search([('confirm_token', '=', token)])
            if len(par) == 1:
                if mode == 'reg':
                    if par.state == 'reg':
                        par.sudo().state = 'draft'
                    return request.render("campos_event.reg_confirmed", {'par': par})
                if mode == 'zx':
                    return request.render("campos_event.zx_confirm_prompt", {'par': par,
                                                                             'mode': mode,
                                                                             'token': token,
                                                                             'error': error,
                                                                             'default': default,
                                                                             })
                if mode == 'sp':
                    return request.render("campos_event.sp_confirm_prompt", {'par': par,
                                                                             'mode': mode,
                                                                             'token': token,
                                                                             'error': error,
                                                                             'default': default,
                                                                             })
                    
        return request.render("campos_event.unknown_token")
    
    @http.route(
        ['/campos/submit/confirm/<mode>'],
         type='http', auth="public", website=True)
    def confirm_submit(self, mode=None, **post):
        request = http.request
        fieldlist = {'sp': ['sharepoint_mailaddress'], 
                     'zx': ['zexpense_firsttime_pwd']}
        datefield = {'sp': 'sharepoint_mail_created', 
                     'zx': 'zexpense_access_created'}
        
        env = request.env(user=SUPERUSER_ID)
        
        if post:
            _logger.info('Confirm par: %d', post.get('par_id'))
            par = env['campos.event.participant'].browse(int(post.get('par_id')))
            values = {}
            for f in fieldlist[mode]:
                values[f] = post.get(f)
            values[datefield[mode]] = fields.Date.today()
            _logger.info("Confirm par val %s", values)
            par.write(values)
            
            return request.render("campos_event.participant updated", {'par': par})
        return request.render("campos_event.unknown_token")

    
    @http.route(['/campos/jobber/ask', 
                 '/campos/jobber/ask/<model("campos.job"):job>'],
                type='http', auth="public", website=True)
    def jobs_ask(self, job=None, **post):
        error = {}
        default = {}
        if post:
            for field_name in ["name", "email", "description"]:
                if not post.get(field_name):
                    error[field_name] = 'Missing %s' % field_name
                default[field_name] = post.get(field_name, False)
                     
            if not error:
            
                # public user can't create applicants (duh)
                env = request.env(user=SUPERUSER_ID)
                job = env['campos.job'].search([('id', '=', int(post.get('job_id')))])
                
                if job.par_contact_id:
                    user = env['res.users'].sudo().search([('participant_id', '=', job.par_contact_id.id)]).id
                else:
                    user = False
                value = {
                    'name': "WEB Question re %s" % job.name,
                    'email_from': "%s <%s>" % (post.get('name'), post.get('email')),
                    'description': post.get('description'),
                    'project_id': env.ref('campos_event.project_job_ask').id,
                    'user_id': user,
                    'model_reference': '%s,%d' % ('campos.job', job.id)
                }
                env['project.issue'].create(value)
                return request.render("campos_event.jobber_job_ask_thankyou")
        
        return request.render("campos_event.jobber_job_ask", {'error': error,
                                                              'default': default,
                                                              'job': job,})
