# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposCheckinGrpWiz(models.TransientModel):

    _name = 'campos.checkin.grp.wiz'
    
    @api.model
    def default_get(self, fields):
        result = super(CamposCheckinGrpWiz, self).default_get(fields)
        if 'registration_id' in result:
            reg = self.env['event.registration'].browse(result['registration_id'])
            hand_out = u'Velkomstbrev\nUnderlejr info\nLejrkort\n'
            result['hand_out'] = hand_out
        return result


    registration_id = fields.Many2one('event.registration', 'Group')
    hand_out = fields.Text('Hand out')
    checkin_info_html = fields.Html(related='registration_id.checkin_info_html')
    checkin_ok = fields.Boolean(related='registration_id.checkin_ok')
    checkin_participant_id = fields.Many2one(related='registration_id.checkin_participant_id')
    checkin_par_mobile = fields.Char(related='checkin_participant_id.mobile')

    @api.multi
    def doit_arrived(self):
        for wizard in self:
            if wizard.registration_id.state != 'arrived':
                wizard.registration_id.state = 'arrived'
                wizard.registration_id.arrive_time = fields.Datetime.now()
            
    @api.multi
    def doit_checkin(self):
        for wizard in self:
            wizard.registration_id.state = 'checkin'
            wizard.registration_id.checkin_completed = fields.Datetime.now()
            #wizard.participant_id.suspend_security().generate_canteen_tickets() CATERING TICKETS!
            