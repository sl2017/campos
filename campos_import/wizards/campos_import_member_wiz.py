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
    transport_to_camp = fields.Boolean('Common transport to camp', default=True)
    transport_from_camp = fields.Boolean('Common transport from camp', default=True)
    

    @api.model
    def default_get(self, fields):
        result = super(CamposImportMemberWiz, self).default_get(fields)
        
        if 'registration_id' in result:
            _logger.info('REG: %d', result['registration_id'])
            registration = self.env['event.registration'].browse(result['registration_id'])
            self.env['campos.import.member.profile'].suspend_security().import_from_membersys(registration)
        return result

    @api.multi
    def action_member_import(self):
        _logger.info('DOIT! action_member_import')
        cepd = self.env['campos.event.participant.day']
        for wizard in self:
            ed_ids = self.env['event.day'].search([('event_period', '=', 'maincamp'),
                                                   ('event_id', '=', wizard.registration_id.event_id.id)])
            # TODO
            for mbr in wizard.member_ids:
                part = self.env['campos.event.participant'].search([('registration_id', '=', wizard.registration_id.id), ('remote_mpro_int_id', '=', mbr.remote_int_id)])
                country_id = self.env['res.country'].search([('name', '=', mbr.country)])
                if part:
                    part.write({'name': mbr.name,
                                'birthdate': mbr.birthdate,
                                'street': mbr.street,
                                'street2': mbr.street2,
                                'zip': mbr.zip,
                                'city': mbr.city,
                                'country': country_id,
                                'email': mbr.email if mbr.is_leader else False,
                                'mobile': mbr.mobile if mbr.is_leader else False,
                                'parent_id': wizard.registration_id.partner_id.id,
                                'transport_to_camp': wizard.transport_to_camp,
                                'transport_from_camp': wizard.transport_from_camp,
                                'participant': True,})
                    mbr.participant_id = part
                else:
                    mbr.participant_id = self.env['campos.event.participant'].suspend_security().create({'registration_id': wizard.registration_id.id,
                                                                                                         'remote_mpro_int_id': mbr.remote_int_id,
                                                                                                         'remote_int_id': mbr.remote_partner_int_id,
                                                                                                         'name': mbr.name,
                                                                                                         'birthdate': mbr.birthdate,
                                                                                                         'street': mbr.street,
                                                                                                         'street2': mbr.street2,
                                                                                                         'zip': mbr.zip,
                                                                                                         'city': mbr.city,
                                                                                                         'country': country_id,
                                                                                                         'email': mbr.email if mbr.is_leader else False,
                                                                                                         'mobile': mbr.mobile if mbr.is_leader else False,
                                                                                                         'parent_id': wizard.registration_id.partner_id.id,
                                                                                                         'transport_to_camp': wizard.transport_to_camp,
                                                                                                         'transport_from_camp': wizard.transport_from_camp,
                                                                                                         })
                    for day in ed_ids:
                        cepd.create({'participant_id': mbr.participant_id.id,
                                     'day_id': day.id,
                                     'will_participate': True if day.event_date >= wizard.participant_from_date and day.event_date <= wizard.participant_to_date else False,
                                     })
                
                    rs = self.env['campos.event.participant'].search([('id', '=', mbr.participant_id.id)]) #JDa Need to trig Transportaion usNeed update
                    if len(rs)> 0:
                        rs[0].recalctoneed= True
                        rs[0].recalcfromneed=True    
                                            
                _logger.info('Saved %s', mbr.name)
                
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
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    country = fields.Char()
    email = fields.Char()
    mobile = fields.Char()
    is_leader = fields.Boolean()
    remote_int_id = fields.Integer('Remote ID', index=True)
    remote_partner_int_id = fields.Integer('Remote Partner ID', index=True)
    age = fields.Integer('Age', compute='_compute_age', store=True)
    state = fields.Selection([('web', 'Web'),  # Received from web
                              ('draft', 'Draft'),
                              ('waiting', 'Waiting list'),
                              ('relative', 'Contact'),  # Profile state "relative" is now known as "Contact" in UI
                              ('active', 'Active'),
                              ('inactive', 'Inactive'),
                              ('cancelled', 'Cancelled'),
                              ('open', 'Confirmed')],
                              default='draft', string="State")
    registration_id = fields.Many2one('event.registration')
    participant_id = fields.Many2one('campos.event.participant')
    remote_event_id = fields.Many2one('campos.import.event', 'Remote Event')
    
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
            for rp in msodoo.execute('member.profile', 'read', remote_profiles_ids, ['id','firstname','lastname','birthdate','state', 'partner_id', 'street','street2','zip','city','country_id', 'is_active_leader','mobile', 'email']):
                cimp = self.search([('remote_partner_int_id', '=', rp['partner_id'][0]),('registration_id', '=', registration.id)])
                if cimp:
                    cimp.write({'name': ' '.join(filter(None, [rp['firstname'], rp['lastname']])),
                                #'department': rp.active_functions_in_profile[0].organization_id.name if rp.active_functions_in_profile else '',
                                'birthdate' : rp['birthdate'],
                                'state': rp['state'],
                                'remote_int_id': rp['id'],
                                'remote_partner_int_id': rp['partner_id'][0],
                                'registration_id': registration.id,
                                'street': rp['street'],
                                'street2': rp['street2'],
                                'zip': rp['zip'],
                                'city': rp['city'],
                                'country': rp['country_id'][1] if rp['country_id'] else 'Danmark',
                                'is_leader': rp['is_active_leader'],
                                'mobile': rp['mobile'],
                                'email': rp['email'],
                                })
                else:
                    self.create({'name': ' '.join(filter(None, [rp['firstname'], rp['lastname']])),
                                 #'department': rp.active_functions_in_profile[0].organization_id.name if rp.active_functions_in_profile else '',
                                 'birthdate' : rp['birthdate'],
                                 'remote_int_id': rp['id'],
                                 'remote_partner_int_id': rp['partner_id'][0],
                                 'state': rp['state'],
                                 'registration_id': registration.id,
                                 'street': rp['street'],
                                 'street2': rp['street2'],
                                 'zip': rp['zip'],
                                 'city': rp['city'],
                                 'country': rp['country_id'][1] if rp['country_id'] else 'Danmark',
                                 'is_leader': rp['is_active_leader'],
                                 'mobile': rp['mobile'],
                                 'email': rp['email'],
                                 #'wiz_id': wizard.id,
                                 })
                _logger.info('Importing: %s %s', rp['firstname'], rp['lastname'])
                
    @api.model
    def import_from_event(self, remote_event):
        
        if remote_event.registration_id.partner_id.remote_system_id:
            remote = remote_event.registration_id.partner_id.remote_system_id
            msodoo = odoorpc.ODOO(remote.host, protocol=remote.protocol, port=remote.port)
            msodoo.login(remote.db_name, remote.db_user, remote.db_pwd)
            Partner = msodoo.env['res.partner']
            
            remote_par_ids = msodoo.env['event.registration'].search([('event_id', '=', remote_event.remote_int_id), ('state', 'in', ['open'])])
            for rp in msodoo.execute('event.registration', 'read', remote_par_ids, ['id','name','partner_id','state']):
                partner = False
                if rp['partner_id']:
                    cimp = self.search([('remote_partner_int_id', '=', rp['partner_id'][0]),('remote_event_id', '=', remote_event.id)])
                    partner = Partner.browse(rp['partner_id'][0])
                else:
                    cimp = self.search([('remote_int_id', '=', rp['id']),('remote_event_id', '=', remote_event.id)])
                if cimp:
                    cimp.write({'name': rp['name'],
                                #'department': rp.active_functions_in_profile[0].organization_id.name if rp.active_functions_in_profile else '',
                                'birthdate' : partner.member_id.birthdate if partner else False,
                                'state': rp['state'],
                                'remote_int_id': rp['id'],
                                'remote_partner_int_id': rp['partner_id'][0] if partner else False,
                                'remote_event_id': remote_event.id,
                                'street': partner.street if partner else False,
                                'street2': partner.street2 if partner else False,
                                'zip': partner.zip if partner else False,
                                'city': partner.city if partner else False,
                                'country': partner.country_id.name if partner and partner.country_id else False,
                                'is_leader': partner.member_id.is_active_leader if partner else False,
                                'mobile': partner.mobile if partner else False,
                                'email': partner.email if partner else False,
                                })
                else:
                    self.create({'name': rp['name'],
                                 #'department': rp.active_functions_in_profile[0].organization_id.name if rp.active_functions_in_profile else '',
                                 'birthdate' : partner.member_id.birthdate if partner else False,
                                 'remote_int_id': rp['id'],
                                 'remote_partner_int_id': rp['partner_id'][0] if partner else False,
                                 'state': rp['state'],
                                 'remote_event_id': remote_event.id,
                                 #'wiz_id': wizard.id,
                                 'street': partner.street if partner else False,
                                 'street2': partner.street2 if partner else False,
                                 'zip': partner.zip if partner else False,
                                 'city': partner.city if partner else False,
                                 'country': partner.country_id.name if partner and partner.country_id else False,
                                 'is_leader': partner.member_id.is_active_leader if partner and partner.member_id else False,
                                 'mobile': partner.mobile if partner else False,
                                 'email': partner.email if partner else False,
                                 })
                _logger.info('Importing: %s', rp['name'])

