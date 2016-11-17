# -*- coding: utf-8 -*-
from openerp import models, fields, api
from xml.dom import minidom
from ..interface import webtourinterface
class WebtourUsDestination(models.Model):
    _name = 'campos.webtourusdestination'
    destinationidno = fields.Char('Destination ID', required=True)
    name = fields.Char('Name', required=False)
    placename = fields.Char('Place', required=False)
    address = fields.Char('Address', required=False)
    latitude = fields.Char('Latitude', required=False)
    longitude = fields.Char('Longitude', required=False)
    note = fields.Char('Note', required=False)

    def get_destinations_online(self, cr, uid, ids, context=None):
        get_destinations(self, cr, uid, context)

    def get_destinations(self, cr, uid, context=None):

        def get_tag_data(nodetag):
            try:
                tag_data = usDestination.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None

            return tag_data

        webtourusdestination_obj = self.pool.get('campos.webtourusdestination')

        response_doc=webtourinterface.usdestinations_getall()

        destinations = response_doc.getElementsByTagName("a:usDestination")

        for usDestination in destinations:
            destinationidno = get_tag_data("a:IDno")
            webtour_dict = {}
            webtour_dict["destinationidno"] = destinationidno
            webtour_dict["name"] = get_tag_data("a:Name")
            webtour_dict["placename"] = get_tag_data("a:PlaceName")
            webtour_dict["address"] = get_tag_data("a:Address")
            webtour_dict["latitude"] = get_tag_data("a:Latitude")
            webtour_dict["longitude"] = get_tag_data("a:Longitude")
            webtour_dict["note"] = get_tag_data("a:Note")

            rs_webtourdestination = self.pool.get('campos.webtourusdestination').search(cr, uid, [('destinationidno','=',destinationidno)])
            rs_webtourdestination_count = len(rs_webtourdestination)
            if rs_webtourdestination_count == 0:
                webtourusdestination_obj.create(cr, uid, webtour_dict)
            else:
                webtourusdestination_obj.write(cr, uid, rs_webtourdestination, webtour_dict)

        return True

    @api.multi
    def get_destinations_org(self):

        def get_tag_data(nodetag):
            try:
                tag_data = usDestination.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None

            return tag_data

        response_doc=webtourinterface.usdestinations_getall()

        destinations = response_doc.getElementsByTagName("a:usDestination")

        for usDestination in destinations:
            destinationidno = get_tag_data("a:IDno")
            webtour_dict = {}
            webtour_dict["destinationidno"] = destinationidno
            webtour_dict["name"] = get_tag_data("a:Name")
            webtour_dict["placename"] = get_tag_data("a:PlaceName")
            webtour_dict["address"] = get_tag_data("a:Address")
            webtour_dict["latitude"] = get_tag_data("a:Latitude")
            webtour_dict["longitude"] = get_tag_data("a:Longitude")
            webtour_dict["note"] = get_tag_data("a:Note")

            rs_webtourdestination = self.env['campos.webtourusdestination'].search([('destinationidno','=',destinationidno)])
            rs_webtourdestination_count = rs_webtourdestination.search_count([])
            if rs_webtourdestination_count == 0:
                rs_webtourdestination.create(webtour_dict)
            else:
                rs_webtourdestination.write(webtour_dict)

            self.note = destinationidno
        self.env.cr.commit()

        self.env.invalidate_all()

        return True
