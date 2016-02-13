# -*- coding: utf-8 -*-

from openerp import http
from openerp.addons.website_event_register_free.controllers.website_event import WebsiteEvent

import datetime
import logging

_logger = logging.getLogger(__name__)

CONFIRM_FIELDS = ['name', 'email', 'phone', 'mobile', 'street', 'street2', 'zip', 'city', 'skype', 'reg_organization_id', 'birthdate']

class WebsiteEventEx(WebsiteEvent):
    
    def _validate(self, name, post, force_check=False):
        if name in post or force_check:
            if name == 'name' and not post.get('name', '').strip():
                return False
            if name == 'email' and not post.get('email', '').strip():
                return False
            if name == 'tickets' and (
                    not post.get('tickets', '').isdigit() or
                    int(post.get('tickets')) <= 0):
                return False
            if name == 'birthdate' and post.get('birthdate'):
                try:
                    datetime.datetime.strptime(post.get('birthdate'), '%Y-%m-%d')
                except ValueError:
                    return False
        return True

    @http.route(['/event/<model("event.event"):event>/register/register_free'],
                type='http', auth="user", website=True)
    def event_register_free(self, event, **post):
        def validate(name, force_check=False):
            return self._validate(name, post, force_check=force_check)

        reg_obj = http.request.env['event.registration']
        registration_vals = {}
        reg_organization_id = False
        noshow = True if post.get('action', False) == 'noshow' else False
        if (http.request.env.ref('base.public_user') !=
                http.request.env.user and
                validate('tickets', force_check=True)):
            # if logged in, use that info
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id,
                partner=http.request.env.user.partner_id)
        elif all(map(lambda f: validate(f, force_check=True),
                   ['name', 'email', 'tickets'])):
            # otherwise, create a simple registration
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id)
        if registration_vals and post.get('name', False):
            # TOD Handle re-registrations 
            registration = reg_obj.suspend_security().search([('event_id', '=', registration_vals['event_id']),('partner_id', '=', http.request.env.user.partner_id.id ) ])
            if not registration:
                if noshow:
                    registration_vals['state'] = 'cancel'
                registration = reg_obj.suspend_security().create(registration_vals)
            else:
                registration = registration[0]
            if registration.partner_id:
                registration._onchange_partner()
            if (http.request.env.ref('base.public_user') !=
                http.request.env.user and http.request.env.user.participant_id):
                vals = {}
                for f in CONFIRM_FIELDS:
                    vals[f] = post.get(f)
                http.request.env.user.participant_id.write(vals)
            if noshow:
                registration.state = 'cancel'
            else:
                registration.registration_open()
            if registration.event_id.survey_id and not noshow:
                if registration.reg_survey_input_id:
                    user_input = registration.reg_survey_input_id
                    user_input.state = 'new'
                else:
                    user_input = http.request.env['survey.user_input'].create({'survey_id': registration.event_id.survey_id.id,
                                                                           'partner_id': http.request.env.user.partner_id.id})
                    registration.reg_survey_input_id = user_input
                return http.request.redirect('/survey/fill/%s/%s' % (registration.event_id.survey_id.id, user_input.token))
            else:
                return http.request.render(
                    'website_event_register_free.partner_register_confirm',
                    {'registration': registration})
        
        if (http.request.env.ref('base.public_user') !=
                http.request.env.user and http.request.env.user.participant_id):
            for f in CONFIRM_FIELDS:
                post[f] = getattr(http.request.env.user.participant_id, f)
            reg_organization_id = http.request.env.user.participant_id.reg_organization_id.id
                
        scoutorgs = http.request.env['campos.scout.org'].sudo().search(
            [('country_id.code', '=', 'DK')])
        
        _logger.info('Post: %s', post)
        values = {
            'event': event,
            'range': range,
            'tickets': post.get('tickets', 1),
            'validate': validate,
            'post': post,
            'scoutorgs' : scoutorgs,
            'reg_organization_id' : reg_organization_id
        }
        return http.request.render(
            'campos_event.partner_register_form', values)
