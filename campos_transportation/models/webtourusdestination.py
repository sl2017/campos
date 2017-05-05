# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
from xml.dom import minidom
#from ..interface import webtourinterface

import logging
_logger = logging.getLogger(__name__)

class WebtourUsDestination(models.Model):
    _name = 'campos.webtourusdestination'
    destinationidno = fields.Char('Destination ID', required=True)
    name = fields.Char(compute='_compute_name', string='Name', store=True ,translate=True)
    webtourname = fields.Char('WebTour Name', required=False ,translate=True)
    placename = fields.Char('Place', required=False, translate=True)
    address = fields.Char('Address', required=False)
    zip_city = fields.Char('Zip City', required=False)
    latitude = fields.Char('Latitude', required=False)
    longitude = fields.Char('Longitude', required=False)
    note = fields.Char('Note', required=False,translate=True)

    @api.one
    @api.depends('placename','address','webtourname','destinationidno')
    def _compute_name(self):
        self.name = ''
        if self.webtourname==False:            
            if self.placename: self.name = self.name  + self.placename
            if self.address: self.name = self.name + ', ' + self.address.replace('\n', ', ').replace('\r', '')
            if self.destinationidno: self.name = self.name + ' (' + ' IDno:' + self.destinationidno + ')'
        else:
            if self.webtourname[:7] == 'SL2017-':
                if self.placename: self.name = self.name  + self.placename 
                if self.address: self.name = self.name + ', ' + self.address.replace('\n', ', ').replace('\r', '')
                if self.webtourname: self.name = self.name + ' (' + self.webtourname  
                if self.destinationidno: self.name = self.name + ' IDno:' + self.destinationidno + ')'
            else:
                if self.webtourname: self.name = '' + self.webtourname 
                if self.destinationidno: self.name = self.name + ' (IDno:' + self.destinationidno + ')'
            
    @api.model
    def get_destinations_cron(self):
        my_self = self.with_context(lang='da_DK');
        #_logger.info("get_destinations_cron context %s",self.env.context.get('lang', False))
        my_self.get_destinations()
         
    def get_destinations(self):
        _logger.info("get_destinations context %s",self.env.context.get('lang', False))
        def get_tag_data(nodetag):
            try:
                tag_data = usDestination.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None

            return tag_data

        webtourusdestination_obj = self.env['campos.webtourusdestination']

        #response_doc=webtourinterface.usdestinations_getall(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'))
        response_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usDestination/GetAll/'}).responce.encode('utf-8'))
 
        destinations = response_doc.getElementsByTagName("a:usDestination")

        for usDestination in destinations:
            destinationidno = get_tag_data("a:IDno")
            webtour_dict = {}
            webtour_dict["destinationidno"] = destinationidno
            webtour_dict["webtourname"] = get_tag_data("a:Name")
            webtour_dict["placename"] = get_tag_data("a:PlaceName")
            address = '' + get_tag_data("a:Address")
            webtour_dict["address"] = address
            crlf1 = address.find('\r')
            crlf2 = address.find('\r',crlf1+1)
            crlf3 = address.find('\r',crlf2+1)
            if crlf3 > 0:
               crlf1 = crlf2
               crlf2 = crlf3 
                
            if crlf1 > 0:
                if crlf2 > 0:
                    webtour_dict["zip_city"] = address[crlf1+1:crlf2]
                else:
                    webtour_dict["zip_city"] = address[crlf1+1:]           

            lat=get_tag_data("a:Latitude")
            lon=get_tag_data("a:Longitude")
 
            webtour_dict["latitude"] = lat    
            webtour_dict["longitude"] = lon
                
            webtour_dict["note"] = get_tag_data("a:Note")
            
            rs_webtourdestination = self.env['campos.webtourusdestination'].search([('destinationidno','=',destinationidno)])
            rs_webtourdestination_count = len(rs_webtourdestination)
            if rs_webtourdestination_count == 0:
                name = get_tag_data("a:Name")
                if name[:7] != 'SL2017-' and name not in ['Ringsted Centrum','Slagelse Vestsjællandscenter','Roskilde station','Næstved station']:
                    webtourusdestination_obj.create(webtour_dict)
            else:
                rs_webtourdestination.write(webtour_dict)

        return True
    
class WebtourUsDestinationView(models.Model):
    _name = 'campos.webtourusdestination.view'
    _auto = False
    _log_access = False

    name = fields.Char('Place', required=False)
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusdestination_view as
                    SELECT destinationidno::int as id, webtourname as name FROM campos_webtourusdestination
                    """
                    )
