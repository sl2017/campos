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
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            sold_out = True
            for actins in record.act_ins_ids:
                if actins.seats_available > 0:
                    sold_out = False
            display_name = record.name
            if sold_out and context.get('limit_check', False):
                display_name += _(' (This activity is fully booked)')
            res.append((record['id'], display_name))
        return res       
                
    _columns = {
        'name': fields.char('Name', size=128, translate=True),
        'committee_id' : fields.many2one('dds_camp.committee', 'Committee'),
        'desc': fields.text('Description', translate=True),
        'age_from': fields.integer('Age from'),
        'age_to': fields.integer('Age to'),
        'points' : fields.integer('Points'),
        'audience': fields.selection([('par','Participants'),
                                     ('staff','ITS'),
                                     ('all', 'All')], 'Audience'),
        'act_ins_ids': fields.one2many('dds_camp.activity.instanse', 'activity_id', 'Instanses'),        
        }
    
    _defaults = {'age_from' : lambda *a: 0,
                 'age_to' : lambda *a: 99,
                 'audience': lambda *a: 'par'}
    
    def name_create(self, cr, uid, name, context=None):
        raise osv.except_osv(_('Warning'), _("Quick creation disallowed."))
    
class dds_camp_activity_period(osv.osv):
    """Activity Period"""
    _description = 'Activity Period'
    _name = 'dds_camp.activity.period'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=128, translate=True),
        'date_begin': fields.datetime('Start Date/Time', required=True),
        'date_end': fields.datetime('End Date/Time', required=True), 
        }
    
    def name_create(self, cr, uid, name, context=None):
        raise osv.except_osv(_('Warning'), _("Quick creation disallowed."))
    
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
    _order = 'actins_date_begin'
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        act_obj = self.pool.get('dds_camp.activity.activity')
        per_obj = self.pool.get('dds_camp.activity.period')
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            act_name = ''
            per_name = ''
            limit_txt = ''
            if record.activity_id:
                dummy,act_name = act_obj.name_get(cr, uid, [record.activity_id.id], context)[0]
            if record.period_id:
                dummy,per_name = per_obj.name_get(cr, uid, [record.period_id.id], context)[0]
            if record.seats_hard and context.get('limit_check', False):
                limit_txt = ' (Only %d seats left)' % (record.seats_available)    
            if record.name:
                display_name = record.name + ' ' + act_name + ' - ' + per_name + limit_txt
            else:
                display_name = act_name + ' - ' + per_name + limit_txt     
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
        ids = []
        for ai in self.browse(cr, uid, self.search(cr, uid, [], context=context), context=context):
            if ai.seats_available > 0:
                ids.append(ai.id)
        return [('id','in', ids)]
    
    def _calc_agegroup(self, cr, uid, ids, field_name, arg, context):
        res = {}
    
        for actins in self.browse(cr, uid, ids, context=context):    
            ag06_08 = 0
            ag09_10 = 0
            ag11_12 = 0
            ag13_16 = 0
            ag17_22 = 0
            ag22p = 0
            for tck in actins.ticket_ids:
                ag06_08 += tck.ag06_08 
                ag09_10 += tck.ag09_10    
                ag11_12 += tck.ag11_12
                ag13_16 += tck.ag13_16
                ag17_22 += tck.ag17_22
                ag22p += tck.ag22p
            res[actins.id] = {'ag06_08': ag06_08,
                              'ag09_10': ag09_10,
                               'ag11_12': ag11_12, 
                               'ag13_16': ag13_16, 
                               'ag17_22':ag17_22,
                               'ag22p': ag22p
                               }           
        return res
    _columns = {
        'name': fields.char('Name', size=128, translate=True),
        'seats_max': fields.integer('Maximum Avalaible Seats'),
        'seats_hard': fields.boolean('Hard limit'),
        'seats_reserved': fields.function(_get_seats, string='Reserved Seats', type='integer', multi='seats_reserved'),
        'seats_available': fields.function(_get_seats, string='Available Seats', type='integer', multi='seats_reserved', fnct_search=_search_seats),
        'seats_used': fields.function(_get_seats, string='Number of Participations', type='integer', multi='seats_reserved'),
        #'complete_name': fields.function(_name_get_fnc, type="char", string='Full Name', multi='seats_reserved'),
        'activity_id' : fields.many2one('dds_camp.activity.activity', 'Activity'),
        'period_id' : fields.many2one('dds_camp.activity.period', 'Period'),
        'staff_ids': fields.many2many('dds_camp.event.participant','dds_camp_activity_staff_rel',
                                      'act_ins_id','par_id','Staff'),
        'ticket_ids': fields.one2many('dds_camp.activity.ticket', 'act_ins_id', 'Tickets'),
        'actins_date_begin' : fields.related('period_id','date_begin', type='datetime', string='Start Date/Time', store=True),
        'ag06_08' : fields.function(_calc_agegroup, type = 'integer', string='Age 6-8', method=True, multi='AGE'),
        'ag09_10' : fields.function(_calc_agegroup, type = 'integer', string='Age 9-10', method=True, multi='AGE'),
        'ag11_12' : fields.function(_calc_agegroup, type = 'integer', string='Age 11-12', method=True, multi='AGE'),
        'ag13_16' : fields.function(_calc_agegroup, type = 'integer', string='Age 13-16', method=True, multi='AGE'),
        'ag17_22' : fields.function(_calc_agegroup, type = 'integer', string='Age 17-22', method=True, multi='AGE'),
        'ag22p' : fields.function(_calc_agegroup, type = 'integer', string='Age 22+', method=True, multi='AGE'),         
        }   
    
