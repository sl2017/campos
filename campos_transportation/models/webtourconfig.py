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
    webtourcorrecterrorpassword = fields.Char('webtour correct error password')
    
    @api.multi
    def action_webtour_check_usgroup(self):
        self.ensure_one()
        _logger.info("action_webtour_check_usgroup Here we go.....")
        usgroupidlist=[]
        namelist=[]
        
        response_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/GetAll/'}).responce.encode('utf-8'))               
        webtourgroups = response_doc.getElementsByTagName("a:usGroup")

        for webtourgroup in webtourgroups:
            idno = webtourgroup.getElementsByTagName("a:IDno")[0].firstChild.data
            usgroupidlist.append(idno)
            aname = webtourgroup.getElementsByTagName("a:Name")[0].firstChild.data
            namelist.append(aname)
            
        _logger.info("action_webtour_check_usgroup Done check1 %s %s",len(namelist),len(usgroupidlist))
        
        for reg in self.event_id.registration_ids:              
            try:               
                i= namelist.index(str(reg.id))
            except:
                i=False
                continue
            if i:
                if reg.webtourusgroupidno != usgroupidlist[i]:
                    s = 'reg:{0} usGroup does not match {1} {2}'.format(reg.id, usgroupidlist[i], reg.webtourusgroupidno)
                    log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usgroup 1','result':s})
                    if self.webtourcorrecterrorpassword == 'sl2017WebtourusGroup':
                        if usgroupidlist[i]:
                            reg.webtourusgroupidno = usgroupidlist[i]
                            s = 'reg:{0} Assigned webtourusgroupidno {1}'.format(reg.id,usgroupidlist[i] )
                            log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usgroup 1A','result':s})                     
            else:
                s = 'reg:{0} usGroup reg_id not found as name in WT'.format(reg.id)
                log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usgroup 2','result':s})  
                
                if reg.webtourusgroupidno:
                    try:               
                        ig= usgroupidlist.index(reg.webtourusgroupidno)
                    except:
                        ig=False
                        continue
                    if ig:
                        s = 'reg:{0} webtourusgroupidno:{1} found on another name in WT: {2}'.format(reg.id,reg.webtourusgroupidno,namelist[ig])
                        log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usgroup 3','result':s})                          
                   

    @api.multi
    def action_webtour_check_ususer(self):
        self.ensure_one()

        _logger.info("action_webtour_check_ususer Her we go !!")
        
        ususer_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usUser/GetAll/'}).responce.encode('utf-8'))
        webtourusers = ususer_doc.getElementsByTagName("a:usUserMinimum")

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
                        
                        if self.webtourcorrecterrorpassword == 'sl2017WebtourusUser':
                            if par.webtourusgroupidno and usg:
                                par.webtour_externalid_suffix='A'
                                s = 'reg:{0} par:{1} Assigned webtour_externalid_suffix {2}'.format(reg.id, par.id,par.webtour_externalid_suffix)
                                log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_ususer 2A','result':s})
                            elif par.webtourusgroupidno == False and usg:
                                par.webtourusgroupidno = usg
                                s = 'reg:{0} par:{1} Assigned webtourusgroupidno {2}'.format(reg.id, par.id,usg)
                                log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_ususer 2B','result':s})                        
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
                    
                    if self.webtourcorrecterrorpassword == 'sl2017WebtourusNeed':
                        s = 'need:{0} {1} par:{2} reg:[3} webtour_useridno and groupidno update U:{4} {5} G:{6} {7}'.format(need.id,need.webtour_needidno,need.participant_id,need.registration_id,need.webtour_useridno,usu,need.webtour_groupidno,usg)
                        
                        dicto = {}
                        if usg and need.webtour_groupidno != usg:
                            dicto['webtour_groupidno'] = usg
                        if  usu and need.webtour_useridno != usu:
                            dicto['webtour_useridno'] = usu
                        
                        if dicto:
                            need.write(dicto)
                            log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 1A','result':s})
                        else:
                            log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 1AA','result':s})
                    else:
                        s = 'need:{0} {1} par:{2} reg:[3} webtour_useridno and groupidno does not match U:{4} {5} G:{6} {7}'.format(need.id,need.webtour_needidno,need.participant_id,need.registration_id,need.webtour_useridno,usu,need.webtour_groupidno,usg)
                        log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 1','result':s})                                     
            else:
                s = '{0} webtourusneed not found in WT N:{1} G:{2} U:{3}'.format(need.id,need.webtour_needidno,need.webtour_groupidno,need.webtour_useridno)
                log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 2','result':s})                
        
        n= len(set(usneedidlist) - set(osneedlist))
        s = 'Number of webtour usNeed(s) not in Campos: {0}'.format(n)
        log = self.env['campos.webtourconfig.checklog'].create({'name':'action_webtour_check_usneed 3','result':s}) 
        
                
    @api.model
    def action_clearusecamptransportjobber_nocampdays(self):
 
        pars = self.env['campos.event.participant'].search([('staff', '=', True),('camp_day_ids', '=', False),'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        _logger.info("action_clearusecamptransportjobber_nocampdays %s",len(pars))
        n=100
        for par in pars:     
            par.clearusecamptransportjobber_nocampdays()
            
            if n > 0: n= n-1
            else: break
            
            
    @api.multi
    def action_Webtour_usneedminimum_get(self):
        self.ensure_one() 
        _logger.info("action_Webtour_usneedminimum_get here we go!!")
        mo = self.env['campos.webtour.usneedminimum']
        n=mo.search_count([])
        while n > 0:
            mo.search([], limit = 10000).unlink()
            n=mo.search_count([])
            _logger.info("action_Webtour_usneedminimum_get deleted records, Still %s records to do",n)

        mo.getfromwebtour()   

    @api.multi
    def action_Webtour_ususerminimum_get(self):
        self.ensure_one() 
        _logger.info("action_Webtour_ususerminimum_get here we go!!")
        mo = self.env['campos.webtour.ususerminimum']
        n=mo.search_count([])
        while n > 0:
            mo.search([], limit = 10000).unlink()
            n=mo.search_count([])
            _logger.info("action_Webtour_ususerminimum_get deleted records, Still %s records to do",n)

        mo.getfromwebtour()  

    @api.multi
    def action_Webtour_usgroup_get(self):
        self.ensure_one() 
        _logger.info("action_Webtour_usgroup_get here we go!!")
        mo = self.env['campos.webtour.usgroup']
        n=mo.search_count([])
        while n > 0:
            mo.search([], limit = 1000).unlink()
            n=mo.search_count([])
            _logger.info("action_Webtour_usgroup_get deleted records, Still %s records to do",n)
  
        mo.getfromwebtour()  


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