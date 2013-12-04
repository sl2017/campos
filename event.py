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


from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID


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

class dds_camp_event_participant(osv.osv):
    """ Event participants """
    _description = 'Event participant'
    _name = 'dds_camp.event.participant'
    _order = 'name'
    _columns = {
        'registration_id': fields.many2one('event.registration', 'Registration', required=True, select=True, ondelete='cascade'),
        'partner_id': fields.many2one('res.partner', 'Participant', states={'done': [('readonly', True)]}),        
        'name': fields.char('Name', size=64),
        'rel_phone': fields.char('Relatives phonenumber', size=64),
        'patrol' : fields.char('Patrol name', size=64),
        'appr_leader' : fields.boolean('Leder godkent')
    }
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
        
        'organization': fields.selection([('dds','Det Danske Spejderkorps'),
                                          ('dbs','Danske Baptisters Spejderkorps'),
                                          ('dgp',u'De Grønne Pigespejdere'),
                                          ('dui', 'DUI Leg og Virke'),
                                          ('fdf', 'FDF'),
                                          ('kfum','KFUM Spejderne'),
                                          ('waggs','WAGGS'),
                                          ('wosm', 'WOSM'),
                                          ('other','Other')],'Scout Organization',required=True),
        'scout_division' : fields.text('Division/District', size=64),       
        
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
        'shared_transport': fields.selection([('yes','Yes'),
                                              ('no', 'No'),
                                              ('maybe','Maybe')],'Shared transport',required=True),
                
        # Home Hsopitality
        'hh_precamp' : fields.boolean('Would like home hospitality before the camp'),
        'hh_aftercamp' : fields.boolean('Would like home hospitality after the camp'),
        'want_friendshipgroup': fields.boolean('Want a friendship group'),
        'has_friendshipgroup' : fields.boolean('Do you have a friendship group participate in the camp'),
        'friendshipgroup_name' : fields.char('Name of friendship group'),
        
        'hcap' : fields.boolean('Do you bring any handicapped scouts'),
        'hcap_desc': fields.text('Describe the handicap'),
        'hcap_specneeds' : fields.text('Describe speciel needs'),
        'food_allergy' : fields.boolean('Do you have any food allergy sufferer'),
        'food_allergy_desc': field.text('Descibe the allergy'),
        
        #Internal fields
        'agreements': fields.text('What have been arranged'),
        'internal_note' : fields.text(''),
        
                
                
                
    }
    
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