class dds_camp_activity_ticket(osv.osv): 
    """Activity Ticket"""
    _description = 'Activity Ticket'
    _name = 'dds_camp.activity.ticket'
    _order = 'actins_date_begin'
    
    def _calc_agegroup(self, cr, uid, ids, field_name, arg, context):
        res = {}
    
        for tck in self.browse(cr, uid, ids, context=context):    
            ag06_08 = 0
            ag09_10 = 0
            ag11_12 = 0
            ag13_16 = 0
            ag17_22 = 0
            ag22p = 0
            for par in tck.par_ids:
                if par.age_group =='06-08':
                    ag06_08 += 1
                elif par.age_group =='09-10':
                    ag09_10 += 1    
                elif par.age_group =='11-12':
                    ag11_12 += 1
                elif par.age_group =='13-16':
                    ag13_16 += 1
                elif par.age_group =='17-22':
                    ag17_22 += 1
                elif par.age_group =='22+':
                    ag22p += 1
            res[tck.id] = {'ag06_08': ag06_08,
                           'ag09_10': ag09_10,
                           'ag11_12': ag11_12, 
                           'ag13_16': ag13_16, 
                           'ag17_22':ag17_22,
                           'ag22p': ag22p
                           }           
        return res
    
    
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
        'actins_date_begin' : fields.related('act_ins_id', 'period_id','date_begin', type='datetime', string='Start Date/Time', store=True),
        'act_desc' : fields.related('act_ins_id', 'activity_id','desc', type='text', string='Description'),
        'ag06_08' : fields.function(_calc_agegroup, type = 'integer', string='Age 6-8', method=True, multi='AGE'),
        'ag09_10' : fields.function(_calc_agegroup, type = 'integer', string='Age 9-10', method=True, multi='AGE'),
        'ag11_12' : fields.function(_calc_agegroup, type = 'integer', string='Age 11-12', method=True, multi='AGE'),
        'ag13_16' : fields.function(_calc_agegroup, type = 'integer', string='Age 13-16', method=True, multi='AGE'),
        'ag17_22' : fields.function(_calc_agegroup, type = 'integer', string='Age 17-22', method=True, multi='AGE'),
        'ag22p' : fields.function(_calc_agegroup, type = 'integer', string='Age 22+', method=True, multi='AGE'),
        } 
    
    def button_unlink_ticket(self, cr, uid, ids, context=None):
        self.unlink(cr, SUPERUSER_ID, ids)
        
    
    def run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        
        exp_time = (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        #print "Check expiring", exp_time
        for tck in self.browse(cr, SUPERUSER_ID, self.search(cr, uid, [('state','=','open'),('reserved_time','<',exp_time)])):
            #print "Expiring", tck.id, tck.reserved_time, tck.name
            self.write(cr, uid, [tck.id], {'state': 'timeout'})
        
        exp_time = (datetime.datetime.now() - datetime.timedelta(minutes=240)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        for tck in self.browse(cr, SUPERUSER_ID, self.search(cr, uid, [('state','=','timeout'),('reserved_time','<',exp_time)])):
            #print "Deleting", tck.id, tck.reserved_time, tck.name
            self.unlink(cr, uid, [tck.id])
            