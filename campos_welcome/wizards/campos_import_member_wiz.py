# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
import odoorpc
from datetime import date
from dateutil.relativedelta import relativedelta


import logging
_logger = logging.getLogger(__name__)

class CamposImportMemberWiz(models.TransientModel):

    _name = 'campos.import.member.wiz'

    name = fields.Char()
    registration_id = fields.Many2one('event.registration', 'Registration')
    member_ids = fields.Many2many(comodel_name='campos.import.member.profile',
                                   relation='campos_imp_mbr_wiz_rel',
                                   column1='member_id',
                                   column2='wiz_id')
    participant_from_date = fields.Date('Date of arrival', required=True, default='2017-07-22')
    participant_to_date = fields.Date('Date of departure', required=True, default='2017-07-30')
    

    @api.model
    def default_get(self, fields):
        result = super(CamposImportMemberWiz, self).default_get(fields)
        
        if 'registration_id' in result:
            _logger.info('REG: %d', result['registration_id'])
            registration = self.env['event.registration'].browse(result['registration_id'])
            self.env['campos.import.member.profile'].import_from_membersys(registration)
        return result

    @api.multi
    def doit(self):
        cepd = self.env['campos.event.participant.day']
        for wizard in self:
            ed_ids = self.env['event.day'].search([('event_date', '>=', wizard.participant_from_date),
                                                   ('event_date', '<=', wizard.participant_to_date ),
                                                   ('event_id', '=', wizard.registration_id.event_id.id)])
            # TODO
            for mbr in wizard.member_ids:
                part = self.env['campos.event.participant'].search([('registration_id', '=', wizard.registration_id.id), ('remote_mpro_int_id', '=', mbr.remote_int_id)])
                if part:
                    part.write({'name': mbr.name,
                                'birthdate': mbr.birthdate})
                    mbr.participant_id = part
                else:
                    mbr.participant_id = self.env['campos.event.participant'].suspend_security().create({'registration_id': wizard.registration_id.id,
                                                                                                         'remote_mpro_int_id': mbr.remote_int_id,
                                                                                                         'name': mbr.name,
                                                                                                         'birthdate': mbr.birthdate,
                                                                                                         'parent_id': wizard.registration_id.partner_id.id,
                                                                                                         })
                    for day in ed_ids:
                        cepd.create({'participaant_id': mbr.participant_id.id,
                                     'day_id': day.id,
                                     'will_participate': True,
                                     })
            pass
#         action = {
#             'type': 'ir.action.act_window',
#             'name': 'Action Name',  # TODO
#             'res_model': 'result.model',  # TODO
#             'domain': [('id', '=', result_ids)],  # TODO
#             'view_mode': 'form,tree',
#         }
#         return action


class CamposImportMemberProfile(models.Model):

    _name = 'campos.import.member.profile'

    name = fields.Char()
    department = fields.Char()
    birthdate = fields.Date()
    remote_int_id = fields.Integer('Remote ID', index=True)
    age = fields.Integer('Age', compute='_compute_age', store=True)
    state = fields.Selection([('web', 'Web'),  # Received from web
                              ('draft', 'Draft'),
                              ('waiting', 'Waiting list'),
                              ('relative', 'Contact'),  # Profile state "relative" is now known as "Contact" in UI
                              ('active', 'Active'),
                              ('inactive', 'Inactive'),
                              ('cancelled', 'Cancelled')],
                              default='draft', string="State")
    registration_id = fields.Many2one('event.registration')
    participant_id = fields.Many2one('campos.event.participant')
    
    @api.multi
    @api.depends('birthdate')
    def _compute_age(self):
        for part in self:
            part.age = relativedelta(date.today(), fields.Date.from_string(part.birthdate)).years if part.birthdate else False


    @api.model
    def import_from_membersys(self, registration):
        
        if registration.partner_id.remote_system_id:
            remote = registration.partner_id.remote_system_id
            msodoo = odoorpc.ODOO(remote.host, protocol=remote.protocol, port=remote.port)
            msodoo.login(remote.db_name, remote.db_user, remote.db_pwd)
            Partner = msodoo.env['res.partner']
            partner = Partner.browse(registration.partner_id.remote_int_id)
            remote_profiles_ids = msodoo.env['member.profile'].search([('organization_id', '=', partner.organization_id.id), ('state', 'in', ['active', 'relative'])])
            for rp in msodoo.execute('member.profile', 'read', remote_profiles_ids, ['id','firstname','lastname','birthdate','state']):
                cimp = self.search([('remote_int_id', '=', rp['id']),('registration_id', '=', registration.id)])
                if cimp:
                    cimp.write({'name': ' '.join(filter(None, [rp['firstname'], rp['lastname']])),
                                #'department': rp.active_functions_in_profile[0].organization_id.name if rp.active_functions_in_profile else '',
                                'birthdate' : rp['birthdate'],
                                'state': rp['state'],
                                })
                else:
                    self.create({'name': ' '.join(filter(None, [rp['firstname'], rp['lastname']])),
                                 #'department': rp.active_functions_in_profile[0].organization_id.name if rp.active_functions_in_profile else '',
                                 'birthdate' : rp['birthdate'],
                                 'remote_int_id': rp['id'],
                                 'state': rp['state'],
                                 'registration_id': registration.id,
                                 #'wiz_id': wizard.id,
                                 })
                _logger.info('Importing: %s %s', rp['firstname'], rp['lastname'])
