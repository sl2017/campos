# -*- coding: utf-8 -*-
##############################################################################
#
#   Copyright (c) 2016 Hans Henrik Gabelgaard
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

import logging
from openerp import api, fields
from openerp import exceptions
from openerp.tools.translate import _
from openerp.addons.base_geoengine import geo_model
from openerp.addons.base_geoengine import fields as geo_fields

from urllib import urlencode
from urllib2 import urlopen
import json
import traceback

_logger = logging.getLogger(__name__)


class ResPartner(geo_model.GeoModel):
    """Add geo_point to partner using a function field"""
    _inherit = "res.partner"

    @api.one
    def geocode_address(self):
        """Get the latitude and longitude by requesting "dava"
        see http://dawa.aws.dk/
        """
        params = {
                  'q': ','.join(filter(None, [self.street, self.zip, self.city]))
                  }
        for key in params:
            params[key] = params[key].encode('utf-8')
        url = 'http://dawa.aws.dk/adresser/autocomplete?%s' % urlencode(params)
        try:
            aws_json = json.load(urlopen(url))
            aws = aws_json[0]
            _logger.info("AWS: %s", aws)
            
            if aws['adresse']:
                url = 'http://dawa.aws.dk/adresser/%s?format=geojson' % aws['adresse']['id']
                _logger.info("AWS URL: %s", url)
                
                aws_json = json.load(urlopen(url))
                _logger.info("AWS json: %s", aws_json)
                aws = aws_json
                _logger.info("AWS Geo: %s", aws)
        
            self.write({
                        'partner_latitude': aws['properties'].get(u'wgs84koordinat_bredde'),
                        'partner_longitude': aws['properties'].get(u'wgs84koordinat_længde'),
                        'date_localization': fields.Date.today()
                        })
        except:
            _logger.info(traceback.format_exc())
            pass
        
    @api.one
    def geo_localize(self):
        self.geocode_address()
        return True

    @api.one
    @api.depends('partner_latitude', 'partner_longitude')
    def _get_geo_point(self):
        """
        Set the `geo_point` of the partner depending of its `partner_latitude`
        and its `partner_longitude`
        **Notes**
        If one of those parameters is not set then reset the partner's
        geo_point and do not recompute it
        """
        if not self.partner_latitude or not self.partner_longitude:
            self.geo_point = False
        else:
            self.geo_point = geo_fields.GeoPoint.from_latlon(
                self.env.cr, self.partner_latitude, self.partner_longitude)

    geo_point = geo_fields.GeoPoint(
        readonly=True, store=True, compute='_get_geo_point')
