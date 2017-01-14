'''
Created on 14. jan. 2017

@author: jda.dk
'''
from openerp import models, fields, api

class webtourconfig(models.Model):
    _name = 'campos.webtourconfig'

    event_id = fields.Many2one('event.event', 'id')
    webtoururl = fields.Char('WEBtour URL', required=True)    
    login_url_part = fields.Char('WEBtour Login part of URL', required=True)
    campdestinationid = fields.Many2one('campos.webtourusdestination', 'id',ondelete='set null')
