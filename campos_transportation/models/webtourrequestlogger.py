# -*- coding: utf-8 -*-
'''
Created on 16. apr. 2017

Usage:
from xml.dom import minidom

# Request all usDestination (usDestination/GetAll/) and convert to xml doc:
response_doc = minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usDestination/GetAll/'}).responce.encode('utf-8'))

Test can be done by create/add a new campos.webtour_req_logger record and enter the relevant webtour primitive as name. 
When the record is saved will the request be executed

@author: jda.dk
'''

from openerp import models, fields, api, tools
from ..interface import webtourinterface
from xml.dom import minidom
import logging

_logger = logging.getLogger(__name__)

class WebtourRequestLogger(models.Model):
    _name = 'campos.webtour_req_logger'
    name = fields.Char('Request')
    responce = fields.Text('Responce')


    @api.model
    def create(self, vals):
        _logger.info("Create Entered %s",vals['name'])
        rec = super(WebtourRequestLogger, self).create(vals)
        rec.responce = webtourinterface.get(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),
                                            self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),
                                            rec.name)
        self.env.cr.commit()
        
        return rec


    
    @api.one
    def get_usdestination_getall(self):  #A small test function.
        response_doc = minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usDestination/GetAll/'}).responce.encode('utf-8'))
        _logger.info("%s", response_doc.toprettyxml(indent="   "))
        
    
