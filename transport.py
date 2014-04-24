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



class dds_camp_transport_option(osv.osv):
    """ Transport Schedules/Routes """
    _description = 'Transport Schedules/Routes'
    _name = 'dds_camp.transport'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=64),
        'direction': fields.selection([('to', 'To Camp',
                                        'from', 'From Camp'), 'Direction']),
        'departure': fields.datetime('Depature'),
        'arrival': fields.datetime('Depature'),
        
        'pickup_address': fields.text('Pickup Address'),
        'destination_address': fields.text('Pickup Address'),
        'ticket_ids': fields.one2many('dds_camp.transport.ticket', 'ticket_id', 'Tickets'),
        'operator_partner_id': fields.many2one('res.partner', 'Operated by'),         
    }

dds_camp_transport_option()

class dds_camp_transport_ticket(osv.osv):
    """ Transport Ticket """
    _description = 'Transport Ticketss'
    _name = 'dds_camp.transport.ticket'
    _order = 'name'
    
    def _get_note_first_line(self, cr, uid, ids, name="", args={}, context=None):
        res = {}
        for ticket in self.browse(cr, uid, ids, context=context):
            res[ticket.id] = {'pickup_summery': (ticket.pickup_address  or "").strip().split("\n")[0],
                              'destination_summery': (ticket.destination_address  or "").strip().split("\n")[0],
                              }
        return res
    
    _columns = {
        'name': fields.char('Name', size=64),
        'direction': fields.selection([('to', 'To Camp',
                                        'from', 'From Camp'), 'Direction']),
        'departure': fields.datetime('Depature'),
        'arrival': fields.datetime('Depature'),
        
        'pickup_address': fields.text('Pickup Address'),
        'destination_address': fields.text('Pickup Address'),
        'pickup_summery': fields.function(_get_note_first_line, 
            string='Pickup', 
            type='char', sixe=64, method=True, multi='ADDR', store=True),
        'destination_summery': fields.function(_get_note_first_line, 
            string='Destination', 
            type='char', sixe=64, method=True, multi='ADDR', store=True),        
        'transport_id': fields.many2one('dds_camp.transport', 'Transport'),
        'reg_id' : fields.many2one('event.registration', 'Troop'), 
        'note' : fields.text('Notes'), 
        'seats': fields.integer('Seats'),       
    }

dds_camp_transport_ticket()