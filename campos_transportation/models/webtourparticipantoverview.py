'''
Created on 15. apr. 2017

@author: jda.dk
'''
from openerp import models, fields, api, tools

import logging

_logger = logging.getLogger(__name__)

       
class WebtourParticipantOverview(models.Model):
    _name = 'campos.webtourparticipantoverview'
    _auto = False
    _log_access = False
    
    registration_id = fields.Many2one('event.registration','Registration ID', readonly=True)
    participant_id = fields.Many2one('campos.event.participant','Participant ID', readonly=True)
    partner_id = fields.Many2one('res.partner','Participant Partner ID', readonly=True)
    regpartner_id = fields.Many2one('res.partner','Registration Partner ID', readonly=True)
    state = fields.Char('participant state', readonly=True)
    regstate = fields.Char('registration state', readonly=True)
    scoutgroup = fields.Boolean('scoutgroup', readonly=True)    
    countrycode = fields.Char('country code', readonly=True)
    scoutorgcountrycode = fields.Char('scout org country code', readonly=True)
    donotparticipate = fields.Boolean('do not participate', readonly=True)
    workas_jobber = fields.Boolean('workas jobber', readonly=True)
    workas_planner = fields.Boolean('work as planner', readonly=True)
    transport_to_camp = fields.Boolean('transport to camp', readonly=True)
    transport_from_camp = fields.Boolean('transport from camp', readonly=True)
    tocampdate = fields.Date(string='To Camp Date', readonly=True)
    fromcampdate = fields.Date(string='From Camp Date', readonly=True)
    tocampusneed_id = fields.Many2one('campos.webtourusneed','To Camp Need ID', readonly=True)
    fromcampusneed_id = fields.Many2one('campos.webtourusneed','From Camp Need ID', readonly=True)
    tocamptravelgroup = fields.Char('to camp travelgroup', readonly=True)
    fromcamptravelgroup = fields.Char('from camp travelgroup', readonly=True)
    group_entrypoint = fields.Many2one('event.registration.entryexitpoint','Point of entry into Denmark', readonly=True)
    group_exitpoint = fields.Many2one('event.registration.entryexitpoint','Point of exit from Denmark', readonly=True)
    webtourdefaulthomedestination = fields.Many2one('campos.webtourusdestination','default home destination', readonly=True)
    webtourdefaulthomedistance = fields.Float('Webtour Pickup Map Distance', readonly=True)
    webtourdefaulthomeduration = fields.Char('Webtour Pickup Map Duration', readonly=True)
    tocamp_TripType_id = fields.Many2one('campos.webtourconfig.triptype','To Camp TripType', readonly=True)
    fromcamp_TripType_id = fields.Many2one('campos.webtourconfig.triptype','From Camp TripType', readonly=True)
    webtourususeridno = fields.Char('webtour us User ID no', readonly=True)
    webtourusgroupidno = fields.Char(string='webtour us Group ID no', readonly=True) 
    toneeded = fields.Boolean('to camp needed', readonly=True)
    fromneeded = fields.Boolean('from camp needed', readonly=True)
    towebtour_deleted = fields.Boolean('webtour to camp deleted', readonly=True)
    fromwebtour_deleted = fields.Boolean('webtour from camp deleted', readonly=True)   
  
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourparticipantoverview as
                    SELECT p.id,registration_id,p.id as participant_id
                    ,p.partner_id,regpartner.id as regpartner_id
                    ,p.state,r.state as regstate,regpartner.scoutgroup,donotparticipate,workas_jobber,workas_planner
                    ,transport_to_camp, transport_from_camp
                    ,regpcountry.code as countrycode
                    ,scoutorgcountry.code as scoutorgcountrycode                                       
                    ,tocampdate,fromcampdate
                    ,tocampusneed_id,fromcampusneed_id
                    ,tocampfromdestination_id, fromcamptodestination_id
                    ,tocamptravelgroup,fromcamptravelgroup
                    ,group_entrypoint,group_exitpoint
                    ,webtourdefaulthomedestination,webtourdefaulthomedistance,webtourdefaulthomeduration
                    ,webtourusgroupidno, webtourususeridno
                    ,toneed.campos_demandneeded as toneeded,fromneed.campos_demandneeded as fromneeded
                    ,toneed.webtour_deleted as towebtour_deleted,fromneed.webtour_deleted as fromwebtour_deleted                    
                    FROM campos_event_participant p
                    left outer join event_registration r on r.id = registration_id
                    left outer join event_registration_entryexitpoint as entry on entry.id = group_entrypoint
                    left outer join event_registration_entryexitpoint as exit on exit.id = group_exitpoint
                    left outer join campos_webtourusneed as toneed on toneed.id = tocampusneed_id
                    left outer join campos_webtourusneed as fromneed on fromneed.id = fromcampusneed_id
                    left outer join res_partner as regpartner on regpartner.id = r.partner_id
                    left outer join res_country as regpcountry on regpcountry.id = regpartner.country_id
                    left outer join campos_scout_org as scoutorg on scoutorg.id = regpartner.scoutorg_id
                    left outer join res_country as scoutorgcountry on scoutorgcountry.id = scoutorg.country_id
                    where p.state != 'deregistered' and (transport_to_camp or transport_from_camp or toneed.campos_demandneeded or fromneed.campos_demandneeded) and  r.event_id=1  
                    """
                    )

