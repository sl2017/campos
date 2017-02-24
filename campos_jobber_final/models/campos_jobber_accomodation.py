# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposJobberAccomodation(models.Model):

    _name = 'campos.jobber.accomodation'
    _description = 'Campos Jobber Accomodation'  # TODO

    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    date_from = fields.Date('From date', required=True, default='2017-07-22')
    date_to = fields.Date('To date', required=True, default='2017-07-30')
    registration_id = fields.Many2one('event.registration', 'Group')
    state = fields.Selection([('draft', 'Draft'),
                              ('cancelled', 'Cancelled'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], default='draft', string='State')
    approved_date = fields.Datetime('Approved')
    approved_user_id = fields.Many2one('res.users', 'Approved By')
    accom_type_id = fields.Many2one('campos.jobber.accom.type', 'Accomondation Type')
    group_sel = fields.Boolean(related='accom_type_id.group_sel', readonly=True)

    @api.model
    def default_get(self, fields):
        result = super(CamposJobberAccomodation, self).default_get(fields)

        if 'participant_id' in result and result['participant_id']:
            part = self.env['campos.event.participant'].browse(result['participant_id'])
            result['registration_id'] = part.registration_id.id
            result['state'] = 'approved'

        return result
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if 'state' in vals and vals['state'] == 'approved':
            vals['approved_date'] = fields.Datetime.now()
            vals['spproved_user_id'] = self.env.uid
        return super(CamposJobberAccomodation,self).create(vals)
    
    @api.multi
    def write(self, vals):
        if 'state' in vals and vals['state'] == 'approved':
            vals['approved_date'] = fields.Datetime.now()
            vals['spproved_user_id'] = self.env.uid
        return super(CamposJobberAccomodation, self).write(vals)
    
    @api.multi
    def action_approve(self):
        self.write({'state': 'approved'})
        
    @api.multi
    def action_refuse(self):
        self.write({'state': 'refused'})
