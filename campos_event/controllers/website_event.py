# -*- coding: utf-8 -*-

import openerp
from openerp import http, _
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

    @http.route(['/event/<model("event.event"):event>/register/register_meeting',
                 '/event/<model("event.event"):event>/register/register_free'],
                type='http', auth="user", website=True)
    def event_register_free(self, event, **post):
        # TODO: Rename back: def event_register_meeting(self, event, **post):
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
                vals['reg_organization_id'] = int(post.get('reg_organization_id', False))

                _logger.info('Par val: %s', vals)
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
            post['reg_organization_id'] = str(http.request.env.user.participant_id.reg_organization_id.id)

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
            # 'reg_organization_id' : reg_organization_id
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
        _logger.info("Post? %s", http.request.httprequest.method)
        if post.get('group_name', False):
            post['name'] = post.get('group_name', '')
            post['email'] = post.get('contact_email', '')
            post['phone'] = post.get('contact_mobile', '')
            post['tickets'] = '1'
        if http.request.httprequest.method == 'POST' and (http.request.env.ref('base.public_user') !=
                http.request.env.user and
                validate('name', force_check=True)):
            # if logged in, use that info
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id,
                partner=http.request.env.user.partner_id)

        if http.request.httprequest.method == 'POST' and all(map(lambda f: validate(f, force_check=True),
                   ['name', 'email', 'tickets'])):
            # otherwise, create a simple registration
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id)
        _logger.info("Reg: %s - post: %s", registration_vals, post)

        if http.request.httprequest.method == 'POST' and registration_vals:
            partner_obj = http.request.env['res.partner']
            group = partner_obj.sudo().create({'name': post.get('name'),
                                               'scoutgroup': True,
                                               'country_id': post.get('group_country_id', False),
                                               })
            registration_vals['partner_id'] = group.id
            for f in ['intl_org', 'natorg', 'friendship']:
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

    @http.route(['/event/<model("event.event"):event>/register/dk_groups/<scout_org_id>',
                 '/event/<model("event.event"):event>/register/dk_groups'],
                type='http', auth="public", website=True)
    def event_register_dk_groups(self, event, scout_org_id=None, **post):
        def validate(name, force_check=False):
            return self._validate(name, post, force_check=force_check)

        error = {}
        reg_obj = http.request.env['event.registration']
        partner_obj = http.request.env['res.partner']
        group = False
        registration_vals = {}
        _logger.info("Post? %s", http.request.httprequest.method)
        if post.get('group_name', False):
            post['name'] = post.get('group_name', '')
            post['email'] = post.get('contact_email', '')
            post['phone'] = post.get('contact_mobile', '')
            post['tickets'] = '1'
        elif post.get('group_partner_id', False):
            group = partner_obj.sudo().browse(int(post.get('group_partner_id', False)))
            post['name'] = group.name
            post['email'] = post.get('contact_email', '')
            post['phone'] = post.get('contact_mobile', '')
            post['tickets'] = '1'
        if http.request.httprequest.method == 'POST' and (http.request.env.ref('base.public_user') !=
                http.request.env.user and
                validate('name', force_check=True)):
            # if logged in, use that info
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id,
                partner=http.request.env.user.partner_id)

        if http.request.httprequest.method == 'POST' and all(map(lambda f: validate(f, force_check=True),
                   ['name', 'email', 'tickets'])):
            # otherwise, create a simple registration
            registration_vals = reg_obj._prepare_registration(
                event, post, http.request.env.user.id)
        _logger.info("Reg: %s - post: %s", registration_vals, post)

        if http.request.httprequest.method == 'POST' and registration_vals:
            if not group:
                group = partner_obj.sudo().create({'name': post.get('name'),
                                                   'scoutgroup': True,
                                                   'country_id': post.get('group_country_id', False),
                                                   'scoutorg_id': post.get('scoutorg_id', False),
                                                   'is_company': True,
                                                   })
            registration_vals['partner_id'] = group.id
            registration_vals['organization_id'] = group.scoutorg_id.id
            for f in ['intl_org', 'natorg']:
                registration_vals[f] = post.get('group_%s' % (f), False)
            cvals = {}
            post['contact_country_id'] = group.country_id.id
            for f in ['name', 'email', 'mobile', 'street', 'zip', 'city', 'country_id', 'lang']:
                cvals[f] = post.get('contact_%s' % (f), False)
            cvals['parent_id'] = group.id
            contact = partner_obj.sudo().create(cvals)
            registration_vals['contact_partner_id'] = contact.id
            registration = reg_obj.sudo().create(registration_vals)

            if registration.partner_id:
                registration._onchange_partner()
            registration.registration_open()
            new_user = reg_obj.env['res.users'].sudo().create({'login':contact.email,
                                                            'partner_id': contact.id,
                                                            'groups_id': [(4, partner_obj.env.ref('campos_preregistration.group_campos_groupleader').id)],
                                                            'action_id': int(http.request.env['ir.config_parameter'].get_param('campos_event.group_login_home_action'))
                                                         })
            return http.request.render(
                'website_event_register_free.partner_register_confirm',
                {'registration': registration})

        countries = http.request.env['res.country'].search([])
        scoutorgs = http.request.env['campos.scout.org'].sudo().search([('country_id.code', '=', 'DK')])
        languages = http.request.env['res.lang'].search([])
        groups = False
        if scout_org_id:
            groups = http.request.env['res.partner'].sudo().search([('scoutorg_id', '=', int(scout_org_id)),('scoutgroup', '=', True)])
        if not post.get('group_country_id', False):
            post['group_country_id'] = http.request.env.ref('base.dk').id
        if not post.get('contact_lang', False):
            post['contact_lang'] = 'da_DK'
        _logger.info('POST: %s', post)
        _logger.info('GROUPS: %s', groups)

        pagetitle = _('Preregistration for Danish Groups')        
        if scout_org_id:
            scoutorg = http.request.env['campos.scout.org'].sudo().browse(int(scout_org_id))
            pagetitle = _('Preregistration for %s') % scoutorg.name
            
        values = {
            'event': event,
            'range': range,
            'countries': countries,
            'scoutorgs': scoutorgs,
            'tickets': post.get('tickets', 1),
            'validate': validate,
            'post': post,
            'languages': languages,
            'error': error,
            'groups': groups,
            'scout_org_id': scout_org_id,
            'pagetitle': pagetitle,
        }
        return http.request.render(
            'campos_event.dk_groups_register_form', values)


    @http.route(['''/event/<model("event.event"):event>/meeting_proposal'''], type='http', auth="user", website=True)
    def event_meeting_proposal(self, event, **post):
        all_comms = http.request.env['campos.committee'].search(['|', ('parent_id', '=', False),('parent_id.parent_id', '=', False)])
        comm_ids = [jf.committee_id.id for jf in http.request.env.user.participant_id.jobfunc_ids]
        _logger.info("My comms: %s", comm_ids)
        my_comms = http.request.env['campos.committee'].search([('id', 'in', comm_ids)])
        values = { 'event': event,
                   'all_comms': all_comms,
                   'my_comms': my_comms}
        return http.request.website.render("campos_event.event_meeting_proposal", values)

    @http.route(['/event/<model("event.event"):event>/meeting_proposal/post'], type='http', auth="user", methods=['POST'], website=True)
    def event_meeting_proposal_post(self, event, **post):
        cr, uid, context = http.request.cr, http.request.uid, http.request.context

        tobj = http.request.registry['event.track']

        tags = []
        for tag in event.allowed_track_tag_ids:
            if post.get('tag_'+str(tag.id)):
                tags.append(tag.id)

        e = openerp.tools.escape
        track_description = post['description']

        track_id = tobj.create(cr, openerp.SUPERUSER_ID, {
            'name': post['track_name'],
            'event_id': event.id,
            'tag_ids': [(6, 0, tags)],
            'user_id': uid,
            'description': track_description,
            'req_comm_id': post['req_comm_id'],
            'wanted_comm_id': post['wanted_comm_id'],
            'wanted_people': post['wanted_people'],
            'duration' : float(post['duration']) / 60.0,
        }, context=context)

        track = tobj.browse(cr, uid, track_id, context=context)
        values = {'track': track, 'event':event}
        return http.request.website.render("campos_event.event_meeting_proposal_success", values)
