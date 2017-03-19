# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourUsUser(models.Model):
    _name = 'campos.webtourususer'
    participant_id = fields.Char('participant ID', required=True)
    troop_id = fields.Char('troop ID', required=True)
    ususeridno = fields.Char('US User ID', required=False)
    usgroupidno = fields.Char('US Group ID', required=False)

    def get_create_webtourususer_online(self, cr, uid, ids, context=None):
        self.get_create_webtourususer(cr, uid, ids, context)

    def get_create_webtourususer(self, cr, uid, ids, participant, context=None):
        webtourususer_obj = self.pool.get('campos.webtourususer')
        rs_webtourususer = self.pool.get('campos.webtourususer').search(cr, uid, ids, [('participant_id','=',participant.participant_id)])
        rs_webtourususer_count = len(rs_webtourususer)
        if rs_webtourususer_count == 0:
            webtourusgroup_obj = self.pool.get('campos.webtourusgroup')
            groupidno=webtourusgroup_obj.get_create_webtourusgroup(participant.troop_id)
            if groupidno!=None:
                webtour_dict = {}
                webtour_dict["participant_id"] = participant.participant_id
                webtour_dict["troop_id"] = participant.troop_id
                webtour_dict["usgroupidno"] = groupidno
                newususer=webtourususer_obj.create(cr, uid, webtour_dict)
                get_create_useridno(newususer)
                rs_webtourususer = self.pool.get('campos.webtourususer').search(cr, uid, ids, [('participant_id','=',participant.participant_id)])
        return rs_webtourususer

    def get_create_useridno_online(self, cr, uid, ids, context=None):
        get_create_useridno(self, cr, uid, context)

    def get_create_useridno(self, cr, uid, context=None):
        ususeridno=webtourinterface.ususer_getbyexternalid(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.participant_id)
        if ususeridno == "0":
            ususeridno=webtourinterface.ususer_create(self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url'),self.env['ir.config_parameter'].get_param('campos_transportation_webtour.url_loginpart'),self.participant_id, self.usgroupidno, self.participant_id, self.troop_id)
        if self.ususeridno != ususeridno:
            self.write({'ususeridno': ususeridno})
        return True
