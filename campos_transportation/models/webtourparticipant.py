# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface

import logging

_logger = logging.getLogger(__name__)

class WebtourParticipant(models.Model):
    _inherit = 'campos.event.participant'
    
    webtourususeridno = fields.Char('webtour us User ID no', required=False)
    webtourusgroupidno = fields.Char(string='webtour us Group ID no', related='registration_id.webtourusgroupidno')                                 
    
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
    
    @api.model
    def get_create_usgroupidno_tron(self):
        rs_missingusgroupidno= self.env['event.registration'].search([('event_id', '=', 1),('state', '=', 'open'),('scoutgroup', '=', True)])
        for rec in rs_missingusgroupidno:
            _logger.info("get_create_usgroupidno_tron %s %s %s %s",str(rec.state), str(rec.id), rec.name,rec.webtourusgroupidno)                    # get or create usgroup from webtour matching troop_id
            newidno=webtourinterface.usgroup_getbyname(str(rec.id))
            if newidno == "0":
                newidno=webtourinterface.usgroup_create(str(rec.id))

            if newidno <> "0":
                dicto = {}
                dicto["webtourusgroupidno"] = newidno
                rec.write(dicto) 

        return True