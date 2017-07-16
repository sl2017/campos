# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class CamposRfidDevice(models.Model):

    _name = 'campos.rfid.device'
    _description = 'Campos Rfid Device'
    _inherit = ['mail.thread']

    name = fields.Char()
    device_macid = fields.Char('Device ID', help='MAC id')
    
    check_method = fields.Selection([('canteen', 'Canteen Check In'),
                                     ('meat', 'Meat Supply')], string='Function')
    canteen_id = fields.Many2one('campos.canteen', 'Canteen')
    meal = fields.Selection([('1breakfast', 'Breakfast'),
                             ('2lunch', 'Lunch'),
                             ('3dinner', 'Dinner')], string='Meal') 
    
    action = fields.Many2one('ir.actions.act_window')
    user = fields.Many2one('res.users')


    
    
    def build_response(self, message, access, res_id=False):
        if access and self.action and self.user:
            action = self.action.read()[0]
            if res_id:
                action['res_id'] = res_id
            _logger.info('ACTION: %s', action)
            self.sudo(self.user.id).env['action.request'].notify(action)

        return {'ShowTime': 10,
                'Message': message,
                'Access': access}
    @api.model
    def checkin(self, device_macid, participant_number):
        device = self.search([('device_macid', '=', device_macid)])
        if not device:
            self.env['campos.rfid.log'].create({'device_macid': device_macid,
                                                'pnum': participant_number,
                                                'name': u'Unknown scanner'})
            return self.build_response(u'Unknown Scanner\n%s' % device_macid, False)
        
        part = self.env['campos.event.participant'].search([('participant_number' ,'=', participant_number)])
        part_ids = [part.id]
        if part.doublet_id:
            part_ids.append(part.doublet_id.id)
        if part.reverse_doublet_id:
            part_ids.append(part.reverse_doublet_id.id)
        if device.check_method == 'canteen':
            return device.checkin_canteen(participant_number, part_ids)
        elif device.check_method == 'meat':
            return self.checkin_meat(participant_number, part_ids)
        else:
            self.env['campos.rfid.log'].create({'device_macid': device_macid,
                                                'pnum': participant_number,
                                                'name': u'Device not configured'})
            return self.build_response(u'Device not configured', False)
        
    
    def checkin_canteen(self, participant_number, part_ids):
        tickets = self.env['campos.canteen.ticket'].search([('participant_id', 'in', part_ids), ('meal', '=', self.meal), ('date', '=', fields.Date.today())])
        if tickets:
            if tickets[0].attended_time:
                return self.build_response(u'Afvist\nAllerede scannet', False) 
            elif tickets[0].canteen_id == self.canteen_id:
                att = fields.Datetime.now()
                s1 = str((int(att[11:13]) + 2) % 24)
                s2 = '30' if int(att[14:16]) >= 30 else '00'
                tickets[0].write({'attended_time': att,
                                  'attended_slot': '%s%s' % (s1,s2)})
                return self.build_response(u'Godkendt\nVelbekommen', True, res_id=tickets[0].canteen_inst_id.id)
            else:
                return self.build_response(u'Afvist\nGå til %s' % tickets[0].canteen_id.name, False)
        else:
            return self.build_response(u'Afvist\nEj tilmeldt mad', False)

        return self.build_response(u'Ukendt deltager', False)
                                   
    def checkin_meat(self, participant_number, part_ids):
        if participant_number == '100':
            return self.build_response(u' 3 Kylling\n 3 Oksekød', True)
        if participant_number == '200':
            return self.build_response(u'Afvist\nGå til Slottet', False)
        if participant_number == '300':
            return self.build_response(u'Afvist\nAllerede afhentet', False)
        if participant_number == '400':
            return self.build_response(u'Afvist\nEj tilmeldt kød', False)
        
        return self.build_response(u'Ukendt gruppe', False)
            
        
