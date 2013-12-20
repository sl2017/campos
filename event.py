# -*- coding: utf-8 -*-
##############################################################################
#
#    DDS Member
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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class dds_camp_scoutorg(osv.osv):
    """ Scout Organizations"""
    _description = 'Scout Organizations'
    _name = 'dds_camp.scout.org'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=128),
        'country_id': fields.many2one('res.country', 'Country'),
        'sex' : fields.char('Sex', size=128),
        'worldorg': fields.selection([('wagggs','WAGGGS'),
                                      ('wosm', 'WOSM'),
                                      ('other','Other')],'World Organization'),
    }
dds_camp_scoutorg()

class dds_camp_municipality(osv.osv):
    """ Kommuner """
    _description = 'DK Kommuner'
    _name = 'dds_camp.municipality'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=64),
        'number': fields.integer('Number')
    }
dds_camp_municipality()


class event_event(osv.osv):
    """ Inherits Event and adds DDS Camp information in the partner form """
    _inherit = 'event.event'
    
    _columns = {
        'webshop_product_nid': fields.integer('Webshop nid'),
        }
    
    def button_open_webevent_url(self, cr, uid, ids, context): 
        """ Open Event
        @return: True
        """
        # logger.info("%s.button_open_drawing_url(): ids = %s", self._name, ids)
        webevent_ref = self.browse(cr, uid, ids)[0].webshop_product_nid
        if webevent_ref:
            return { 'type': 'ir.actions.act_url', 'url': r"%s/node/%s" % (r"http://e2014.gruppe.dds.dk", webevent_ref), 'nodestroy': True, 'target': 'new' }
        return True    

event_event()

class dds_camp_event_participant_day(osv.osv):
    """ Event participant day """
    _description = 'Event participant day'
    _name = 'dds_camp.event.participant.day'
    _order = 'date'
    _columns = {
        'participant_id': fields.many2one('dds_camp.event.participant', 'Participant', required=True, select=True, ondelete='cascade'),
        'date' : fields.date('Date'),
        'state': fields.boolean('Participate'),
        'name' : fields.char('Name', size=64)
        }
    
    def button_reg_confirm(self, cr, uid, ids, context=None, *args):
        return self.write(cr, uid, ids, {'state': True})
             
    def button_reg_cancel(self, cr, uid, ids, context=None, *args):
        return self.write(cr, uid, ids, {'state': False})
dds_camp_event_participant_day()    
 
