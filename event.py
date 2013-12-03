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


import sys
from osv import fields,osv
from openerp import tools
import pprint
from datetime import date, datetime
import netsvc
import hmac, hashlib, random, xmlrpclib, time, csv, urllib2
import logging
import re
import string

from cStringIO import StringIO
try:
    import xlwt
except ImportError:
    xlwt = None

_logger = logging.getLogger(__name__)


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
            return { 'type': 'ir.actions.act_url', 'url': r"%s/node/%s" % (r"http://www.mikkelskov.dk", webevent_ref), 'nodestroy': True, 'target': 'new' }
        return True    

    event_event()

class dds_camp_event_participant(osv.osv):
    """ Event participants """
    _description = 'Event participant'
    _name = 'dds_camp.event.participant'
    _order = 'name'
    _columns = {
        'registration_id': fields.many2one('event.registration', 'Registration', required=True, select=True, ondelete='cascade'),        
        'name': fields.char('Name', size=64),
        'value': fields.char('Value', size=256),
    }
dds_member_event_regattr()
    
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
        
        # Contact
        'contact_name': fields.char('Contact Name', size=128, required=True, select=True),
        'contact_street': fields.char('Street', size=128),
        'contact_street2': fields.char('Street2', size=128),
        'contact_zip': fields.char('Zip', change_default=True, size=24),
        'contact_city': fields.char('City', size=128),
        'contact_state_id': fields.many2one("res.country.state", 'State'),
        'contact_country_id': fields.many2one('res.country', 'Country'),
        'contact_email': fields.char('Email', size=240),
        'contact_phone': fields.char('Phone', size=64),
        
        # Economic Contact
        'econ_name': fields.char('Economic Contact Name', size=128, required=True, select=True),
        'econ_street': fields.char('Street', size=128),
        'econ_street2': fields.char('Street2', size=128),
        'econ_zip': fields.char('Zip', change_default=True, size=24),
        'econ_city': fields.char('City', size=128),
        'econ_state_id': fields.many2one("res.country.state", 'State'),
        'econ_country_id': fields.many2one('res.country', 'Country'),
        'econ_email': fields.char('Email', size=240),
        'econ_phone': fields.char('Phone', size=64),
        
    }
    
    def button_open_weborder_url(self, cr, uid, ids, context): 
        """ Open Blåt Medlem
        @return: True
        """
        # logger.info("%s.button_open_drawing_url(): ids = %s", self._name, ids)
        weborder_ref = self.browse(cr, uid, ids)[0].webshop_orderno
        if weborder_ref:
            return { 'type': 'ir.actions.act_url', 'url': r"%s/dds/tilmelding/orders/%s/invoice" % (r"http://www.mikkelskov.dk", weborder_ref), 'nodestroy': True, 'target': 'new' }

        return True
         
event_registration()

