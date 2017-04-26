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
    def action_webtour_get_create_usneed_tron(self):
        self.env['campos.webtourusneed'].get_create_usneed_tron()   
    

    @api.multi
    def action_webtour_getcreate_usgroup_ususer(self):
        self.env['campos.event.participant'].get_create_usgroupidno_tron()
        
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
        usgroup_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/GetAll/'}).responce.encode('utf-8'))

        webtourusers = ususer_doc.getElementsByTagName("a:usUserMinimum")
        webtourgroups = usgroup_doc.getElementsByTagName("a:usGroup")

        ususeridlist=[]
        ususergroupidnolist=[]
        ususerexternalidlist=[]        
        for webtouruser in webtourusers:
            ususeridlist.append(webtouruser.getElementsByTagName("a:IDno")[0].firstChild.data)
            ususergroupidnolist.append(webtouruser.getElementsByTagName("a:GroupIDno")[0].firstChild.data)
            ususerexternalidlist.append(webtouruser.getElementsByTagName("a:ExternalID")[0].firstChild.data)

        usgroupidlist=[]
        usgroupnamelist=[]
        for webtourgroup in webtourgroups:
            usgroupidlist.append(webtourgroup.getElementsByTagName("a:IDno")[0].firstChild.data)
            usgroupnamelist.append(webtourgroup.getElementsByTagName("a:Name")[0].firstChild.data)

        pars=self.env['campos.event.participant'].search([('webtourusgroupidno', 'in', usgroupidlist),('webtourususeridno', '!=', False)])
        _logger.info("action_webtour_check_ususer No rec %s",len(pars))
        for par in pars:
            try:               
                i=ususeridlist.index(par.webtourususeridno)
                #_logger.info("action_webtour_check_ususer %s, gr:%s, db:%s, wt:%s",i,par.id,par.webtourususeridno,ususeridlist[i])
                if ususergroupidnolist[i] != par.webtourusgroupidno:
                    _logger.info("action_webtour_check_ususer %s Not Matching Gr!!! webtour:%s, campos:%s, id:%s",par.webtourususeridno,ususergroupidnolist[i], par.webtourusgroupidno,par.id)
                else:
                    if ususeridlist[i] != par.webtourususeridno:
                        _logger.info("action_webtour_check_ususer Update gr:%s, db:%s, wt:%s",par.id,par.webtourususeridno,ususeridlist[i])
                    else:
                        _logger.info("action_webtour_check_ususer OK gr:%s, db:%s, wt:%s",par.id,par.webtourususeridno,ususeridlist[i])
            except:
                _logger.info("action_webtour_check_ususer not found id:%s, group:%s, ususer:%s",par.id,par.webtourusgroupidno,par.webtourususeridno)                      

    @api.multi
    def action_webtour_check_usneed(self):
        self.ensure_one()
        _logger.info("action_webtour_check_usneed Her we go !!")

        pars=self.env['campos.event.participant'].search([('webtourusgroupidno', '!=', False),('webtourususeridno', '!=', False)])
        #_logger.info("action_webtour_check_usneed Step 1 No of Pars %s",len(pars))
        for par in pars:
            if par.tocampusneed_id:
                updat = False
                if par.tocampusneed_id.webtour_groupidno != par.webtourusgroupidno: 
                    par.tocampusneed_id.webtour_groupidno = par.webtourusgroupidno
                    updat = True
                if par.tocampusneed_id.webtour_useridno != par.webtourususeridno:
                    par.tocampusneed_id.webtour_useridno = par.webtourususeridno
                    updat = True
                                
                if par.fromcampusneed_id:
                    if par.fromcampusneed_id.webtour_groupidno != par.webtourusgroupidno: 
                        par.fromcampusneed_id.webtour_groupidno = par.webtourusgroupidno
                        updat = True
                    if par.fromcampusneed_id.webtour_useridno != par.webtourususeridno:
                        par.fromcampusneed_id.webtour_useridno = par.webtourususeridno
                        updat = True
                        
                if updat:
                    _logger.info("action_webtour_check_usneed Update !! id:%s, group:%s, user:%s", par.tocampusneed_id,par.webtourusgroupidno,par.webtourususeridno)
 
        _logger.info("action_webtour_check_usneed Step 2 Start to read usNeed from Webtour")
        
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
            needs=self.env['campos.webtourusneed'].search([('webtour_groupidno', '=', groupno),('webtour_useridno', '=', userno),('webtour_needidno', '=', False)])
            
            if len(needs)>0:
                _logger.info("action_webtour_check_usneed found matching Needs gr:%s user:%s len:%s",groupno,userno,len(needs))
                needs[0].webtour_needidno=needno
            
        for n in range(0, len(usneedidlist)-1):
            #_logger.info("action_webtour_check_usgroup webtourusgroupidno name:%s usGr:%s",namelist[n],usgroupidlist[n])
            if (usneedidlist[n][0:].isdigit()):
                needs= self.env['campos.webtourusneed'].search([('webtour_needidno', '=', usneedidlist[n])])
                #_logger.info("action_webtour_check_usneed %s %s",usneedidlist[n], len(needs))
                for need in needs:
                    if need.webtour_needidno != str(usneedgroupidnolist[n]):
                        _logger.info("action_webtour_check_usneed webtourusgroupidno !! id:%s, par:%s, db:%s, wt:%s",need.id,need.participant_id ,need.webtour_groupidno,usneedgroupidnolist[n])
        
    @api.multi
    def action_clearusecamptransportjobber_nocampdays(self):
 
        pars = self.env['campos.event.participant'].search([('staff', '=', True),('camp_day_ids', '=', False),'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])
        _logger.info("action_clearusecamptransportjobber_nocampdays %s",len(pars))
        n=100
        for par in pars:     
            par.clearusecamptransportjobber_nocampdays()
            
            if n > 0: n= n-1
            else: break
                          
                   
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