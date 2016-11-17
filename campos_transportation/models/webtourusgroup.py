# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourUsGroup(models.Model):
    _name = 'campos.webtourusgroup'
    troop_id = fields.Char('troop ID', required=True)
    groupidno = fields.Char('US Group ID', required=False)

    @api.one
    def get_create_groupidno(self):
        groupidno=webtourinterface.usgroup_getbyname(self.troop_id)
        if groupidno == "0":
            groupidno=webtourinterface.usgroup_create(self.troop_id)
        if self.groupidno != groupidno:
            self.write({'groupidno': groupidno})
        return True
