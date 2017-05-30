# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class CamposRfidDevice(models.Model):

    _name = 'campos.rfid.device'
    _description = 'Campos Rfid Device'
    _inherit = ['mail.thread']

    name = fields.Char()
    device_macid = fields.Char('Device ID', help='MAC id')
    
    check_method = fields.Selection([('canteen', 'Canteen Check In'),
                                     ('meat', 'Meat Supply')], string='Function')
    canteen_id = fields.Many2one('campos.canteen', 'Canteen')
    meal = fields.Selection([('breakfast', 'Breakfast'),
                             ('lunch', 'Lunch'),
                             ('dinner', 'Dinner')], string='Meal') 
    
    
    def build_response(self, message, access):
        return {'ShowTime': 30,
                'Message': message,
                'Access': access}
    @api.model
    def checkin(self, device_macid, participant_number):
        device = self.search([('device_macid', '=', device_macid)])
        if not device:
            return self.build_response(u'Unknown Scanner\nDevice', False)
        
        if device.check_method == 'canteen':
            return device.checkin_canteen(participant_number)
        elif device.check_method == 'meat':
            return self.checkin_meat(participant_number)
        else:
            return self.build_response(u'Device not configured', False)
        
    
    def checkin_canteen(self, participant_number):
        tickets = self.env['campos.canteen.ticket'].search([('participant_id.participant_number', '=', participant_number), ('meal', '=', self.meal), ('date', '=', fields.Date.today())])
        if tickets:
            if tickets[0].attended_time:
                return self.build_response(u'Afvist\nAllerede scannet', False) 
            elif tickets[0].canteen_id == self.canteen_id:
                att = fields.Datetime.now()
                s1 = str((int(att[11:13]) + 2) % 24)
                s2 = '30' if int(att[14:16]) >= 30 else '00'
                tickets[0].write({'attended_time': att,
                                  'attended_slot': '%s%s' % (s1,s2)})
                return self.build_response(u'Godkendt\nVelbekommen', True)
            else:
                return self.build_response(u'Afvist\nGå til %s' % tickets[0].canteen_id.name, False)
        else:
            return self.build_response(u'Afvist\nEj tilmeldt mad', False)

        return self.build_response(u'Ukendt deltager', False)
                                   
    def checkin_meat(self, participant_number):
        if participant_number == '100':
            return self.build_response(u' 3 Kylling\n 3 Oksekød', True)
        if participant_number == '200':
            return self.build_response(u'Afvist\nGå til Slottet', False)
        if participant_number == '300':
            return self.build_response(u'Afvist\nAllerede afhentet', False)
        if participant_number == '400':
            return self.build_response(u'Afvist\nEj tilmeldt kød', False)
        
        return self.build_response(u'Ukendt gruppe', False)
            
        
