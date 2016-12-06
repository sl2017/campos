# -*- coding: utf-8 -*-
from openerp import models, fields, api
from xml.dom import minidom
class WebtourUsNeed(models.Model):
    _name = 'campos.webtourusneed'
    participant_id = fields.Many2one('campos.event.participant','Participant ID', ondelete='set null')
    campos_deleted = fields.Boolean('CampOs Deleted', default=False)
    campos_startdatetime = fields.Char('CampOs StartDateTime', required=False)
    campos_startdestinationidno = fields.Char('CampOs StartDestinationIdNo', required=False)
    campos_startnote = fields.Char('CampOs StartNote', required=False)
    campos_enddatetime = fields.Char('CampOs EndDateTime', required=False)
    campos_enddestinationidno = fields.Char('CampOs EndDestinationIdNo', required=False)
    campos_endnote = fields.Char('CampOs EndNote', required=False)
    webtour_needidno = fields.Char('Webtour Need ID', required=False)
    webtour_useridno = fields.Char('Webtour User ID', required=False)
    webtour_groupidno = fields.Char('Webtour Groupidno', required=False)
    webtour_deleted = fields.Boolean('Webtour Deleted', default=False)
    webtour_startdatetime = fields.Char('Webtour StartDateTime', required=False)
    webtour_startdestinationidno = fields.Char('Webtour StartDestinationIdNo', required=False)
    webtour_startnote = fields.Char('Webtour StartNote', required=False)
    webtour_enddatetime = fields.Char('Webtour EndDateTime', required=False)
    webtour_enddestinationidno = fields.Char('Webtour EndDestinationIdNo', required=False)
    webtour_endnote = fields.Char('Webtour EndNote', required=False)
    @api.one
    def get_create_webtour_need(self):
        if self.needidno == None:
            rs_webtouruser = self.env['webtourususer'].search(["participant_id","=",self.participant_id], limit=1)
            sql_useridno = rs_webtouruser.useridno
            sql_troopid = rs_webtouruser.troopid
            rs_webtourusgroup = self.env['webtourusgroup'].search(["troopid","=",sql_troopid], limit=1)
            sql_groupidno = rs_webtourusgroup.groupidno
            request="UserIDno="+sql_useridno
            request=request+"&GroupIDno="+sql_groupidno
            request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
            request=request+"&StartDateTime="+self.campos_startdatetime
            request=request+"&StartNote="+self.campos_startnote
            request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
            request=request+"&EndDateTime="+self.campos_enddatetime
            request=request+"&EndNote="+self.campos_endnote
            response_doc=webtourinterface.usneed_create(request)
        else:
            request="IDno="+selv.webtour_needidno
            response_doc=webtourinterface.usneed_getbyidno(request)
        webtour_dict = {}
        webtour_dict["webtour_needidno"] = doc.getElementsByTagName("a:IDno")[0].firstchild.data
        webtour_dict["webtour_useridno"] = doc.getElementsByTagName("a:UserIDno")[0].firstchild.data
        webtour_dict["webtour_groupidno"] = doc.getElementsByTagName("a:GroupIDno")[0].firstchild.data
       #webtour_dict["webtour_deleted"] = doc.getElementsByTagName("a:IDno")[0].firstchild.data
        webtour_dict["webtour_startdatetime"] = doc.getElementsByTagName("a:StartDateTime")[0].firstchild.data
        webtour_dict["webtour_startdestinationidno"] = doc.getElementsByTagName("a:StartDestinationIDno")[0].firstchild.data
        webtour_dict["webtour_startnote"] = doc.getElementsByTagName("a:StartNote")[0].firstchild.data
        webtour_dict["webtour_enddatetime"] = doc.getElementsByTagName("a:EndDateTime")[0].firstchild.data
        webtour_dict["webtour_enddestinationidno"] = doc.getElementsByTagName("a:EndDestinationIDno")[0].firstchild.data
        webtour_dict["webtour_endnote"] = doc.getElementsByTagName("a:EndNote")[0].firstchild.data

        self.write(webtour_dict)

        return True
