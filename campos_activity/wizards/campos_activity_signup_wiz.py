# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _, exceptions


class CamposActivitySignupMembers(models.TransientModel):
    _name = 'campos.activity.signup.members'
    _description = 'Activity Signup Members'    
    
    name =  fields.Char('Name', size=64)
    par_id = fields.Many2one('campos.event.participant', 'Participation',  ondelete='cascade')
    reg_id = fields.Many2one('event.registration', 'Registration', ondelete='cascade')
    wiz_id = fields.Many2one('campos.activity.signup', 'Wizard', ondelete='cascade')


class CamposActivitySignupWiz(models.TransientModel):

    _name = 'campos.activity.signup.wiz'

    name = fields.Char('Own Note', size=128, help='You can add a Note for own use. It will be shown on activity list etc. I will NOT be read/answered by the Staff.')
    
    state = fields.Selection([('step1', 'Select Activity'),
                              ('step2', 'Select Participants')], 'State', default='step1')
    reg_id = fields.Many2one('event.registration', 'Scout Group')
    act_id = fields.Many2one('campos.activity.activity', '1. Select Activity', required=True, select=True, ondelete='cascade')
    teaser = fields.Text(related='act_id.teaser', readonly=True)
    audience_ids = fields.Many2many(related='act_id.audience_ids', readonly=True)
    age_from =  fields.Integer(related='act_id.age_from', readonly=True)
    age_to = fields.Integer(related='act_id.age_to', readonly=True)
    
    act_ins_id = fields.Many2one('campos.activity.instanse', '2. Select Period', required=True, select=True, ondelete='cascade')
    seats = fields.Integer('3. Reserve Seats', required=True)
    ticket_id = fields.Many2one('campos.activity.ticket', 'Ticket', ondelete='set null'),
    seats_available = fields.Integer(related='act_ins_id.seats_available', readonly=True)
    
    @api.one
    @api.constrains('seats', 'act_ins_id')
    def _check_seats(self):
        if self.seats <= 0:
            raise exceptions.ValidationError("Reserved seats should be positive")
        if self.act_ins_id.seats_hard and not self.ticket_id:
            if self.seats > self.act_ins_id.seats_available:
                raise exceptions.ValidationError("Sorry! Only %d seats available" % self.act_ins_id.seats_available)
        return True
    
    @api.multi
    def doit_step1(self):
        
        for wiz in self:
            dt = wiz.act_ins_id.period_id.date_begin[0:6]
            if wiz.reg_id.participant_ids:
                for par in wiz.reg_id.participant_ids:
                    #Test aktivitetsdato mod deltagerdage
                    if dt < par.tocampdate or dt > par.fromcampdate:
                        continue
                    # Test alderskrav        
                    if par.camp_age < wiz.act_ins_id.activity_id.age_from or par.camp_age > wiz.act_ins_id.activity_id.age_to:
                        continue
                    # Test mod andre bookinger    
                    period_ok = True
                    if par.ticket_ids:
                        for tck in par.ticket_ids:
                            if tck.act_ins_id.period_id.date_begin <= wiz.act_ins_id.period_id.date_end and tck.act_ins_id.period_id.date_end >= wiz.act_ins_id.period_id.date_begin:
                                period_ok = False
                                break
                    if not period_ok:
                        continue
                    mbr_obj.create({'wiz_id' : wiz.id,
                                    'par_id' : par.id,
                                    'name'   : par.name,
                                    'reg_id' : wiz.reg_id.id})
 
            
                wiz.state='step2'
        action = {
            'type': 'ir.action.act_window',
            'name': 'Activity Signup',  # TODO
            'res_model': 'campos.activity.signup.wiz',  # TODO
            'res_id' : self.id,
            'view_mode': 'form',
        }
        return action
