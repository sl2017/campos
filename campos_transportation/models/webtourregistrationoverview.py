'''
Created on 15. apr. 2017

@author: jda.dk
'''
from openerp import models, fields, api, tools

import logging

_logger = logging.getLogger(__name__)

       
class WebtourRegistrationOverview(models.Model):
    _name = 'campos.webtourregistrationoverview'
    _auto = False
    _log_access = False

    registration_id = fields.Many2one('event.registration','Registration ID', readonly=True)
    regstate = fields.Char('registration state', readonly=True)
    scoutgroup = fields.Boolean('scoutgroup', readonly=True)
    countrycode = fields.Char('country code', readonly=True)
    scoutorgcountrycode = fields.Char('scout org country code', readonly=True)
    group_entrypoint = fields.Many2one('event.registration.entryexitpoint','Point of entry into Denmark', readonly=True)
    group_exitpoint = fields.Many2one('event.registration.entryexitpoint','Point of exit from Denmark', readonly=True)
    webtourgrouptocampdestination_id = fields.Many2one('campos.webtourusdestination','Group to camp destination', readonly=True)
    webtourgroupfromcampdestination_id = fields.Many2one('campos.webtourusdestination','Group from camp destination', readonly=True)
    webtourdefaulthomedestination = fields.Many2one('campos.webtourusdestination','default home destination', readonly=True)
    webtourdefaulthomedistance = fields.Float('Webtour Pickup Map Distance', readonly=True)
    webtourdefaulthomeduration = fields.Char('Webtour Pickup Map Duration', readonly=True)
    webtourusgroupidno = fields.Char('webtour us Group ID no', readonly=True) 
    name = fields.Char('name', readonly=True)
    partnerid = fields.Integer('partnerid', readonly=True)
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourregistrationoverview as
                    SELECT r.id,r.id as registration_id,r.state as regstate, scoutgroup
                    ,regpcountry.code as countrycode
                    ,scoutorgcountry.code as scoutorgcountrycode                                       
                    ,group_entrypoint,group_exitpoint
                    ,webtourgrouptocampdestination_id, webtourgroupfromcampdestination_id
                    ,webtourdefaulthomedestination,webtourdefaulthomedistance,webtourdefaulthomeduration
                    ,webtourusgroupidno
                    ,r.name as name
                    ,r.partner_id as partnerid
                    FROM event_registration r 
                    left outer join res_partner as regpartner on regpartner.id = r.partner_id
                    left outer join res_country as regpcountry on regpcountry.id = regpartner.country_id
                    left outer join campos_scout_org as scoutorg on scoutorg.id = regpartner.scoutorg_id
                    left outer join res_country as scoutorgcountry on scoutorgcountry.id = scoutorg.country_id
                    where r.event_id=1 and scoutgroup and r.id in (select distinct registration_id from campos_event_participant
                                                                   left outer join campos_webtourusneed as toneed on toneed.id = tocampusneed_id
                                                                   left outer join campos_webtourusneed as fromneed on fromneed.id = fromcampusneed_id
                                                                where (transport_to_camp or transport_from_camp) 
                        and (transport_to_camp or transport_from_camp or toneed.campos_demandneeded or fromneed.campos_demandneeded))
                    """
                    )
        
    @api.multi    
    def action_open_groupparticipants(self):
        self.ensure_one()
        
        view = self.env.ref('campos_final_registration.view_form_finalregistration_participant')
        treeview = self.env.ref('campos_final_registration.view_tree_finalregistration_participant')
        _logger.info('"OPEN PAR: %s %s', view, treeview)
        return {
                'name': ("Participants from %s" % self.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'views': [(treeview.id, 'tree'), (view.id, 'form')],
                'res_model': 'campos.event.participant',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('registration_id', '=', self.id)],
                'context': {
                            'default_registration_id': self.id,
                            'default_participant': True,
                            'default_parent_id': self.partnerid,
                            }
            }
        
    @api.multi    
    def action_open_registration(self):
        self.ensure_one()
        
        view = self.env.ref('campos_final_registration.view_form_finalregistration_gl')
        treeview = self.env.ref('campos_preregistration.view_tree_event_registration')
        _logger.info('"OPEN Reg: %s %s', view, treeview)
        return {
                'name': ("Registration from %s" % self.name),
                'view_mode': 'tree,form',
                'view_type': 'form',
                'views': [(treeview.id, 'tree'), (view.id, 'form')],
                'res_model': 'event.registration',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': [('id', '=', self.id)]
            }
