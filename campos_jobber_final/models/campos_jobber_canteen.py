# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, exceptions, _


class CamposJobberCanteen(models.Model):

    _name = 'campos.jobber.canteen'
    _description = 'Campos Jobber Canteen'  # TODO

    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    date_from = fields.Date('From date', required=True, default='2017-07-22')
    date_to = fields.Date('To date', required=True, default='2017-07-30')
    eat_at = fields.Selection([('group', 'With Scoutgroup'),
                               ('jobcamp', 'Own jobber camp'),
                               ('canteen', 'Canteen')], default='canteen', string='Eating')
    canteen_id = fields.Many2one('campos.canteen', 'Canteen')
    registration_id = fields.Many2one('event.registration', 'Group')
    state = fields.Selection([('draft', 'Draft'),
                              ('cancelled', 'Cancelled'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], default='draft', string='State')
    approved_date = fields.Datetime('Approved')
    approved_user_id = fields.Many2one('res.users', 'Approved By')
    
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if 'state' in vals and vals['state'] == 'approved':
            vals['approved_date'] = fields.Datetime.now()
            vals['spproved_user_id'] = self.env.uid
        return super(CamposJobberCanteen,self).create(vals)
    
    @api.multi
    def write(self, vals):
        if 'state' in vals and vals['state'] == 'approved':
            vals['approved_date'] = fields.Datetime.now()
            vals['spproved_user_id'] = self.env.uid
        return super(CamposJobberCanteen, self).write(vals)
    
    @api.one
    @api.constrains('date_from', 'date_to')
    def validation_dates(self):
        if self.date_from > self.date_to:
            raise exceptions.ValidationError(_('From date must be before To date'))
        if self.date_from < '2017-07-22' or self.date_to > '2017-07-30':
            raise exceptions.ValidationError(_('Dates must be in Main Camp Period'))

    
    @api.multi
    def action_approve(self):
        self.write({'state': 'approved'})
        
    @api.multi
    def action_refuse(self):
        self.write({'state': 'refused'})


