'''
Created on 14. jan. 2017

@author: jda.dk
'''
from openerp import models, fields, api
from xml.dom import minidom

import logging
_logger = logging.getLogger(__name__)

class webtourconfig(models.Model):
    _name = 'campos.webtourconfig'

    event_id = fields.Many2one('event.event', 'id')
    campdestinationid = fields.Many2one('campos.webtourusdestination', 'id',ondelete='set null')
    tocamp_campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','To Camp TripType', ondelete='set null')
    fromcamp_campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','From Camp TripType', ondelete='set null')
    webtoutexternalid_prefix = fields.Char('webtour ExternaiId prefix', default='0')
    
    @api.multi
    def action_webtour_check_usgroup(self):
        self.ensure_one()
        _logger.info("action_webtour_check_usgroup Here we go.....")
        registrationidlist=[]
        usgroupidlist=[]
        namelist=[]
        
        response_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/GetAll/'}).responce.encode('utf-8'))
        _logger.info("action_webtour_check_usgroup Got usGroup/GetAll/")
          
        webtourgroups = response_doc.getElementsByTagName("a:usGroup")

        for webtourgroup in webtourgroups:
            idno = webtourgroup.getElementsByTagName("a:IDno")[0].firstChild.data
            usgroupidlist.append(idno)
            aname = webtourgroup.getElementsByTagName("a:Name")[0].firstChild.data
            if aname in namelist:
                _logger.info("action_webtour_check_usgroup name doublet !!!!!!! %s %s",aname,idno)
            namelist.append(aname)
            
        _logger.info("action_webtour_check_usgroup Done check1 %s %s",len(namelist),len(usgroupidlist))
               
        for n in range(0, len(namelist)-1):
            #_logger.info("action_webtour_check_usgroup webtourusgroupidno name:%s usGr:%s",namelist[n],usgroupidlist[n])
            if (namelist[n][0:].isdigit()):
                for reg in self.env['event.registration'].search([('id', '=', namelist[n])]):
                    if reg.webtourusgroupidno != str(usgroupidlist[n]):
                        _logger.info("action_webtour_check_usgroup Wrong webtourusgroupidno !!! id:%s, db:%s wt:%s",reg.id,reg.webtourusgroupidno,usgroupidlist[n])
                        reg.webtourusgroupidno = usgroupidlist[n]
                if len(reg) < 1:
                    _logger.info("action_webtour_check_usgroup Not in Campos !!! usGroup: %s Name:%s",usgroupidlist[n],namelist[n])
            else:
                _logger.info("action_webtour_check_usgroup Not Int webtourusgroupidno !!!!!!! %s %s",namelist[n],usgroupidlist[n])    

        _logger.info("action_webtour_check_usgroup Done check2")        
        
        for reg in self.env['event.registration'].search([('webtourusgroupidno', 'in', usgroupidlist),('webtourusgroupidno', '!=', False)]):
            try:
                i = usgroupidlist.index(reg.webtourusgroupidno)
                if namelist[i] != str(reg.id):
                    _logger.info("action_webtour_check_usgroup Does not match  id:%s wt:%s Gr%s",reg.id,namelist[i],reg.webtourusgroupidno)
                    reg.webtourusgroupidno = False
      
            except:
                _logger.info("action_webtour_check_usgroup Did not find id:%s db:%s",reg.id,reg.webtourusgroupidno)
                
        for reg in self.env['event.registration'].search([('webtourusgroupidno', 'not in', usgroupidlist),('webtourusgroupidno', '!=', False)]):
            _logger.info("action_webtour_check_usgroup Not Int Webtour !!!!!!! %s %s %s",reg.id,reg.webtourusgroupidno, reg.name)  
        
        _logger.info("action_webtour_check_usgroup Done check3")
        
        for n in range(0, len(namelist)-1):
            if (namelist[n][0:].isdigit()):
                for reg in self.env['event.registration'].search([('id', '=', namelist[n]),('webtourusgroupidno', '=', False)]):
                    _logger.info("action_webtour_check_usgroup write new Gr id:%s Gr%s",reg.id,usgroupidlist[n])
                    reg.webtourusgroupidno = usgroupidlist[n]

        _logger.info("action_webtour_check_usgroup Done check4")
                
    @api.multi
    def action_webtour_check_ususer(self):
        self.ensure_one()

        _logger.info("action_webtour_check_ususer Her we go !!")
        
        ususer_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usUser/GetAll/'}).responce.encode('utf-8'))
        #usgroup_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/GetAll/'}).responce.encode('utf-8'))

        webtourusers = ususer_doc.getElementsByTagName("a:usUserMinimum")
        #webtourgroups = usgroup_doc.getElementsByTagName("a:usGroup")

        ususeridlist=[]
        ususergroupidnolist=[]
        ususerexternalidlist=[]        
        for webtouruser in webtourusers:
            ususeridlist.append(webtouruser.getElementsByTagName("a:IDno")[0].firstChild.data)
            ususergroupidnolist.append(webtouruser.getElementsByTagName("a:GroupIDno")[0].firstChild.data)
            ususerexternalidlist.append(webtouruser.getElementsByTagName("a:ExternalID")[0].firstChild.data)

        for reg in self.event_id.registration_ids:
            for par in reg.participant_ids:
                extid = self.webtoutexternalid_prefix+str(par.id)+par.webtour_externalid_suffix
                try:               
                    i= ususerexternalidlist.index(extid)
                except:
                    i=False
                    continue
                if i:
                    usg = ususergroupidnolist[i]
                    usu = ususeridlist[i]
                    if usu != par.webtourususeridno:
                        s = 'reg:{0} par:{1} Ext: {2} usUser does not match {3} {4}'.format(reg.id, par.id,extid,usu, par.webtourususeridno)
                        log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_ususer 1','result':s})         
                    elif usg != par.webtourusgroupidno:
                        s = 'reg:{0} par:{1} Ext: {2} usGroup does not match {3} {4}'.format(reg.id, par.id,extid,usg, par.webtourusgroupidno)
                        log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_ususer 2','result':s})
                    _logger.info("%s %s action_webtour_check_ususer",reg.id,par.id)  
                else:
                    if par.webtourusgroupidno != False or par.webtourususeridno != False:
                        s = 'reg:{0} par:{1} Ext: {2} Par not in found in WT {3} {4}'.format(reg.id, par.id,extid,par.webtourusgroupidno,par.webtourususeridno)
                        log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_ususer 3','result':s})                     
                    
                        
    @api.multi
    def action_webtour_check_usneed(self):
        self.ensure_one()
        _logger.info("action_webtour_check_usneed Her we go !!")
      
        usneed_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usNeed/GetAll/'}).responce.encode('utf-8'))
        webtourneeds = usneed_doc.getElementsByTagName("a:usNeedMinimum")

        usneedidlist=[]
        usneedgroupidnolist=[]
        ususeridnolist=[]    
        for webtourneed in webtourneeds:
            needno=webtourneed.getElementsByTagName("a:IDno")[0].firstChild.data
            groupno=webtourneed.getElementsByTagName("a:GroupIDno")[0].firstChild.data
            userno=webtourneed.getElementsByTagName("a:UserIDno")[0].firstChild.data
            usneedidlist.append(needno)
            usneedgroupidnolist.append(groupno)
            ususeridnolist.append(userno)
        
        osneedlist=[]  
        needs=self.env['campos.webtourusneed'].search([('webtour_needidno', '!=', False)])
        
        for need in needs:
            osneedlist.append(need.webtour_needidno)
            try:           
                i= usneedidlist.index(need.webtour_needidno)
            except:
                i=False
                continue
            
            if i:    
                usg = usneedgroupidnolist[i]
                usu = ususeridnolist[i]
                if need.webtour_groupidno != usg or need.webtour_useridno !=usu:
                    s = '{0} webtourusneed does not match Gr:{1} {2} U:{3} {4}'.format(need.id,need.webtour_needidno, need.webtour_groupidno,groupno, need.webtour_useridno,userno)
                    log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 1','result':s}) 
            else:
                s = '{0} webtourusneed not found in WT N:{1} G:{2} U:{3}'.format(need.id,need.webtour_needidno,need.webtour_groupidno,need.webtour_useridno)
                log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 2','result':s})                
        
        n= len(set(usneedidlist) - set(osneedlist))
        s = 'Number of webtour usNeed(s) not in Campos: {0}'.format(n)
        log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 3','result':s}) 
        
        #for n in list(set(usneedidlist) - set(osneedlist)):
        #    _logger.info("webtour usNeed not in Campos %s",n)
        
    @api.model
    def action_clearusecamptransportjobber_nocampdays(self):
 
        pars = self.env['campos.event.participant'].search([('staff', '=', True),('camp_day_ids', '=', False),'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        _logger.info("action_clearusecamptransportjobber_nocampdays %s",len(pars))
        n=100
        for par in pars:     
            par.clearusecamptransportjobber_nocampdays()
            
            if n > 0: n= n-1
            else: break

class WebtourConfigChecklog(models.Model):
    _description = 'Webtour check log'
    _name = 'campos.webtourconfig.checklog'
    name = fields.Char('Check', required=True)
    result = fields.Char('Result', required=True)                    
                   
class WebtourTripType(models.Model):
    _description = 'Webtour Trip Types'
    _name = 'campos.webtourconfig.triptype'
   
    name = fields.Char('Webtour Trip Type', required=True)
    traveldate_ids = fields.One2many('campos.webtourconfig.triptype.date','campos_TripType_id','Travel Days')
    returnjourney = fields.Boolean('Return Journey')


class WebtourTripTypeDate(models.Model):
    _description = 'Webtour Trip Types Date'
    _name = 'campos.webtourconfig.triptype.date'
    campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','Webtour_TripType', ondelete='set null')
    name = fields.Date('Date', required=True) 
    #date = fields.Date('Date', required=True)
    
class WebtourEvent(models.Model):
    _inherit = 'event.event'
    
    webtourconfig_id = fields.Many2one('campos.webtourconfig','Webtour Configuration')