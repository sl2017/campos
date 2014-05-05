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
from openerp.osv.fields import datetime as datetime_field
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
        'name': fields.char('Name', size=128, translate=True),
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
    """Activity Period"""
    _description = 'Activity Period'
    _name = 'dds_camp.activity.period'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=128),
        'date_begin': fields.datetime('Start Date/Time', required=True),
        'date_end': fields.datetime('End Date/Time', required=True), 
        }
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            date = record.date_begin.split(" ")[0]
            date_end = record.date_end.split(" ")[0]
            if date != date_end:
                date += ' - ' + date_end
            display_name = record.name + ' (' + date + ')'
            res.append((record['id'], display_name))
        return res
    
    
class dds_camp_activity_instanse(osv.osv): 
    """Activity Instanse"""
    _description = 'Activity Instanses'
    _name = 'dds_camp.activity.instanse'
    _order = 'name'
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        act_obj = self.pool.get('dds_camp.activity.activity')
        per_obj = self.pool.get('dds_camp.activity.period')
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            dummy,act_name = act_obj.name_get(cr, uid, [record.activity_id.id], context)[0]
            dummy,per_name = per_obj.name_get(cr, uid, [record.period_id.id], context)[0]
            if record.name:
                display_name = record.name + ' ' + act_name + ' - ' + per_name
            else:
                display_name = act_name + ' - ' + per_name     
            res.append((record['id'], display_name))
    
        return res
    
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
            #res[actins.id]['name'] =     
        return res
    
    def _search_seats(self, cr, uid, obj, name, args, context=None):
        print args
        return [('id','in',[58,59,60])]
    
    _columns = {
        'name': fields.char('Name', size=128),
        'seats_max': fields.integer('Maximum Avalaible Seats'),
        'seats_reserved': fields.function(_get_seats, string='Reserved Seats', type='integer', multi='seats_reserved'),
        'seats_available': fields.function(_get_seats, string='Available Seats', type='integer', multi='seats_reserved', fnct_search=_search_seats),
        'seats_used': fields.function(_get_seats, string='Number of Participations', type='integer', multi='seats_reserved'),
        #'complete_name': fields.function(_name_get_fnc, type="char", string='Full Name', multi='seats_reserved'),
        'activity_id' : fields.many2one('dds_camp.activity.activity', 'Activity'),
        'period_id' : fields.many2one('dds_camp.activity.period', 'Period'),
        'staff_ids': fields.many2many('dds_camp.event.participant','dds_camp_activity_staff_rel',
                                      'act_ins_id','par_id','Staff'),
        'ticket_ids': fields.one2many('dds_camp.activity.ticket', 'act_ins_id', 'Tickets'),         
        }   
    
class dds_camp_activity_ticket(osv.osv): 
    """Activity Ticket"""
    _description = 'Activity Ticket'
    _name = 'dds_camp.activity.ticket'
    _order = 'name'
    _columns = {
        'name': fields.char('Own Note', size=128, help='You can add a Note for own use. It will be shown on activity list etc. I will NOT be read/answered by the Staff.'),
        'seats': fields.integer('Seats'),
        'reserved_time': fields.datetime('Reserved Date/Time'),
        'state': fields.selection([('open','Reserved'),
                                    ('done','Booked'),
                                    ('timeout', 'TimeOut'),
                                    ],'Ticket State'),
        'act_ins_id' : fields.many2one('dds_camp.activity.instanse', 'Activity'),
        'reg_id' : fields.many2one('event.registration', 'Troop'),
        'par_ids': fields.many2many('dds_camp.event.participant','dds_camp_activity_par_rel',
                                      'ticket_id','par_id','Participants'),
        'actins_date_begin' : fields.related('act_ins_id', 'period_id','date_begin', type='datetime', string='Start Date/Time'),
        
        } 
    
    def run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        
        exp_time = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        print "Check expiring", exp_time
        for tck in self.browse(cr, SUPERUSER_ID, self.search(cr, uid, [('state','=','open'),('reserved_time','<',exp_time)])):
            print "Expiring", tck.id, tck.reserved_time, tck.name
            self.write(cr, uid, [tck.id], {'state': 'timeout'})
            