# -*- coding: utf-8 -*-
##############################################################################
#
#    DDS Camp
#    Copyright (C) 2014 Hans Henrik Gabelgaard
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import datetime
from openerp.osv import fields, osv, orm
from openerp.osv.fields import datetime as datetime_field
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT



class dds_camp_transport_route(osv.osv):
    """ Transport Schedules/Routes """
    _description = 'Transport Schedules/Routes'
    _name = 'dds_camp.transport.route'
    _order = 'departure'
    _columns = {
        'name': fields.char('Name', size=64),
        'direction': fields.selection([('to', 'To Camp'),
                                       ('from', 'From Camp')], 'Direction'),
        'departure': fields.datetime('Depature'),
        'arrival': fields.datetime('Arrival'),
        
        'pickup_address': fields.text('Pickup Address'),
        'destination_address': fields.text('Destination Address'),
        'ticket_ids': fields.one2many('dds_camp.transport.ticket', 'transport_id', 'Tickets'),
        'operator_partner_id': fields.many2one('res.partner', 'Operated by'),         
    }

dds_camp_transport_route()

class dds_camp_transport_ticket(osv.osv):
    """ Transport Ticket """
    _description = 'Transport Tickets'
    _name = 'dds_camp.transport.ticket'
    _order = 'departure'
    
    def _get_note_first_line(self, cr, uid, ids, name="", args={}, context=None):
        res = {}
        for ticket in self.browse(cr, uid, ids, context=context):
            res[ticket.id] = {'pickup_summery': (ticket.pickup_address  or "").strip().split("\n")[0],
                              'destination_summery': (ticket.destination_address  or "").strip().split("\n")[0],
                              }
        return res
    
    _columns = {
        'name': fields.char('Name', size=64),
        'transport_id': fields.many2one('dds_camp.transport.route', 'Transport'),
        'direction': fields.related('transport_id', 'direction', readonly=True, type='selection', values=[('to', 'To Camp',
                                        'from', 'From Camp')],  string = 'Direction'), 
        'departure': fields.datetime('Depature'),
        'arrival': fields.datetime('Arrival'),
        
        'pickup_address': fields.text('Pickup Address'),
        'destination_address': fields.text('Destination Address'),
        
        'pickup_summery': fields.function(_get_note_first_line, 
            string='Pickup', 
            type='char', sixe=64, method=True, multi='ADDR', store=True),
        'destination_summery': fields.function(_get_note_first_line, 
            string='Destination', 
            type='char', sixe=64, method=True, multi='ADDR', store=True),        
        
        'reg_id' : fields.many2one('event.registration', 'Troop'), 
        'note' : fields.text('Notes'), 
        'seats': fields.integer('Seats'),       
    }
    
    def onchange_transport_id(self, cr, uid, ids, transport_id, context=None):       
                
        res = {}
        values = {}
        print "on_ch", transport_id
        tran_obj = self.pool.get('dds_camp.transport.route')
        for tran in tran_obj.browse(cr,uid, [transport_id], context):
            if tran.departure:
                values['departure'] = tran.departure
            if tran.arrival:
                values['arrival'] = tran.arrival
            if tran.pickup_address:
                values['pickup_address'] = tran.pickup_address
            if tran.destination_address:
                values['destination_address'] = tran.destination_address    
            
            res['value'] = values
        
        print "res", res
        return res     

dds_camp_transport_ticket()