class dds_camp_event_participant(osv.osv):
    """ Event participants """
    _description = 'Event participant'
    _name = 'dds_camp.event.participant'
    _order = 'name'
    _columns = {
        'registration_id': fields.many2one('event.registration', 'Registration', required=True, select=True, ondelete='cascade'),
        'partner_id': fields.many2one('res.partner', 'Participant'),  
        # The following fields are synced to res_partner on Write      
        'name': fields.char('Name', size=128, required=True, select=True),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'zip': fields.char('Zip', change_default=True, size=24),
        'city': fields.char('City', size=128),
        'state_id': fields.many2one("res.country.state", 'State'),
        'country_id': fields.many2one('res.country', 'Country'),
        'email': fields.char('Email', size=240),
        'phone': fields.char('Phone', size=64),
        # end of res_partner fields
        
        'rel_phone': fields.char('Relatives phonenumber', size=64),

        'patrol' : fields.char('Patrol name', size=64),
        'appr_leader' : fields.boolean('Leder godkent'),
        'days_ids': fields.one2many('dds_camp.event.participant.day', 'participant_id', 'Participation'),
    }
    
    _sql_constraints = [
        ('participation_uniq', 'unique(registration_id, partner_id)', 'Participant must be unique!'),
    ]
    
    def action_create_day_lines(self, cr, uid, ids, context):
        day_obj = self.pool.get('dds_camp.event.participant.day')
        participant = self.browse(cr, uid, ids)[0]
        dates = {}
       
        if participant.days_ids:
            for d in participant.days_ids:
                dates[d.date] = d.id
        from_date = datetime.datetime.strptime(participant.registration_id.event_id.date_begin, DEFAULT_SERVER_DATETIME_FORMAT).date()
        to_date = datetime.datetime.strptime(participant.registration_id.event_id.date_end, DEFAULT_SERVER_DATETIME_FORMAT).date()  
        print "dates", from_date, to_date
        dt = from_date
        delta = datetime.timedelta(days=1)
        while dt <= to_date:
            if dt.strftime(DEFAULT_SERVER_DATE_FORMAT) not in dates.keys():
                day_obj.create(cr, SUPERUSER_ID, {'participant_id' : participant.id,
                                         'date' : dt,
                                         'state': True})
                dt += delta
            else:
                day_obj.write(cr, SUPERUSER_ID, [dates[dt]], {'state' : True})    
     
    def action_create_day_some(self, cr, uid, ids, context):
        day_obj = self.pool.get('dds_camp.event.participant.day')
        participant = self.browse(cr, uid, ids)[0]
        dates = {}
       
        if participant.days_ids:
            for d in participant.days_ids:
                dates[d.date] = d.id
        from_date = datetime.datetime.strptime(participant.registration_id.event_id.date_begin, DEFAULT_SERVER_DATETIME_FORMAT).date()
        to_date = datetime.datetime.strptime(participant.registration_id.event_id.date_end, DEFAULT_SERVER_DATETIME_FORMAT).date()  
        print "dates", from_date, to_date
        dt = from_date
        delta = datetime.timedelta(days=1)
        while dt <= to_date:
            if dt.strftime(DEFAULT_SERVER_DATE_FORMAT) not in dates.keys():
                day_obj.create(cr, SUPERUSER_ID, {'participant_id' : participant.id,
                                         'date' : dt,
                                         'state': False})
                dt += delta
        
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, [partner_id])[0]
        res = {}
        values = {}
        for k in ['name', 'street', 'street2', 'email','phone']:
            values.update({k : getattr(partner, k)})
        values.update({'state_id' : partner.state_id.id,
                       'country_id' : partner.country_id.id})
        res['value'] = values
        print res
        return res
    
#     def write(self, cr, uid, ids, vals, context=None):
#         res = super(dds_camp_event_participant, self).write(cr, uid, ids, vals, context=context)
#         partner_obj = self.pool.get('res.partner')
#         print "write", ids, vals 
#         values = {}
#         for k in ['name', 'street', 'street2', 'state_id', 'country_id', 'email','phone']:
#             if vals.has_key(k):    
#                 values.update({k : vals[k]})
#             if vals.has_key('partner_id'):
#                 partner_obj.write(cr,uid,[vals['partner_id']], values, context)
#                 print "write", values
#             else:
#                 #values.update({'parent_id' : par.registration_id.partner_id.id})
#                 partner_id = partner_obj.create(cr,uid, values, context)
#                 self.write(cr, uid, {'partner_id': partner_id}, context)
#                 print "create", partner_id, values            
#         return res
               
dds_camp_event_participant()
    
