# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class CamposCheckinChildWiz(models.TransientModel):

    _name = 'campos.checkin.child.wiz'

    wizard_id = fields.Many2one('campos.checkin.wiz', 'Wizard')
    participant_id = fields.Many2one('campos.event.participant', 'Child')
    name = fields.Char('Child')
    checkin = fields.Boolean('Checkin', default=True)
    note = fields.Char('Note')


class CamposCheckinWiz(models.TransientModel):

    _name = 'campos.checkin.wiz'

    @api.model
    def default_get(self, fields):
        result = super(CamposCheckinWiz, self).default_get(fields)
        _logger.info('DEFAULT: %s CTX: %s', result, self.env.context)
        if 'participant_id' in result:
            par = self.env['campos.event.participant'].browse(result['participant_id'])
            hand_out = u'Velkomstbrev\nLejrmærke\nLejrkort\n'
            if not par.wristband_date:
                hand_out += u'Armbånd'
            else:
                hand_out += u'\nArmbånd er allerede udsendt/uddelt'
            result['hand_out'] = hand_out
            if par.jobber_child_ids:
                children = []
                for c in par.jobber_child_ids:
                    if c.state != 'deregistered':
                        children.append((0,0,{'participant_id': c.id,
                                              'name': c.name,
                                              'checkin': True,
                                              'note': u'Armbånd er uddelt' if c.wristband_date else False}))
                result['children_ids'] = children
        return result

    participant_id = fields.Many2one('campos.event.participant', 'Jobber')
    hand_out = fields.Text('Hand out')
    checkin_info_html = fields.Html(related='participant_id.checkin_info_html')
    checkin_ok = fields.Boolean(related='participant_id.checkin_ok')
    children_ids = fields.One2many('campos.checkin.child.wiz', 'wizard_id', 'Children')
    
    

    @api.multi
    def doit_arrived(self):
        for wizard in self:
            if wizard.participant_id.state != 'arrived':
                wizard.participant_id.state = 'arrived'
                wizard.participant_id.arrive_time = fields.Datetime.now()
                wizard.participant_id.suspend_security().generate_canteen_tickets()
            for c in wizard.children_ids:
                c.participant_id.state = 'arrived'
                c.participant_id.arrive_time = fields.Datetime.now()
                c.participant_id.suspend_security().generate_canteen_tickets()
                
    @api.multi
    def doit_checkin(self):
        for wizard in self:
            wizard.participant_id.state = 'checkin'
            wizard.participant_id.checkin_completed = fields.Datetime.now()
            if not wizard.participant_id.wristband_date:
                wizard.participant_id.wristband_date = fields.Date.today()
            wizard.participant_id.suspend_security().generate_canteen_tickets()
            for c in wizard.children_ids:
                if c.checkin:
                    c.participant_id.state = 'checkin'
                    c.participant_id.checkin_completed = fields.Datetime.now()
                    if not c.participant_id.wristband_date:
                        c.participant_id.wristband_date = fields.Date.today()
                    c.participant_id.suspend_security().generate_canteen_tickets()
    