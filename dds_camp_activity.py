# -*- coding: utf-8 -*-
##############################################################################
#
#    DDS Camp
#    Copyright (C) 2011 Hans Henrik Gabelgaard
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
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class dds_camp_activity_activity(osv.osv):
    """Activities"""
    _description = 'Activities'
    _name = 'dds_camp.activity.activity'
    _order = 'name'
    _inherit = 'mail.thread'
    
    _columns = {
        'name': fields.char('Name', size=128),
        'committee_id' : fields.many2one('dds_camp.committee', 'Committee'),
        'desc': fields.text('Description', translate=True),
        'age_from': fields.integer('Age from'),
        'age_to': fields.integer('Age to'),
        'points' : fields.integer('Points'),
        'audience': fields.selection([('par','Participants'),
                                     ('staff','ITS'),
                                     ('all', 'All')], 'Audience')
                
        }
    
    _defaults = {'age_from' : lambda *a: 0,
                 'age_to' : lambda *a: 99,
                 'audience': lambda *a: 'par'}
    
class dds_camp_activity_period(osv.osv):
    """Activities"""
    _description = 'Activities'
    _name = 'dds_camp.activity.period'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=128),
        'date_begin': fields.datetime('Start Date/Time', required=True),
        'date_end': fields.datetime('End Date/Time', required=True), 
        }
    
    
class dds_camp_activity_instanse(osv.osv): 
    """Activity Instanse"""
    _description = 'Activity Instanses'
    _name = 'dds_camp.activity.instanse'
    _order = 'name'
    
    def _get_seats(self, cr, uid, ids, fields, args, context=None):
        """Get reserved, available, reserved but unconfirmed and used seats for each event tickets.
        @return: Dictionary of function field values.
        """
        res = dict([(id, {}) for id in ids])
        for actins in self.browse(cr, uid, ids, context=context):
            res[actins.id]['seats_reserved'] = sum(ticket.seats for ticket in actins.ticket_ids if ticket.state == "open")
            res[actins.id]['seats_used'] = sum(ticket.seats for ticket in actins.ticket_ids if ticket.state == "done")
            res[actins.id]['seats_available'] = actins.seats_max - \
                (res[actins.id]['seats_reserved'] + res[actins.id]['seats_used']) \
                if actins.seats_max > 0 else None
        return res
    
    _columns = {
        'name': fields.char('Name', size=128),
        'seats_max': fields.integer('Maximum Avalaible Seats'),
        'seats_reserved': fields.function(_get_seats, string='Reserved Seats', type='integer', multi='seats_reserved'),
        'seats_available': fields.function(_get_seats, string='Available Seats', type='integer', multi='seats_reserved'),
        'seats_used': fields.function(_get_seats, string='Number of Participations', type='integer', multi='seats_reserved'),
        'activity_id' : fields.many2one('dds_camp.activity.activity', 'Activity'),
        'period_id' : fields.many2one('dds_camp.activity.period', 'Period'),
        'staff_ids': fields.many2many('dds_camp.event.participant','dds_camp_activity_staff_rel',
                                      'act_ins_id','par_id','Staff'),
        'ticket_ids': fields.one2many('dds_camp.activity.ticket', 'act_ins_id', 'Tickets'),         
        }   
    
class dds_camp_activity_ticket(osv.osv): 
    """Activity Instanse"""
    _description = 'Activity Instanses'
    _name = 'dds_camp.activity.ticket'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=128),
        'seats': fields.integer('Seats'),
        'reserved_time': fields.datetime('Reserved Date/Time'),
        'state': fields.selection([('open','Reserved'),
                                    ('done','Booked'),
                                    ('timeout', 'TimeOut'),
                                    ],'Ticket State'),
        'act_ins_id' : fields.many2one('dds_camp.activity.instanse', 'Activity'),
        'reg_id' : fields.many2one('dds_camp.activity.instanse', 'Troop'),
        'par_ids': fields.many2many('dds_camp.event.participant','dds_camp_activity_par_rel',
                                      'act_ins_id','par_id','Participants'),
        
        } 