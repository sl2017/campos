'''
Created on 14. jan. 2017

@author: jda.dk
'''
from openerp import models, fields, api

class webtourconfig(models.Model):
    _name = 'campos.webtourconfig'

    event_id = fields.Many2one('event.event', 'id')
    campdestinationid = fields.Many2one('campos.webtourusdestination', 'id',ondelete='set null')
    tocamp_campos_TripType_id = fields.Many2one('campos.webtourusneed.triptype','To Camp TripType', ondelete='set null')
    fromcamp_campos_TripType_id = fields.Many2one('campos.webtourusneed.triptype','From Camp TripType', ondelete='set null')