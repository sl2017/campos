# -*- coding: utf-8 -*-
# Copyright 2016 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, exceptions, _


class CamposJobberAccomodation(models.Model):

    _name = 'campos.jobber.accomodation'
    _description = 'Campos Jobber Accomodation'  # TODO

    name = fields.Char()
    participant_id = fields.Many2one('campos.event.participant', 'Participant')
    date_from = fields.Date('From date', required=True, default='2017-07-22')
    date_to = fields.Date('To date', required=True, default='2017-07-30')
    registration_id = fields.Many2one('event.registration', 'Group', domain=[('partner_id.scoutgroup', '=', True),('state', 'not in', ['cancel','deregistered'])])
    camp_area_id = fields.Many2one(
        'campos.camp.area',
        'Camp Area',
        select=True,
        ondelete='set null')
    subcamp_id = fields.Many2one(
        'campos.subcamp',
        'Sub Camp',
        select=True,
        ondelete='set null')
    accom_group_id = fields.Many2one(
        'campos.jobber.accom.group',
        'Accomodation Group',
        select=True,
        ondelete='set null')
    accom_code = fields.Char('Accomodation Code')
    state = fields.Selection([('draft', 'Draft'),
                              ('cancelled', 'Cancelled'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], default='draft', string='State')
    approved_date = fields.Datetime('Approved')
    approved_user_id = fields.Many2one('res.users', 'Approved By')
    accom_type_id = fields.Many2one('campos.jobber.accom.type', 'Accomondation Type')
    group_sel = fields.Boolean(related='accom_type_id.group_sel', readonly=True)
    camparea_sel = fields.Boolean(related='accom_type_id.camparea_sel', readonly=True)
    subcamp_sel = fields.Boolean(related='accom_type_id.subcamp_sel', readonly=True)
    accomgroup_sel = fields.Boolean(related='accom_type_id.accomgroup_sel', readonly=True)

    @api.model
    def default_get(self, fields):
        result = super(CamposJobberAccomodation, self).default_get(fields)

        if 'participant_id' in result and result['participant_id']:
            part = self.env['campos.event.participant'].browse(result['participant_id'])
            result['registration_id'] = part.registration_id.id
            result['state'] = 'approved'

        return result

    def _date_overlaps(self):
        '''Return search domain expression for date overlap'''
        domain = ['|', ('date_to', '=', False), ('date_to', '>=', self.date_from)]
        if self.date_to:
            domain += [('date_from', '<=', self.date_to)]
        return domain
    
    def _date_contains(self):
        '''Return search domain express for an interval contianing the search interval'''
        domain = [('date_from', '<=', self.date_from)]
        if self.date_to:
            domain += ['|', ('date_to', '=', False), ('date_to', '>=', self.date_to)]
        else:
            domain += [('date_to', '=', False)]
        return domain

    @api.one
    @api.constrains('date_from', 'date_to')
    def validation_dates(self):
        if self.date_from > self.date_to:
            raise exceptions.ValidationError(_('From date must be before To date'))
        if self.date_from < '2017-07-22' or self.date_to > '2017-07-30':
            raise exceptions.ValidationError(_('Accomodation dates must be in Main Camp Period'))
        if self.search_count([('participant_id', '=', self.participant_id.id),
                              ('id', '!=', self.id)] + 
                             self._date_overlaps()) > 0:
            raise exceptions.ValidationError(_('Accomodation dates must not be overlapping'))


    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if 'state' in vals and vals['state'] == 'approved':
            vals['approved_date'] = fields.Datetime.now()
            vals['spproved_user_id'] = self.env.uid
        if 'accom_code' in vals and vals['accom_code']:
            accom_id = self.env['campos.jobber.accom.group'].suspend_security().search([('code', '=', vals['accom_code'])])
            if accom_id:
                vals['accom_group_id'] = accom_id.id
                vals['state'] = 'draft'
        return super(CamposJobberAccomodation,self).create(vals)
    
    @api.multi
    def write(self, vals):
        if 'state' in vals and vals['state'] == 'approved':
            vals['approved_date'] = fields.Datetime.now()
            vals['spproved_user_id'] = self.env.uid
        if 'accom_code' in vals and vals['accom_code']:
            accom_id = self.env['campos.jobber.accom.group'].suspend_security().search([('code', '=', vals['accom_code'])])
            if accom_id:
                vals['accom_group_id'] = accom_id.id
                vals['state'] = 'draft'
        return super(CamposJobberAccomodation, self).write(vals)
    
    @api.multi
    def action_approve(self):
        self.write({'state': 'approved'})
        
    @api.multi
    def action_refuse(self):
        self.write({'state': 'refused'})
        
    @api.onchange('accom_code')
    def onchange_accom_code(self):
        if self.accom_code:
            accom_id = self.env['campos.jobber.accom.group'].suspend_security().search([('code', '=', self.accom_code)])
            if accom_id:
                self.accom_group_id = accom_id
                self.state = 'draft'

    @api.onchange('accom_type_id')
    def onchange_accom_type_id(self):
        if self.accom_type_id:
            if not self.accom_type_id.group_sel:
                self.registration_id = False
            if not self.accom_type_id.accomgroup_sel:
                self.accom_group_id = False
            if not self.accom_type_id.subcamp_sel:
                self.subcamp_id = False
            else:
                self.subcamp_id = self.participant_id.primary_committee_id.subcamp_id  
    
    @api.multi
    def action_open_accom_group(self):
        self.ensure_one()

        if self.accom_group_id:
            return {
                'name': self.accom_group_id.name,
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('campos_jobber_final.campos_jobber_accom_group_form_view').id,
                'res_model': 'campos.jobber.accom.group',
                'res_id': self.accom_group_id.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                #'target': 'new',
                'context' : {
                             'default_owner_id': self.id, 
                             }
                }    
            
