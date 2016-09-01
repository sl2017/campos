# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


import logging
import traceback

_logger = logging.getLogger(__name__)



class CamposWelcomeProfile(models.TransientModel):

    _name= 'campos.welcome.profile'
    
    user_id = fields.Many2one('res.users', 'Welcome Wizard')
    name = fields.Char()
    org_int_id = fields.Integer('Remote Res ID')
    org_ext_id = fields.Char('Remote Ext ID')
    profile_id = fields.Char('Remote Profile ID')
    wiz_id = fields.Many2one('campos.welcome', 'Welcome Wizard')
    


class CamposWelcome(models.TransientModel):

    _name = 'campos.welcome'

    name = fields.Char('Your Name')
    profile_id = fields.Many2one('campos.welcome.profile', 'Scout group')
    remote_system_id = fields.Many2one('campos.remote.system', 'Logged in by')
    state = fields.Selection([('welcome', 'Welcome'),
                              ('select', 'Group Selection'),
                              ('done', 'Completed')], 'State', default='welcome')
    message = fields.Char()
    reg_id = fields.Many2one('event.registration')

    @api.model
    def default_get(self, fields):
        result = super(CamposWelcome, self).default_get(fields)
        pro_id = False
        remote_system_id = self.env['campos.remote.system'].getRemoteSystem() 
#         profiles = remote_system_id.getProfiles(self.env.user.oauth_uid)
#         cwpro = self.env['campos.welcome.profile']
#         for pro in profiles:
#             _logger.info("Profile: %s", pro)
#             pro_id = cwpro.create(pro)
#         
#         result['profile_id'] = pro_id.id
        result['remote_system_id'] = remote_system_id.id
        result['name'] = self.env.user.name 
        if self.env.user.partner_id.remote_system_id:
            #Already imported - Go to "Done"
            result['state'] = 'done'
            event_id = self.env['ir.config_parameter'].get_param('campos_welcome.event_id')
            _logger.info('EVent: %s', event_id)
            if event_id:
                event_id = int(event_id)
                reg = self.env['event.registration'].search([('partner_id', '=', self.env.user.partner_id.id), ('event_id', '=', event_id)])
                if reg:
                    result['reg_id'] = reg.id
                    result['message'] = _('Your group has already been signed up')
                    self.env.user.action_id = False
        return result



    @api.multi
    def do_reopen_form(self):
        self.ensure_one()
        return {
                'name': _('Welcome to SL2017 Group Pre-registration'),
                'type': 'ir.actions.act_window',
                'res_model': self._name, # this model
                'res_id': self.id, # the current wizard record
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'}

    @api.multi
    def doit_welcome(self):
        for wizard in self:
            member_number, profiles = wizard.remote_system_id.getProfiles(wizard.remote_system_id.getRemoteUID())
            cwpro = self.env['campos.welcome.profile']
            for pro in profiles:
                _logger.info("Profile: %s", pro)
                pro['wiz_id'] = wizard.id
                pro_id = cwpro.create(pro)
            self.env.user.partner_id.write({'remote_ext_id': member_number,
                                            'remote_int_id': self.env.user.oauth_uid,
                                            'remote_system_id': wizard.remote_system_id.id,
                                            'remote_link_id': wizard.profile_id.profile_id,
                                            })
            wizard.profile_id = pro_id.id
            wizard.state = 'select'

        return self.do_reopen_form()

    @api.multi
    def doit_select(self):
        for wizard in self:
            event_id = self.env['ir.config_parameter'].get_param('campos_welcome.event_id')
            _logger.info('EVent: %s', event_id)
            if event_id:
                event_id = int(event_id)
            group = self.env['res.partner'].search([('remote_int_id', '=', wizard.profile_id.org_int_id),('remote_system_id', '=', wizard.remote_system_id.id)])
            if group:
                wizard.message = "%s has already been signed up - Skipping Group import"
                wizard.reg_id = self.env['event.registration'].search([('partner_id', '=', group.id), ('event_id', '=', event_id)])
                self.env.user.partner_id.parent_id = group
                wizard.remote_system_id.syncPartner(partner=self.env.user.partner_id)
            else:
                group = wizard.remote_system_id.syncPartner(remote_int_id=wizard.profile_id.org_int_id, is_company=True)
                self.env.user.partner_id.parent_id = group
                wizard.remote_system_id.syncPartner(partner=self.env.user.partner_id)
                vals = {}
                if event_id:
                    vals = {'event_id': event_id,
                            'partner_id': group.id,
                            'contact_partner_id': self.env.user.partner_id.id,
                            'scoutgroup': True,
                            'staff': False,
                            'organization_id': wizard.remote_system_id.scoutorg_id
                            }

                    cse = self.env['campos.subcamp.exception'].search([('name', 'ilike', group.name)])
                    if cse:
                        vals['subcamp_id'] = cse.subcamp_id.id
                    elif group.municipality_id.subcamp_id:
                        vals['subcamp_id'] = group.municipality_id.subcamp_id.id

                treasurer_id = wizard.remote_system_id.getTreasurer(group.remote_link_id)
                if treasurer_id:
                    treasurer = wizard.remote_system_id.syncPartner(remote_int_id=treasurer_id)
                    treasurer.parent_id = group
                    vals['econ_partner_id'] = treasurer.id

                if event_id:
                    wizard.reg_id = self.env['event.registration'].sudo().create(vals)
                    template = self.env.ref('campos_welcome.treasurer_mail')
                    assert template._name == 'email.template'
                    try:
                        template.send_mail(wizard.reg_id.id)
                    except:
                        pass
                    _logger.info('REG Created')
            wizard.state = 'done'
            self.env.user.action_id = False

        return self.do_reopen_form()

    @api.multi
    def doit_done(self):
        for wizard in self:
            view = self.env.ref('campos_preregistration.view_form_preregistration_gl')
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'event.registration',
                'res_id': wizard.reg_id.id,  # the current wizard record
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view.id
                }