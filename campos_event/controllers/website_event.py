# -*- coding: utf-8 -*-

from openerp import http
from openerp.addons.website_event_register_free.controllers.website_event import WebsiteEvent

import logging

_logger = logging.getLogger(__name__)

CONFIRM_FIELDS = ['name', 'email', 'phone']

class WebsiteEventEx(WebsiteEvent):

    @http.route(['/event/<model("event.event"):event>/register/register_free'],
                type='http', auth="user", website=True)
    def event_register_free(self, event, **post):
        def validate(name, force_check=False):
            return self._validate(name, post, force_check=force_check)

        reg_obj = http.request.env['event.registration']
        registration_vals = {}
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
            registration = reg_obj.sudo().create(registration_vals)
            if registration.partner_id:
                registration._onchange_partner()
            if (http.request.env.ref('base.public_user') !=
                http.request.env.user and http.request.env.user.participant_id):
                vals = {}
                for f in CONFIRM_FIELDS:
                    vals[f] = post.get(f)
                http.request.env.user.participant_id.write(vals)
            #registration.registration_open()
            if registration.event_id.survey_id:
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
                
        values = {
            'event': event,
            'range': range,
            'tickets': post.get('tickets', 1),
            'validate': validate,
            'post': post,
        }
        return http.request.render(
            'campos_event.partner_register_form', values)
