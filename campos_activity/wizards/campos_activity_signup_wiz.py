# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _, exceptions

import logging
_logger = logging.getLogger(__name__)

class CamposActivitySignupMembers(models.TransientModel):
    _name = 'campos.activity.signup.members'
    _description = 'Activity Signup Members'    
    
    name =  fields.Char('Name', size=64)
    camp_age = fields.Integer(related='par_id.camp_age')
    own_note = fields.Char(related='par_id.own_note')
    par_id = fields.Many2one('campos.event.participant', 'Participation',  ondelete='cascade')
    reg_id = fields.Many2one('event.registration', 'Registration', ondelete='cascade')
    wiz_id = fields.Many2one('campos.activity.signup.wiz', 'Wizard', ondelete='cascade')


class CamposActivitySignupWiz(models.TransientModel):

    _name = 'campos.activity.signup.wiz'

    name = fields.Char('Own Note', size=128, help='You can add a Note for own use. It will be shown on activity list etc. I will NOT be read/answered by the Staff.')
    
    state = fields.Selection([('step1', 'Select Activity'),
                              ('step2', 'Select Participants')], 'State', default='step1')
    reg_id = fields.Many2one('event.registration', 'Scout Group')
    act_id = fields.Many2one('campos.activity.activity', '1. Select Activity', required=True, select=True, ondelete='cascade', domain=[('state', 'in', ['confirmed'])])
    teaser = fields.Text(related='act_id.teaser', readonly=True)
    audience_ids = fields.Many2many(related='act_id.audience_ids', readonly=True)
    age_from =  fields.Integer(related='act_id.age_from', readonly=True)
    age_to = fields.Integer(related='act_id.age_to', readonly=True)
    
    act_ins_id = fields.Many2one('campos.activity.instanse', '2. Select Period', required=True, select=True, ondelete='cascade')
    seats = fields.Integer('3. Reserve Seats', required=True)
    seats_reserved = fields.Integer('Reserved Seats')
    ticket_id = fields.Many2one('campos.activity.ticket', 'Ticket', ondelete='set null')
    seats_available = fields.Integer(related='act_ins_id.seats_available', readonly=True)
    par_signup_ids = fields.Many2many('campos.activity.signup.members', relation="rel_act_signup_wiz", string='4. Signup participants')
    
    @api.one
    @api.constrains('seats', 'act_ins_id')
    def _check_seats(self):
        if self.seats <= 0:
            raise exceptions.ValidationError(_("Reserved seats should be positive"))
        if self.act_ins_id.seats_hard and not self.ticket_id:
            if self.seats > self.act_ins_id.seats_available:
                if self.act_ins_id.seats_available > 0:
                    raise exceptions.ValidationError(_("Sorry! Only %d seats available") % self.act_ins_id.seats_available)
                else:
                    raise exceptions.ValidationError(_("Sorry! No seats available"))
        if self.act_ins_id.seats_hard and self.ticket_id and self.seats > self.seats_reserved:
             raise exceptions.ValidationError(_("Sorry! You can't increase the number of reserved seats. Only %d reserved") % (self.seats_reserved))
        if self.act_ins_id.seats_available <= 0 and not self.ticket_id:
                raise exceptions.ValidationError(_("Sorry! No seats available"))
        return True
    
    @api.onchange('act_ins_id')
    def _onchange_act_ins_id(self):
        if self.act_ins_id and self.act_ins_id.seats_available <= 0:
            return {
                    'warning': {'title': _("Warning"), 'message': _("No seats available for selected period!")},
                    }
            
    @api.multi
    def doit_step1(self):
        _logger.info('doit_step1')
        self.ensure_one()
        for wiz in self:
            wiz.seats_reserved = wiz.seats
            dt = wiz.act_ins_id.period_id.date_begin[0:10]
            mbr_obj = self.env['campos.activity.signup.members']
            if wiz.reg_id.participant_ids:
                for par in wiz.reg_id.participant_ids:
                    if par.state in ['reg', 'duplicate', 'deregistered']:
                        continue
                    #Test aktivitetsdato mod deltagerdage
                    _logger.info('Evaluating %s %s %s', par.name, dt, par.tocampdate)
                    if dt < par.tocampdate or dt > par.fromcampdate:
                        continue
                    # Test alderskrav - Alderskrav bortfaldet        
                    #_logger.info('Evaluating age %s %s', par.name, par.camp_age)
                    #if par.camp_age < wiz.act_ins_id.activity_id.age_from or par.camp_age > wiz.act_ins_id.activity_id.age_to:
                    #    continue
                    # Test mod andre bookinger    
                    period_ok = True
                    if par.ticket_ids:
                        for tck in par.ticket_ids:
                            if tck.act_ins_id.period_id.date_begin <= wiz.act_ins_id.period_id.date_end and tck.act_ins_id.period_id.date_end >= wiz.act_ins_id.period_id.date_begin:
                                period_ok = False
                                break
                    if not period_ok:
                        continue
                    _logger.info('Adding %s', par.name)
                    mbr_obj.create({'wiz_id' : wiz.id,
                                    'par_id' : par.id,
                                    'name'   : par.name,
                                    'reg_id' : wiz.reg_id.id})
 
            
            self.state = 'step2'
            self.ticket_id = self.env['campos.activity.ticket'].suspend_security().create({'reg_id': wiz.reg_id.id,
                                                                                       'act_ins_id': wiz.act_ins_id.id,
                                                                                       'seats': wiz.seats,
                                                                                       'state': 'open'})
            _logger.info('Ticket created %s %d', wiz.state, wiz.id)
        
        
        return {
            'name': _('Add participants'),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('campos_activity.campos_activity_signup_wiz_form_view').id,
            'res_model': 'campos.activity.signup.wiz',
            'type': 'ir.actions.act_window',
            #'nodestroy': True,
            'target': 'new',
            'context' : {
                         'default_reg_id': self.id, 
                         },
            'res_id': self.id,
            }


    @api.multi
    def doit_step2(self):
        _logger.info('doit_step2')
        self.ensure_one()
        for wiz in self:
            signups = []
            for par in wiz.par_signup_ids:
                signups.append(par.par_id.id)
            tck = wiz.ticket_id.suspend_security()    
            tck.par_ids = [(6, 0, signups)]
            tck.seats = len(signups) # TODO Check against max avail!
            tck.state = 'done' 
                
        
        
    @api.multi
    def prepare_step2(self):
        _logger.info('prepare_step2')
        self.ensure_one()
        for wiz in self:
            dt = wiz.act_ins_id.period_id.date_begin[0:10]
            mbr_obj = self.env['campos.activity.signup.members']
            if wiz.reg_id.participant_ids:
                for par in wiz.reg_id.participant_ids:
                    if par.state in ['reg', 'duplicate', 'deregistered']:
                        continue
                    #Test aktivitetsdato mod deltagerdage
                    _logger.info('Evaluating %s %s %s', par.name, dt, par.tocampdate)
                    if dt < par.tocampdate or dt > par.fromcampdate:
                        continue
                    # Test alderskrav - Alderskrav bortfaldet        
                    #_logger.info('Evaluating age %s %s', par.name, par.camp_age)
                    #if par.camp_age < wiz.act_ins_id.activity_id.age_from or par.camp_age > wiz.act_ins_id.activity_id.age_to:
                    #    continue
                    # Test mod andre bookinger    
                    period_ok = True
                    if par.ticket_ids:
                        for tck in par.ticket_ids:
                            if tck.act_ins_id.period_id.date_begin <= wiz.act_ins_id.period_id.date_end and tck.act_ins_id.period_id.date_end >= wiz.act_ins_id.period_id.date_begin and tck.id != wiz.ticket_id.id:
                                period_ok = False
                                break
                    if not period_ok:
                        continue
                    _logger.info('Adding %s', par.name)
                    mbr_id = mbr_obj.create({'wiz_id' : wiz.id,
                                             'par_id' : par.id,
                                             'name'   : par.name,
                                             'reg_id' : wiz.reg_id.id})
                    if self.ticket_id.id in par.ticket_ids.ids:
                        self.par_signup_ids += mbr_id
 
        return {
            'name': _('Edit participants'),
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('campos_activity.campos_activity_signup_wiz_form_view').id,
            'res_model': 'campos.activity.signup.wiz',
            'type': 'ir.actions.act_window',
            #'nodestroy': True,
            'target': 'new',
            'context' : {
                         'default_reg_id': self.id, 
                         },
            'res_id': self.id,
            }
