'''
Created on 2. dec. 2016

@author: jda.dk
'''
from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourRegistration(models.Model):
    _inherit = 'event.registration'
    webtourusgroupidno = fields.Char('webtour us Group ID no', required=False, Default='')
    