class event_registration(osv.osv):
    """ Inherits Event and adds DDS Camp information in the Registration form """
    _inherit = 'event.registration'
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            display_name = record.name + ' (' + (record.event_id.name or '') + ')'
            res.append((record['id'], display_name))
        return res
    
            
    _columns = {
        'webshop_orderno': fields.integer('Webshop Order No'),
        'webshop_order_product_id': fields.integer('Webshop Order Line No'),
        'participant_ids': fields.one2many('dds_camp.event.participant', 'registration_id', 'Registration.'),
        'country_id': fields.many2one('res.country', 'Country'),
        'organization_id': fields.many2one('dds_camp.scout.org', 'Scout Organization'),
        'organization': fields.selection([('dds','Det Danske Spejderkorps'),
                                          ('dbs','Danske Baptisters Spejderkorps'),
                                          ('dgp',u'De Grønne Pigespejdere'),
                                          ('dui', 'DUI Leg og Virke'),
                                          ('fdf', 'FDF'),
                                          ('kfum','KFUM Spejderne'),
                                          ('waggs','WAGGS'),
                                          ('wosm', 'WOSM'),
                                          ('other','Other')],'Scout Organization',required=True),
        'scout_division' : fields.char('Division/District', size=64),
        'municipality_id': fields.many2one('dds_camp.municipality', 'Municipality', select=True, ondelete='set null'),       
        
        # Contact
        'contact_partner_id': fields.many2one('res.partner', 'Contact', states={'done': [('readonly', True)]}),
        
#         'contact_name': fields.char('Contact Name', size=128, required=True, select=True),
#         'contact_street': fields.char('Street', size=128),
#         'contact_street2': fields.char('Street2', size=128),
#         'contact_zip': fields.char('Zip', change_default=True, size=24),
#         'contact_city': fields.char('City', size=128),
#         'contact_state_id': fields.many2one("res.country.state", 'State'),
#         'contact_country_id': fields.many2one('res.country', 'Country'),
#         'contact_email': fields.char('Email', size=240),
#         'contact_phone': fields.char('Phone', size=64),
#         
        # Economic Contact
        'econ_partner_id': fields.many2one('res.partner', 'Economic Contact', states={'done': [('readonly', True)]}),
#         
#         'econ_name': fields.char('Economic Contact Name', size=128, required=True, select=True),
#         'econ_street': fields.char('Street', size=128),
#         'econ_street2': fields.char('Street2', size=128),
#         'econ_zip': fields.char('Zip', change_default=True, size=24),
#         'econ_city': fields.char('City', size=128),
#         'econ_state_id': fields.many2one("res.country.state", 'State'),
#         'econ_country_id': fields.many2one('res.country', 'Country'),
#         'econ_email': fields.char('Email', size=240),
#         'econ_phone': fields.char('Phone', size=64),
        'foreigners' : fields.boolean('Foreigners'),
        'signed_up' : fields.boolean('Signed up'),
        'shared_transport': fields.selection([('yes','Yes'),
                                              ('no', 'No'),
                                              ('maybe','Maybe')],'Shared transport',required=True),
                
        # Home Hsopitality
        'hh_precamp' : fields.boolean('Would like home hospitality before the camp'),
        'hh_aftercamp' : fields.boolean('Would like home hospitality after the camp'),
        'hh_precamp_prv' : fields.boolean('Can provide home hospitality before the camp'),
        'hh_aftercamp_prv' : fields.boolean('Can provide home hospitality after the camp'),
        'want_friendshipgroup': fields.boolean('Want a friendship group'),
        'has_friendshipgroup' : fields.boolean('Do you have a friendship group participate in the camp'),
        'friendshipgroup_name' : fields.char('Name of friendship group'),

        'hcap' : fields.boolean('Do you bring any handicapped scouts'),
        'hcap_desc': fields.text('Describe the handicap'),
        'hcap_specneeds' : fields.text('Describe speciel needs'),
        'food_allergy' : fields.boolean('Do you have any food allergy sufferer'),
        'food_allergy_desc': fields.text('Descibe the allergy'),
        
        #Internal fields
        'agreements': fields.text('What have been arranged'),
        'internal_note' : fields.text('Internal note'),
    
    }
    
        
    def onchange_country_id(self, cr, uid, ids, country_id, context=None):       
                
        res = {}           
        # - set a domain on organization_id
        res['domain'] = {'organization_id': [('country_id','=',country_id)]}      
        return res
    
    
    def button_open_weborder_url(self, cr, uid, ids, context): 
        """ Open Pre Registretion
        @return: True
        """
        # logger.info("%s.button_open_drawing_url(): ids = %s", self._name, ids)
        weborder_ref = self.browse(cr, uid, ids)[0].webshop_orderno
        if weborder_ref:
            return { 'type': 'ir.actions.act_url', 'url': r"%s/dds/tilmelding/orders/%s/invoice" % (r"http://e2014.gruppe.dds.dk", weborder_ref), 'nodestroy': True, 'target': 'new' }

        return True
         
event_registration()

