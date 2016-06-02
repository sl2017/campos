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

    @http.route(['/event/<model("event.event"):event>/register/register_meeting'],
                type='http', auth="user", website=True)
    def event_register_meeting(self, event, **post):
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
            registration = reg_obj.suspend_security().search([('event_id', '=', registration_vals['event_id']), ('partner_id', '=', http.request.env.user.partner_id.id) ])
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



    @http.route(['/event/<model("event.event"):event>/register/intl_groups'],
                type='http', auth="public", website=True)
    def event_register_intl_groups(self, event, **post):
        def validate(name, force_check=False):
            return self._validate(name, post, force_check=force_check)

        error = {}
        reg_obj = http.request.env['event.registration']
        registration_vals = {}
        post['name'] = post.get('group_name', '')
        post['email'] = post.get('contact_email', '')
        post['phone'] = post.get('contact_mobile', '')
        post['tickets'] = '1'
        if (http.request.env.ref('base.public_user') !=
                http.request.env.user and
                validate('tickets', force_check=True)):
            # if logged in, use that info
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id,
                partner=http.request.env.user.partner_id)

        if all(map(lambda f: validate(f, force_check=True),
                   ['name', 'email', 'tickets'])):
            # otherwise, create a simple registration
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id)
        _logger.info("Reg: %s - post: %s", registration_vals, post)
        if http.request.httprequest.method == 'POST' and registration_vals:
            partner_obj = http.request.env['res.partner']
            group = partner_obj.sudo().create({'name': post.get('name'),
                                               'scoutgroup': True})
            registration_vals['partner_id'] = group.id
            for f in ['country_id', 'intl_org', 'natorg', 'friendship']:
                registration_vals[f] = post.get('group_%s' % (f), False)
            for f in ['scout_qty_pre_reg', 'leader_qty_pre_reg']:
                registration_vals[f] = int(post.get('group_%s' % (f), '0'))
            cvals = {}
            post['contact_country_id'] = post.get('group_country_id', False)
            for f in ['name', 'email', 'mobile', 'street', 'zip', 'city', 'country_id', 'lang']:
                cvals[f] = post.get('contact_%s' % (f), False)
            contact = partner_obj.sudo().create(cvals)
            registration_vals['contact_partner_id'] = contact.id
            registration = reg_obj.sudo().create(registration_vals)

            if registration.partner_id:
                registration._onchange_partner()
            registration.registration_open()
            return http.request.render(
                'website_event_register_free.partner_register_confirm',
                {'registration': registration})

        countries = http.request.env['res.country'].search([])
        intl_orgs = http.request.env['campos.scout.org'].search([('country_id', '=', False)])
        languages = http.request.env['res.lang'].search([])
        values = {
            'event': event,
            'range': range,
            'countries': countries,
            'intl_orgs': intl_orgs,
            'tickets': post.get('tickets', 1),
            'validate': validate,
            'post': post,
            'languages': languages,
            'error': error,
        }
        return http.request.render(
            'campos_event.intl_groups_register_form', values)

