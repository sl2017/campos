# -*- coding: utf-8 -*-
from openerp import models, fields, api
from xml.dom import minidom
from ..interface import webtourinterface
class WebtourUsDestination(models.Model):
    _name = 'campos.webtourusdestination'
    destinationidno = fields.Char('Destination ID', required=True)
    name = fields.Char(compute='_compute_name', string='Name')
    webtourname = fields.Char('WebTour Name', required=False)
    placename = fields.Char('Place', required=False)
    address = fields.Char('Address', required=False)
    latitude = fields.Char('Latitude', required=False)
    longitude = fields.Char('Longitude', required=False)
    note = fields.Char('Note', required=False)

    @api.one
    @api.depends('placename','address','webtourname','destinationidno')
    def _compute_name(self):
        
        if self.webtourname==False:
            self.name = '' + self.placename 
            self.name = self.name + ', ' + self.address.replace('\n', ', ').replace('\r', '')
            self.name = self.name + ' (' + ' IDno:' 
            self.name = self.name + self.destinationidno + ')'
        else:
            self.name = '' + self.placename 
            self.name = self.name + ', ' + self.address.replace('\n', ', ').replace('\r', '')
            self.name = self.name + ' (' + self.webtourname  
            self.name = self.name + ' IDno:' + self.destinationidno + ')'
            
    @api.model
    def get_destinations_cron(self):
        self.get_destinations()
         
    #def get_destinations_online(self, cr, uid, ids, context=None):
    #    get_destinations(self, cr, uid, context)

    def get_destinations(self):

        def get_tag_data(nodetag):
            try:
                tag_data = usDestination.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None

            return tag_data

        webtourusdestination_obj = self.env['campos.webtourusdestination']

        response_doc=webtourinterface.usdestinations_getall()

        destinations = response_doc.getElementsByTagName("a:usDestination")

        for usDestination in destinations:
            destinationidno = get_tag_data("a:IDno")
            webtour_dict = {}
            webtour_dict["destinationidno"] = destinationidno
            webtour_dict["webtourname"] = get_tag_data("a:Name")
            webtour_dict["placename"] = get_tag_data("a:PlaceName")
            webtour_dict["address"] = get_tag_data("a:Address")
            lat=get_tag_data("a:Latitude")
            lon=get_tag_data("a:Longitude")
            if lat[2] <>'.':
                webtour_dict["latitude"] = lat[:2] + '.' + lat[2:]
            else: 
                webtour_dict["latitude"] = lat
                
            if lon[2] <>'.':
                if (lon[0]=='1'):
                    webtour_dict["longitude"] = lon[:2] + '.' + lon[2:]
                else:
                    webtour_dict["longitude"] = lon[:1] + '.' + lon[1:]
            else:     
                webtour_dict["longitude"] = lon
                
            webtour_dict["note"] = get_tag_data("a:Note")

            rs_webtourdestination = self.env['campos.webtourusdestination'].search([('destinationidno','=',destinationidno)])
            rs_webtourdestination_count = len(rs_webtourdestination)
            if rs_webtourdestination_count == 0:
                webtourusdestination_obj.create(webtour_dict)
            else:
                rs_webtourdestination.write(webtour_dict)

        return True
