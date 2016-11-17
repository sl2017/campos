# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourUsUser(models.Model):
    _name = 'campos.webtourususer'
    participant_id = fields.Char('participant ID', required=True)
    useridno = fields.Char('US User ID', required=False)
    troop_id = fields.Char('troop ID', required=True)

    @api.one
    def get_create_useridno(self):
        useridno=webtourinterface.ususer_getbyexternalid(self.participant_id)
        if useridno == "0":
            useridno=webtourinterface.ususer_create(self.participant_id, self.troop_id)
        if self.useridno != useridno:
            self.write({'useridno': useridno})
        return True
