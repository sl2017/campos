# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourParticipant(models.Model):
    _inherit = 'campos.event.participant'
    
    webtourusidno = fields.Char('webtour us ID no', required=False)

    tocampfromdestination = fields.Many2one('campos.webtourusdestination',
                                            'destinationidno',
                                            ondelete='set null')
    fromcamptodestination = fields.Many2one('campos.webtourusdestination',
                                            'destinationidno',
                                            ondelete='set null')
    tocampdate = fields.Date('To Camp Date', required=False)
    fromcampdate = fields.Date('From Camp Date', required=False)
    usecamptransporttocamp = fields.Boolean('Use Camp Transport to Camp', required=False, default=True)
    usecamptransportfromcamp = fields.Boolean('Use Camp Transport from Camp', required=False, default=True)
    tocampneedidno = fields.Char('To Camp Need ID', required=False)
    fromcampneedidno = fields.Char('From Camp Need ID', required=False)

    @api.model
    def get_create_usIDno_tron(self):
        rs_missingusgroupidno= self.env['campos.event.participant'].search([('webtourusidno','=',None),('active', '=', True),('scoutgroup', '=', True)])
        for rec in rs_missingusgroupidno:
                    # get or create usgroup from webtour matching troop_id
            newidno=webtourinterface.usgroup_getbyname(rec.registration_id)
            if newidno == "0":
                newidno=webtourinterface.usgroup_create(rec.registration_id)

                if newidno <> "0":
                    dicto = {}
                    dicto["webtourusidno"] = newidno
                    rec.dicto(dict) 

        return True