# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
from datetime import datetime, timedelta
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
    subcamp_id = fields.Many2one('campos.subcamp', 'Subcamp')
    meal = fields.Selection([('1breakfast', 'Breakfast'),
                             ('2lunch', 'Lunch'),
                             ('3dinner', 'Dinner')], string='Meal') 
    
    action = fields.Many2one('ir.actions.act_window')
    user = fields.Many2one('res.users')

    showtime_ok = fields.Integer('OK Show Time', default=7)
    showtime_not = fields.Integer('Not OK Show Time', default=7)

    
    
    def build_response(self, message, access, res_id=False):
        if access and self.action and self.user:
            action = self.action.read()[0]
            if res_id:
                action['res_id'] = res_id
            _logger.info('ACTION: %s', action)
            self.sudo(self.user.id).env['action.request'].notify(action)
        _logger.info('SCAN response: %s %s', access, message)
        return {'ShowTime': self.showtime_ok if access else self.showtime_not,
                'Message': message,
                'Access': access}
    @api.model
    def checkin(self, device_macid, participant_number):
        _logger.info('SCAN mac: %s, p: %s', device_macid, participant_number)
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
            return device.checkin_meat(participant_number, part_ids)
        else:
            self.env['campos.rfid.log'].create({'device_macid': device_macid,
                                                'pnum': participant_number,
                                                'name': u'Device not configured'})
            return self.build_response(u'Device not configured', False)
        
    
    def checkin_canteen(self, participant_number, part_ids):
        if participant_number == '-1':
            return self.build_response(u'Armbånd er ikke\ni Skejser', False)
        tickets = self.env['campos.canteen.ticket'].search([('participant_id', 'in', part_ids), ('meal', '=', self.meal), ('date', '=', fields.Date.today())])
        if tickets:
            if tickets[0].attended_time:
                att = datetime.strptime(tickets[0].attended_time, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(seconds=120)
                _logger.info('ATT: %s < %s', att, datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT))
                if att > datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT):
                    return self.build_response(u'Velbekommen\nAllerede scannet', True)
                else:
                    return self.build_response(u'Velbekommen\nAllerede scannet', True)
            elif tickets[0].canteen_id == self.canteen_id:
                att = fields.Datetime.now()
                s1 = str((int(att[11:13]) + 2) % 24).zfill(2)
                s2 = '30' if int(att[14:16]) >= 30 else '00'
                tickets[0].write({'attended_time': att,
                                  'attended_slot': '%s%s' % (s1,s2),
                                  'device_id': self.id})
                return self.build_response(u'Godkendt\nVelbekommen', True, res_id=tickets[0].canteen_inst_id.id)
            else:
                return self.build_response(u'Afvist\nGå til %s' % tickets[0].canteen_id.name, False)
        else:
            if self.env['campos.event.participant'].browse(part_ids).filtered(lambda r: r.staff and not r.arrive_time):
                return self.build_response(u'Jobber CheckIN\nMangler', False)
            return self.build_response(u'Afvist\nEj tilmeldt mad', False)

        return self.build_response(u'Ukendt deltager', False)
    
    def meat_response(self, ticket, message, access, par):
        if access:
            responce = '<div class="campos_info_box">%s</div>' % message.replace('\n','<br/>')
        else:
            responce = '<div class="campos_warning_box">%s</div>' % message.replace('\n','<br/>')
        ticket.write({'responce': responce,
                      'responce_status': access,
                      'participant_id': par.id if par else ticket.particpant_id})
        return self.build_response(message, access, res_id=ticket.id)
                                   
    def checkin_meat(self, participant_number, part_ids):
        reg = False
        par = False
        for p in self.env['campos.event.participant'].browse(part_ids):
            if p.registration_id:
                reg = p.registration_id
                par = p
            else:
                reg = p.partner_id.primary_reg_id
                par = p
            if reg:
                break
        if reg:
            tickets = self.env['campos.cat.ticket'].search([('registration_id', '=', reg.id),  ('date', '=', fields.Date.today())])
            if tickets:
                if tickets[0].subcamp_id != self.subcamp_id:
                    return self.meat_response(tickets[0],u'Afvist\nGå til %s' % (tickets[0].subcamp_id.name), False, par)
                elif not tickets[0].attended_time:
                    att = fields.Datetime.now()
                    s1 = str((int(att[11:13]) + 2) % 24).zfill(2)
                    s2 = '30' if int(att[14:16]) >= 30 else '00'
                    tickets[0].write({'attended_time': att,
                                      'attended_slot': '%s%s' % (s1, s2),
                                      'device_id': self.id})
                    meat_txt = []
                    for m in tickets[0].meat_ids:
                        meat_txt.append('%d %s' % (m.packs, m.event_day_meat_id.meat_id.name))
                    return self.meat_response(tickets[0], '\n'.join(meat_txt), True, par)
                elif tickets[0].attended_time:
                    if tickets[0].state == 'done':
                        return self.meat_response(tickets[0],u'Afvist\nAllerede afhentet', True, False)
                    else:
                        return self.meat_response(tickets[0], u'Delvist afhentet\n%s' % (tickets[0].participant_id.name), True, par)
            else:
                return self.build_response(u'Afvist\nEj tilmeldt kød', False)
        
        return self.build_response(u'Ukendt gruppe', False)
    
    @api.model
    def update_meal_on_canteen_devices(self, meal=False):
        devs = self.search([('check_method','=', 'canteen')])
        devs.write({'meal': meal})
            
        
