# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposImportParticipantWiz(models.TransientModel):

    _name = 'campos.import.participant.wiz'

    name = fields.Char()
    registration_id = fields.Many2one('event.registration', 'Registration')
    remote_event_id = fields.Many2one('campos.import.event', 'Event')
    member_ids = fields.Many2many(comodel_name='campos.import.member.profile',
                                   relation='campos_imp_par_wiz_rel',
                                   column1='member_id',
                                   column2='wiz_id')
    
    participant_from_date = fields.Date('Date of arrival', required=True, default='2017-07-22')
    participant_to_date = fields.Date('Date of departure', required=True, default='2017-07-30')
    transport_to_camp = fields.Boolean('Common transport to camp', default=True)
    transport_from_camp = fields.Boolean('Common transport from camp', default=True)
    
    @api.model
    def default_get(self, fields):
        result = super(CamposImportParticipantWiz, self).default_get(fields)
        
        if 'remote_event_id' in result:
            remote_event = self.env['campos.import.event'].browse(result['remote_event_id'])
            self.env['campos.import.member.profile'].import_from_event(remote_event)
            result['participant_from_date'] = remote_event.date_begin
            result['participant_to_date'] = remote_event.date_end
        return result
 

    @api.multi
    def doit(self):
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
                                'participant': True,
                                })
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
                

