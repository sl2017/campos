# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
import odoorpc


import logging
_logger = logging.getLogger(__name__)


class CamposImportManagerWiz(models.TransientModel):

    _name = 'campos.import.manager.wiz'

    name = fields.Char()
    registration_id = fields.Many2one('event.registration', 'Registration')
    remote_event_id = fields.Many2one('campos.import.event', 'Event')
    
    @api.model
    def default_get(self, fields):
        result = super(CamposImportManagerWiz, self).default_get(fields)
        
        if 'registration_id' in result:
            _logger.info('REG: %d', result['registration_id'])
            registration = self.env['event.registration'].browse(result['registration_id'])
            self.env['campos.import.event'].import_from_membersys(registration)
        return result

    @api.multi
    def doit(self):
        for wizard in self:
            # TODO
            pass
        action = {
            'type': 'ir.action.act_window',
            'name': 'Action Name',  # TODO
            'res_model': 'result.model',  # TODO
            'domain': [('id', '=', result_ids)],  # TODO
            'view_mode': 'form,tree',
        }
        return action


class CamposImportEvent(models.Model):

    _name = 'campos.import.event'

    name = fields.Char()
    remote_int_id = fields.Integer('Remote ID', index=True)
    registration_id = fields.Many2one('event.registration')
    date_begin = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string='End Date')

    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for event in self:
            date_begin = fields.Datetime.from_string(event.date_begin)
            date_end = fields.Datetime.from_string(event.date_end)
            dates = [fields.Date.to_string(fields.Datetime.context_timestamp(event, dt)) for dt in [date_begin, date_end] if dt]
            dates = sorted(set(dates))
            result.append((event.id, '%s (%s)' % (event.name, ' - '.join(dates))))
        return result

    @api.model
    def import_from_membersys(self, registration):

        if registration.partner_id.remote_system_id:
            remote = registration.partner_id.remote_system_id
            msodoo = odoorpc.ODOO(remote.host, protocol=remote.protocol, port=remote.port)
            msodoo.login(remote.db_name, remote.db_user, remote.db_pwd)
            #Partner = msodoo.env['res.partner']
            #partner = Partner.browse(registration.partner_id.remote_link_id)
            
            org = msodoo.execute('member.organization', 'read', registration.partner_id.remote_link_id, ['id','legal_company_id'])
            _logger.info('ORG: %s', org)
            remote_event_ids = msodoo.env['event.event'].search([('company_id', '=', org['legal_company_id'][0]), ('date_begin', '<', '2017-07-31 00:00:00'),('date_end', '>', '2017-07-21 00:00:00')])
            for rev in msodoo.env['event.event'].browse(remote_event_ids):
                ciev = self.search([('remote_int_id', '=', rev.id),('registration_id', '=', registration.id)])
                if ciev:
                    ciev.write({'name': rev.name,
                                'date_begin': rev.date_begin,
                                'date_end': rev.date_end,
                                })
                else:
                    self.create({'name': rev.name,
                                 'date_begin': rev.date_begin,
                                 'date_end': rev.date_end,
                                 'remote_int_id': rev.id,
                                 'registration_id': registration.id,
                                 })
                _logger.info('Importing: %s', rev.name)
