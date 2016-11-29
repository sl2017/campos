# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourUsGroup(models.Model):
    _name = 'campos.webtourusgroup'
    troop_id = fields.Char('troop ID', required=True)
    groupidno = fields.Char('US Group ID', required=False)

    def get_create_webtourusgroup(troop_id):
        webtourusgroup_obj = self.pool.get('campos.webtourusgroup')
        rs_webtourusgroup = self.pool.get('campos.webtourusgroup').search(cr, uid, [('troop_id','=',troop_id)])
        rs_webtourusgroup_count = len(rs_webtourusgroup)
        if rs_webtourusgroup_count == 0:
            webtour_dict = {}
            webtour_dict["troop_id"] = troop_id
            newusgroup=webtourusgroup_obj.create(cr, uid, webtour_dict)
            get_create_groupidno(newusgroup)
        rs_webtourusgroup = self.pool.get('campos.webtourusgroup').search(cr, uid, [('troop_id','=',troop_id)])
        return rs_webtourusgroup.groupidno

    @api.one
    def get_create_groupidno(self):
        groupidno=webtourinterface.usgroup_getbyname(self.troop_id)
        if groupidno == "0":
            groupidno=webtourinterface.usgroup_create(self.troop_id)
        if self.groupidno != groupidno:
            self.write({'groupidno': groupidno})
        return True
