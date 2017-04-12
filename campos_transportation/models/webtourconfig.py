'''
Created on 14. jan. 2017

@author: jda.dk
'''
from openerp import models, fields, api

class webtourconfig(models.Model):
    _name = 'campos.webtourconfig'

    event_id = fields.Many2one('event.event', 'id')
    campdestinationid = fields.Many2one('campos.webtourusdestination', 'id',ondelete='set null')
    tocamp_campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','To Camp TripType', ondelete='set null')
    fromcamp_campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','From Camp TripType', ondelete='set null')
    
    
class WebtourTripType(models.Model):
    _description = 'Webtour Trip Types'
    _name = 'campos.webtourconfig.triptype'
   
    name = fields.Char('Webtour Trip Type', required=True)
    traveldate_ids = fields.One2many('campos.webtourconfig.triptype.date','campos_TripType_id','Travel Days')
    returnjourney = fields.Boolean('Return Journey')


class WebtourTripTypeDate(models.Model):
    _description = 'Webtour Trip Types Date'
    _name = 'campos.webtourconfig.triptype.date'
    campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','Webtour_TripType', ondelete='set null')
    name = fields.Date('Date', required=True) 
    #date = fields.Date('Date', required=True)
    
class WebtourEvent(models.Model):
    _inherit = 'event.event'
    
    webtourconfig_id = fields.Many2one('campos.webtourconfig','Webtour Configuration')