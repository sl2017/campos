# -*- coding: utf-8 -*-
from openerp import models, fields, api, tools
#from ..interface import webtourinterface
from xml.dom import minidom
import xml.etree.ElementTree as ET

import logging

_logger = logging.getLogger(__name__)

from openerp.addons.connector.queue.job import job, related_action
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector.exception import FailedJobError


def related_action_generic(session, job):
            model = job.args[0]
            res_id = job.args[1]
            model_obj = session.env['ir.model'].search([('model', '=', model)])
            action = {
                'name': model_obj.name,
                'type': 'ir.actions.act_window',
                'res_model': model,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': res_id,
            }
            return action

@job(default_channel='root.webtour')
@related_action(action=related_action_generic)
def do_delayed_get_create_webtour_need_job(session, model, rec_id):
    rec = session.env['campos.webtourusneed'].browse(rec_id)
    if rec.exists():
        rec.get_create_webtour_need()
        
    
class WebtourUsNeed(models.Model):
    _name = 'campos.webtourusneed'
    _description = 'Campos Webtour usneed'
    participant_id = fields.Many2one('campos.event.participant','Participant ID', ondelete='set null')
    registration_id = fields.Many2one('event.registration','Registration ID', ondelete='set null', related="participant_id.registration_id")
    travelgroup = fields.Char('Travel Group', default='1')
    campos_deleted = fields.Boolean('CampOs Deleted', default=False)
    
    campos_demandneeded = fields.Boolean('CampOs Demand Needed', default=False)
    campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','Webtour_TripType', ondelete='set null')
    campos_triptype_returnjourney = fields.Boolean('Return journey', related='campos_TripType_id.returnjourney')
    campos_traveldate = fields.Char('CampOs StartDateTime', required=False)
    campos_startdestinationidno = fields.Char('CampOs StartDestinationIdNo', required=False)
    campos_enddestinationidno = fields.Char('CampOs EndDestinationIdNo', required=False)
    travelneed_id= fields.Many2one('event.registration.travelneed','Travel need',ondelete='set null')
    travelneed_deadline = fields.Selection([    ('Select', 'Please Select'),
                                     ('00:00', '00:00'),
                                     ('01:00', '01:00'),
                                     ('02:00', '02:00'),
                                     ('03:00', '03:00'),
                                     ('04:00', '04:00'),
                                     ('05:00', '05:00'),                                    
                                     ('06:00', '06:00'),
                                     ('07:00', '07:00'),
                                     ('08:00', '08:00'),
                                     ('09:00', '09:00'),                                     
                                     ('10:00', '10:00'),                                     
                                     ('11:00', '11:00'),
                                     ('12:00', '12:00'),
                                     ('13:00', '13:00'),
                                     ('14:00', '14:00'),
                                     ('15:00', '15:00'),                                    
                                     ('16:00', '16:00'),
                                     ('17:00', '17:00'),
                                     ('18:00', '18:00'),
                                     ('19:00', '19:00'),                                     
                                     ('20:00', '20:00'),                                     
                                     ('21:00', '21:00'),
                                     ('22:00', '22:00'),
                                     ('23:00', '23:00')                                                                         
                                     ], default='Select', string='Time', related='travelneed_id.deadline') 
    travelneed_travelconnectiondetails = fields.Char(related='travelneed_id.travelconnectiondetails')
        
    campos_transfered_demandneeded = fields.Boolean('Transfered Demand Needed', default=False)
    campos_transfered_deadline = fields.Selection([    ('Select', 'Please Select'),
                                     ('00:00', '00:00'),
                                     ('01:00', '01:00'),
                                     ('02:00', '02:00'),
                                     ('03:00', '03:00'),
                                     ('04:00', '04:00'),
                                     ('05:00', '05:00'),                                    
                                     ('06:00', '06:00'),
                                     ('07:00', '07:00'),
                                     ('08:00', '08:00'),
                                     ('09:00', '09:00'),                                     
                                     ('10:00', '10:00'),                                     
                                     ('11:00', '11:00'),
                                     ('12:00', '12:00'),
                                     ('13:00', '13:00'),
                                     ('14:00', '14:00'),
                                     ('15:00', '15:00'),                                    
                                     ('16:00', '16:00'),
                                     ('17:00', '17:00'),
                                     ('18:00', '18:00'),
                                     ('19:00', '19:00'),                                     
                                     ('20:00', '20:00'),                                     
                                     ('21:00', '21:00'),
                                     ('22:00', '22:00'),
                                     ('23:00', '23:00')                                                                         
                                     ], default='Select', string='Time')
    campos_transfered_travelconnectiondetails = fields.Char('Transfered connection details', required=False)
    campos_transfered_traveldate = fields.Char('Transfered Travel Date', required=False)

    campos_transfered_startdatetime = fields.Char('Transfered StartDateTime', required=False)
    campos_transfered_enddatetime = fields.Char('Transfered EndDateTime', required=False)
    campos_transfered_startdestinationidno = fields.Char('Transfered StartDestinationIdNo', required=False)
    campos_transfered_enddestinationidno = fields.Char('Transfered EndDestinationIdNo', required=False)
    campos_transfered_startnote = fields.Char('Transfered StartNote', required=False)
    campos_transfered_endnote = fields.Char('Transfered EndNote', required=False)
    
    campos_writeseq = fields.Char('CampOs Last Write Seq.', required=False)
    campos_transferedseq = fields.Char('CampOs Last transfered Seq.', required=False)
    
    campos_transfered = fields.Boolean(string='campos transfered',compute='_computediff', readonly=True, store=True)
    webtour_transfererror = fields.Char('Webtour transfer Error.', required=False)
    
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

    webtour_pending_startdatetime = fields.Char('Webtour Pending StartDateTime', required=False)
    webtour_pending_startdestinationidno = fields.Char('Webtour Pending StartDestinationIdNo', required=False)
    webtour_pending_startnote = fields.Char('Webtour Pending StartNote', required=False)
    webtour_pending_enddatetime = fields.Char('Webtour Pending EndDateTime', required=False)
    webtour_pending_enddestinationidno = fields.Char('Webtour Pending EndDestinationIdNo', required=False)
    webtour_pending_endnote = fields.Char('Webtour Pending EndNote', required=False)
    webtour_pending_pendingtype = fields.Char('Webtour Pending PendingType', required=False)
    
    webtour_rejected_startdatetime = fields.Char('Webtour rejected StartDateTime', required=False)
    webtour_rejected_startdestinationidno = fields.Char('Webtour rejected StartDestinationIdNo', required=False)
    webtour_rejected_startnote = fields.Char('Webtour rejected StartNote', required=False)
    webtour_rejected_enddatetime = fields.Char('Webtour rejected EndDateTime', required=False)
    webtour_rejected_enddestinationidno = fields.Char('Webtour rejected EndDestinationIdNo', required=False)
    webtour_rejected_endnote = fields.Char('Webtour rejected EndNote', required=False)
    webtour_rejected_rejecttype = fields.Char('Webtour rejected RejectType', required=False)
    webtour_rejected_rejectdatetime = fields.Char('Webtour rejected RejectDateTime', required=False)
    
    webtour_CurrentDateTime = fields.Char('CurrentDateTime', required=False)
    webtour_touridno = fields.Char('Webtour TourIDno', required=False)

    WebtourUsNeedChanges_ids= fields.One2many('campos.webtourusneed.changes','WebtourUsNeed_id',ondelete='set null')
    webtourstatus = fields.Selection([('1', 'Pending Create'),
                                      ('2', 'No Pending Change'),
                                      ('3', 'Pending Change'),
                                      ('4', 'Pending Delete'),
                                      ('5', 'Deleted'),
                                      ('6', 'Not Accepted'),
                                      ('7', 'Not Deleted')], default=False, string='Webtour Status')  
     
    needstatus = fields.Selection([('0', 'No Demand'),
                                   ('1', 'OK'),
                                   ('2', 'In Planning'),
                                   ('3', 'Pending Change'),
                                   ('4', 'NOT AS DESIRED'),
                                   ('5', 'CANNOT BE CANCELED'),
                                   ('6', 'NO SEAT RESERVED'),
                                   ('9', 'Error')], default=False, string='Need Status')

    needproblem = fields.Char('Need Problem')
    extra_registration_id = fields.Many2one('event.registration','Registration ID', ondelete='set null')
    extra_traveldate_id = fields.Many2one('campos.webtourconfig.triptype.date', 'Travel Date', domain="[('campos_TripType_id','=',campos_TripType_id)]", ondelete='set null') 
    extra_destination_id = fields.Many2one('campos.webtourusdestination','Destination ID', ondelete='set null')
    extra_passengername = fields.Char('Passenger name')
    extra_participant_id = fields.Many2one('campos.event.participant','Linked Participant', ondelete='set null') #, domain = "[('registration_id','=',extra_registration_id)]"
    
    @api.multi
    @api.depends('webtour_CurrentDateTime','campos_demandneeded','campos_TripType_id','campos_traveldate','campos_startdestinationidno','campos_enddestinationidno','travelneed_id','travelneed_deadline','travelneed_travelconnectiondetails') 
    def _computeneedstatus(self):
                       
            needstatus = False
            if rec.campos_demandneeded == False:
                if rec.webtour_deleted == True or rec.webtour_needidno == False or same(need.webtourstatus,'5') or same(need.webtourstatus,'6'):
                    needstatus = '0'
                elif rec.webtour_rejected_rejecttype == 'DELETE':
                    needstatus = '5'
                else:
                    needstatus = '3'                    
            elif rec.webtour_transfererror:
                    needstatus = '9'
            else: #There is a Need 
                if ((rec.campos_demandneeded != rec.campos_transfered_demandneeded)
                    or (rec.travelneed_deadline != rec.campos_transfered_deadline)
                    or (rec.travelneed_travelconnectiondetails != rec.campos_transfered_travelconnectiondetails)
                    or (rec.campos_traveldate != rec.campos_transfered_traveldate)
                    or (rec.campos_startdestinationidno != rec.campos_transfered_startdestinationidno)
                    or (rec.campos_enddestinationidno != rec.campos_transfered_enddestinationidno)       
                    ): # check for changes in travel data
                    needstatus = '3'
                else:
                    if rec.webtourstatus in ('1','3','4','5'):        
                        needstatus = '3'
                    elif rec.webtourstatus == '2':
                        if (rec.webtour_rejected_rejecttype == 'DELETE') and problem:
                            needstatus = '5'
                        elif (rec.webtour_rejected_rejecttype == 'UPDATE') and problem:
                            needstatus = '4'
                        elif (rec.webtour_rejected_rejecttype == 'CREATE') and problem:
                            needstatus = '6'
                        elif rec.webtour_touridno == False or rec.webtour_touridno == '0':
                            needstatus = '2'
                        else:
                            needstatus = '1'
                    else:
                        needstatus = False #STRANGE !!!
                                               
            rec.needstatus = needstatus   
    
                            
    @api.multi
    def write(self, vals):
        _logger.info("WebtourUsNeed Write Entered %s", vals.keys())
        ret = super(WebtourUsNeed, self).write(vals)
        
        def same(a,b):
            if a == False:
                a=''
            if b == False:
                b=''
            return a == b
        
        def addseplist(list,t):
            if t:
                if list:
                    return list +', ' + t
                else:
                    return t
            else:
                return list  
    
        for need in self:
            
            if ('extra_traveldate_id' in vals
                or 'extra_destination_id' in vals
                or 'campos_TripType_id' in vals
                or 'extra_participant_id' in vals):
                dicto = {}
                
                if need.extra_traveldate_id:
                    if need.campos_traveldate != need.extra_traveldate_id.name : dicto['campos_traveldate'] = need.extra_traveldate_id.name
                
                if need.extra_registration_id:
                    webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', need.extra_registration_id.event_id.id)])
                    campdestination = webtourconfig.campdestinationid.destinationidno
                    
                    if need.campos_TripType_id:
                        if need.campos_TripType_id.returnjourney:
                            if need.campos_startdestinationidno != campdestination: dicto['campos_startdestinationidno'] = campdestination
                            if need.campos_enddestinationidno != need.extra_destination_id.destinationidno: dicto['campos_enddestinationidno'] = need.extra_destination_id.destinationidno
                        else:
                            if need.campos_startdestinationidno != need.extra_destination_id.destinationidno: dicto['campos_startdestinationidno'] = need.extra_destination_id.destinationidno
                            if need.campos_enddestinationidno != campdestination: dicto['campos_enddestinationidno'] = campdestination

                if need.extra_participant_id:                            
                    if need.participant_id.id != need.extra_participant_id.id: dicto['participant_id'] = need.extra_participant_id.id
                
                if len(dicto) > 0:
                    need.write(dicto)
            
            if  ('campos_TripType_id' in vals 
                or 'travelgroup' in vals
                or 'campos_traveldate' in vals
                or 'campos_startdestinationidno' in vals
                or 'campos_enddestinationidno' in vals 
                ):
                #_logger.info("WebtourUsNeed Write Change %s %s", need.campos_traveldate,fields.Date.from_string(need.campos_startdatetime))
                need.calc_travelneed_id()

            problem = False
            if need.campos_demandneeded == (need.webtour_deleted or same(need.webtourstatus,'5') or same(need.webtourstatus,'6') or (need.webtour_needidno == False)):
                    problem = 'Demand'
            elif need.campos_demandneeded:
                if not same(need.campos_startdestinationidno,need.webtour_startdestinationidno):
                    problem = 'Start Dest'
                if not same(need.campos_enddestinationidno, need.webtour_enddestinationidno):
                    problem = addseplist(problem,'End Dest')
                    
                #compose note (for non Danish groups)
                note = False
                if need.travelneed_id.deadline and (need.travelneed_id.deadline != 'Select'):
                    note = 'Deadline: ' + need.travelneed_id.deadline
                  
                if need.travelneed_id.travelconnectiondetails:
                    if note:
                        note = note + ', Connection: ' + need.travelneed_id.travelconnectiondetails 
                    else:
                        note = 'Connection: ' + need.travelneed_id.travelconnectiondetails 
                
                if note == False:
                    note =''
                elif note: # Limit to 80 Chars
                    note = note[:80]
                                      
                if need.campos_triptype_returnjourney:
                    if not same('',need.webtour_startnote) or not same(note,need.webtour_endnote):
                        problem = addseplist(problem,'Details')      
                    
                else:                    
                    if not same(note,need.webtour_startnote) or not same('',need.webtour_endnote):
                        problem = addseplist(problem,'Details')                        
                    
                s=need.webtour_startdatetime
                if s == False: s = ''
                if not same(need.campos_traveldate,s[:10]):
                    problem = addseplist(problem,'Date') 
            
            if need.needproblem != problem: 
                need.needproblem = problem 

            ''' need.webtourstatus:
                '1', 'Pending Create'
                '2', 'No Pending Change'
                '3', 'Pending Change'
                '4', 'Pending Delete'
                '5', 'Deleted'
                '6', 'Not Accepted'
                '7', 'Not Deleted'
            '''  

            ''' need.needstatus:
                '0', 'No Demand'
                '1', 'OK'
                '2', 'In Planning'
                '3', 'Pending Change'
                '4', 'NOT AS DESIRED'
                '5', 'CANNOT BE CANCELED'
                '6', 'NO SEAT RESERVED'
                '9', 'Error'
            '''
            needstatus = False
            if need.campos_demandneeded == False:
                if need.webtour_deleted == True or need.webtour_needidno == False or same(need.webtourstatus,'5') or same(need.webtourstatus,'6'):
                    needstatus = '0'
                elif same(need.webtourstatus,'7'):
                    needstatus = '5'
                else:
                    needstatus = '3'                    
            elif need.webtour_transfererror:
                    needstatus = '9'
            else: #There is a Need
                if need.webtourstatus in ('1','3','4'):        
                    needstatus = '3'
                elif same(need.webtourstatus,'6'):
                    needstatus = '6'
                elif need.needproblem:
                    needstatus = '4'
                elif need.webtour_touridno == False or same(need.webtour_touridno,'0'):
                    needstatus = '2'
                else:
                    needstatus = '1'
                                               
            if need.needstatus != needstatus:
                need.needstatus = needstatus

        return ret
    
    @api.model
    def create(self, vals):
        _logger.info("WebtourUsNeed Create Entered %s", vals.keys())
        rec = super(WebtourUsNeed, self).create(vals)
        
        if rec.extra_traveldate_id:
            rec.campos_traveldate=rec.extra_traveldate_id.name
        
        if rec.extra_registration_id:         
            webtourconfig= rec.env['campos.webtourconfig'].search([('event_id', '=', rec.extra_registration_id.event_id.id)])
            campdestination = webtourconfig.campdestinationid.destinationidno
            
            if rec.campos_TripType_id and rec.extra_destination_id:
                
                if rec.campos_TripType_id.returnjourney:
                    rec.campos_startdestinationidno = campdestination
                    rec.campos_enddestinationidno =  rec.extra_destination_id.destinationidno
                else:
                    rec.campos_startdestinationidno = rec.extra_destination_id.destinationidno
                    rec.campos_enddestinationidno  = campdestination
                    
        if rec.extra_participant_id: 
            rec.participant_id = rec.extra_participant_id.id        
        
        rec.calc_travelneed_id()       
        return rec
    
    @api.one
    def calc_travelneed_id(self):
        # find travelneed matching usneeds
        rs_travelneed= self.env['event.registration.travelneed'].search([('registration_id', '=', self.participant_id.registration_id.id),('travelgroup', '=', self.travelgroup),('campos_TripType_id', '=', self.campos_TripType_id.id)
                                                                        ,('startdestinationidno.id', '=', self.campos_startdestinationidno),('enddestinationidno.id', '=', self.campos_enddestinationidno),('traveldate', '=', self.campos_traveldate)])
    
        if self.campos_TripType_id.id and self.campos_startdestinationidno and self.campos_enddestinationidno:
            _logger.info("%s calc_travelneed_id Entered %s %s %s %s %s %s %s",self.id, self.travelneed_id.traveldate , len(rs_travelneed),self.participant_id.registration_id.id,self.campos_TripType_id.id,self.campos_startdestinationidno,self.campos_enddestinationidno,self.campos_traveldate)
            if rs_travelneed:
                if (self.travelneed_id == False) or (self.travelneed_id != rs_travelneed[0]): 
                    self.travelneed_id=rs_travelneed[0]     
            else:
                dicto0 = {}
                dicto0["registration_id"] = self.participant_id.registration_id.id
                dicto0["travelgroup"] =self.travelgroup
                dicto0["name"] = 'Bus Trip'   
                dicto0["campos_TripType_id"] = self.campos_TripType_id.id
                dicto0["startdestinationidno"] = self.campos_startdestinationidno
                dicto0["enddestinationidno"] = self.campos_enddestinationidno
                dicto0["traveldate"] = fields.Date.from_string(self.campos_traveldate)
                dicto0["deadline"] ='Select'
                _logger.info("%s calc_travelneed_id Create %s",self.id,dicto0)
                self.travelneed_id = self.env['event.registration.travelneed'].create(dicto0)     
        else:
            _logger.info("%s calc_travelneed_id Entered with insufficent data %s %s %s %s %s %s %s",self.id,self.travelneed_id.traveldate , len(rs_travelneed),self.participant_id.registration_id.id,self.campos_TripType_id.id,self.campos_startdestinationidno,self.campos_enddestinationidno,fields.Date.from_string(self.campos_traveldate))
            
    @api.multi
    @api.depends('campos_writeseq','campos_transferedseq') 
    def _computediff(self):
        for record in self: 
            record.campos_transfered = record.campos_writeseq == record.campos_transferedseq
    
    @api.one
    def get_create_webtour_need(self):   
        ns = {'i': 'http://schemas.datacontract.org/2004/07/webTourManager',
              'a': 'http://schemas.datacontract.org/2004/07/webTourManager.Classes'}
        
        def get_tag_data_from_node(node,nodetag):
            if node is None:
                return False
            else:
                tag = node.findall(nodetag,ns)                            
                if tag is not None:
                    try:
                        t = tag[0].text
                    except:
                        t = False
                        pass
                    if t is None : t = False                    
                    return t
                else:
                    return False
        
        def getidno(root):
            try:
                content = root.find("i:Content",ns) #Let's find the contenr Section
            except:
                content = False
            try:    
                pending = content.find("a:Pending",ns) #Let's see if there is a Pending Section
            except:
                pending = False
            try:    
                rejected = content.find("a:Rejected",ns) #Let's see if there is a Rejected Section
            except:
                rejected = False
            
            idno = get_tag_data_from_node(content,"a:IDno")
            if (idno is False):
                idno = get_tag_data_from_node(pending,"a:IDno")
                if (idno is False):
                    idno = get_tag_data_from_node(rejected,"a:IDno")
            return idno

                                     
        def updatewebtourfields17(root):         
            content = root.find("i:Content",ns) #Let's find the contenr Section
            pending = content.find("a:Pending",ns) #Let's see if there is a Pending Section
            rejected = content.find("a:Rejected",ns) #Let's see if there is a Rejected Section
            
            dicto ={}
            
            idno = getidno(root)
            if self.webtour_needidno != idno: dicto['webtour_needidno'] = idno
            
            pendingtype = get_tag_data_from_node(pending,"a:PendingType")
            rejecttype = get_tag_data_from_node(rejected,"a:RejectType")

            ''' '1', 'Pending Create'
                '2', 'No Pending Change'
                '3', 'Pending Change'
                '4', 'Pending Delete'
                '5', 'Deleted'
                '6', 'Not Accepted'
                '7', 'Not Deleted'
            '''                       
            if get_tag_data_from_node(content,"a:Deleted") =='true':
                if self.webtour_deleted != True : dicto['webtour_deleted'] = True
                if self.webtourstatus != '5': dicto['webtourstatus'] = '5'              
            else:
                if self.webtour_deleted != False : dicto['webtour_deleted'] = False
            
                if (pendingtype == False):
                    if (rejecttype == 'CREATE') and self.campos_demandneeded == True:
                        if self.webtourstatus != '6': dicto['webtourstatus'] = '6' 
                    elif (rejecttype == 'DELETE') and self.campos_demandneeded == False:
                        if self.webtourstatus != '7': dicto['webtourstatus'] = '7'
                    else:    
                        if self.webtourstatus != '2': dicto['webtourstatus'] = '2'
                else:
                    if pendingtype == 'CREATE':
                        if self.webtourstatus != '1': dicto['webtourstatus'] = '1'
                    elif pendingtype == 'UPDATE':
                        if self.webtourstatus != '3': dicto['webtourstatus'] = '3'
                    elif pendingtype == 'DELETE':
                        if self.webtourstatus != '4': dicto['webtourstatus'] = '4'
                    else: dicto['webtourstatus']  = False      
            
            if pending is not None:
                if self.webtour_pending_pendingtype != pendingtype: 
                    dicto['webtour_pending_pendingtype'] = pendingtype               
                if self.webtour_pending_startdatetime            != get_tag_data_from_node(pending,"a:StartDateTime"):
                    dicto['webtour_pending_startdatetime']        = get_tag_data_from_node(pending,"a:StartDateTime")                    
                if self.webtour_pending_startdestinationidno     != get_tag_data_from_node(pending,"a:StartDestinationIDno"):
                    dicto['webtour_pending_startdestinationidno'] = get_tag_data_from_node(pending,"a:StartDestinationIDno")
                if self.webtour_pending_startnote                != get_tag_data_from_node(pending,"a:StartNote"):
                    dicto['webtour_pending_startnote']            = get_tag_data_from_node(pending,"a:StartNote")
                if self.webtour_pending_enddatetime              != get_tag_data_from_node(pending,"a:EndDateTime"):
                    dicto['webtour_pending_enddatetime']          = get_tag_data_from_node(pending,"a:EndDateTime")
                if self.webtour_pending_enddestinationidno       != get_tag_data_from_node(pending,"a:EndDestinationIDno"):
                    dicto['webtour_pending_enddestinationidno']   = get_tag_data_from_node(pending,"a:EndDestinationIDno")
                if self.webtour_pending_endnote                  != get_tag_data_from_node(pending,"a:EndNote"): 
                    dicto['webtour_pending_endnote']              = get_tag_data_from_node(pending,"a:EndNote")
                if self.webtour_CurrentDateTime                  != get_tag_data_from_node(pending,"CurrentDateTime"): 
                    dicto['webtour_CurrentDateTime']              = get_tag_data_from_node(pending,"CurrentDateTime")                    
            else:
                if self.webtour_pending_pendingtype: dicto['webtour_pending_pendingtype'] = False               
                if self.webtour_pending_startdatetime: dicto['webtour_pending_startdatetime'] = False
                if self.webtour_pending_startdestinationidno: dicto['webtour_pending_startdestinationidno'] = False
                if self.webtour_pending_startnote :dicto['webtour_pending_startnote'] = False
                if self.webtour_pending_enddatetime:dicto['webtour_pending_enddatetime'] = False
                if self.webtour_pending_enddestinationidno :dicto['webtour_pending_enddestinationidno'] = False
                if self.webtour_pending_endnote: dicto['webtour_pending_endnote'] = False

            if rejected is not None:
                if self.webtour_rejected_rejecttype               != get_tag_data_from_node(rejected,"a:RejectType"): 
                    dicto['webtour_rejected_rejecttype']           = get_tag_data_from_node(rejected,"a:RejectType")               
                if self.webtour_rejected_startdatetime            != get_tag_data_from_node(rejected,"a:StartDateTime"):
                    dicto['webtour_rejected_startdatetime']        = get_tag_data_from_node(rejected,"a:StartDateTime")                    
                if self.webtour_rejected_startdestinationidno     != get_tag_data_from_node(rejected,"a:StartDestinationIDno"):
                    dicto['webtour_rejected_startdestinationidno'] = get_tag_data_from_node(rejected,"a:StartDestinationIDno")
                if self.webtour_rejected_startnote                != get_tag_data_from_node(rejected,"a:StartNote"):
                    dicto['webtour_rejected_startnote']            = get_tag_data_from_node(rejected,"a:StartNote")
                if self.webtour_rejected_enddatetime              != get_tag_data_from_node(rejected,"a:EndDateTime"):
                    dicto['webtour_rejected_enddatetime']          = get_tag_data_from_node(rejected,"a:EndDateTime")
                if self.webtour_rejected_enddestinationidno       != get_tag_data_from_node(rejected,"a:EndDestinationIDno"):
                    dicto['webtour_rejected_enddestinationidno']   = get_tag_data_from_node(rejected,"a:EndDestinationIDno")
                if self.webtour_rejected_endnote                  != get_tag_data_from_node(rejected,"a:EndNote"): 
                    dicto['webtour_rejected_endnote']              = get_tag_data_from_node(rejected,"a:EndNote")
                if self.webtour_rejected_rejectdatetime           != get_tag_data_from_node(rejected,"a:RejectDateTime"): 
                    dicto['webtour_rejected_rejectdatetime']       = get_tag_data_from_node(rejected,"a:RejectDateTime")                    
            else:
                if self.webtour_rejected_rejecttype:            dicto['webtour_rejected_rejecttype'] = False
                if self.webtour_rejected_rejectdatetime:        dicto['webtour_rejected_rejectdatetime'] = False                 
                if self.webtour_rejected_startdatetime:         dicto['webtour_rejected_startdatetime'] = False
                if self.webtour_rejected_startdestinationidno:  dicto['webtour_rejected_startdestinationidno'] = False
                if self.webtour_rejected_startnote:             dicto['webtour_rejected_startnote'] = False
                if self.webtour_rejected_enddatetime:           dicto['webtour_rejected_enddatetime'] = False
                if self.webtour_rejected_enddestinationidno:    dicto['webtour_rejected_enddestinationidno'] = False
                if self.webtour_rejected_endnote:               dicto['webtour_rejected_endnote'] = False

            if self.webtour_startdatetime           != get_tag_data_from_node(content,"a:StartDateTime"):        dicto['webtour_startdatetime'] =        get_tag_data_from_node(content,"a:StartDateTime")
            if self.webtour_startdestinationidno    != get_tag_data_from_node(content,"a:StartDestinationIDno"): dicto['webtour_startdestinationidno'] = get_tag_data_from_node(content,"a:StartDestinationIDno")
            if self.webtour_startnote               != get_tag_data_from_node(content,"a:StartNote"):            dicto['webtour_startnote'] =            get_tag_data_from_node(content,"a:StartNote")
            if self.webtour_enddatetime             != get_tag_data_from_node(content,"a:EndDateTime"):          dicto['webtour_enddatetime'] =          get_tag_data_from_node(content,"a:EndDateTime")
            if self.webtour_enddestinationidno      != get_tag_data_from_node(content,"a:EndDestinationIDno"):   dicto['webtour_enddestinationidno'] =   get_tag_data_from_node(content,"a:EndDestinationIDno")
            if self.webtour_endnote                 != get_tag_data_from_node(content,"a:EndNote"):              dicto['webtour_endnote'] =              get_tag_data_from_node(content,"a:EndNote")
            if self.webtour_touridno                != get_tag_data_from_node(content,"a:TourIDno"):             dicto['webtour_touridno'] =             get_tag_data_from_node(content,"a:TourIDno")
            if self.campos_transferedseq != self.campos_writeseq: dicto['campos_transferedseq'] = self.campos_writeseq

            dicto['webtour_CurrentDateTime'] = get_tag_data_from_node(root,"i:CurrentDateTime")
            
            if len(dicto) > 0:
                self.write(dicto)

        def webtour_updatereq(request):
            root = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/Update/?' + request}).responce.encode('utf-8'))
            content = root.find("i:Content",ns) #Let's find the contet Section                                 
            if get_tag_data_from_node(content,"a:Deleted") =='true': ## Cant use that usNeed any more
                #compose note (for non Danish groups)
                note = False
                if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                    note = 'Deadline: ' + self.travelneed_id.deadline
                  
                if self.travelneed_id.travelconnectiondetails:
                    if note:
                        note = note + ', Connection: ' + self.travelneed_id.travelconnectiondetails 
                    else:
                        note = 'Connection: ' + self.travelneed_id.travelconnectiondetails 
                
                if note: # Limit to 80 Chars
                    note = note[:80]
                                 
                if self.travelneed_id.campos_TripType_id.returnjourney: #Return jurney
                    startnote = False
                    endnote = note
                    if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                        enddatetime = self.campos_traveldate+"T"+self.travelneed_id.deadline
                    else:
                        enddatetime = self.campos_traveldate
                    startdatetime = self.campos_traveldate
                else: 
                    startnote = note
                    endnote = False
                    if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                        startdatetime = self.campos_traveldate+"T"+self.travelneed_id.deadline
                    else:
                        startdatetime = self.campos_traveldate
                    enddatetime = self.campos_traveldate  
                    
                if startnote == False:
                    startnote=""
                if endnote == False:
                    endnote=""
                
                request="UserIDno=" + self.webtour_useridno
                request=request+"&GroupIDno="+self.webtour_groupidno
                request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                request=request+"&StartDateTime="+startdatetime
                request=request+"&EndDateTime="+enddatetime                       
                request=request+"&StartNote="+startnote
                request=request+"&EndNote="+endnote                                      
                root = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/Create/?' + request}).responce.encode('utf-8'))
                idno = getidno(root) #Let us check response
                _logger.info("%s 20. webtour_updatereq new need created Old: %s New:%s Req:%s",self.id,self.webtour_needidno,idno,request)
                
            return root    
                
        _logger.info("Here we go !!!!!!!!!!! %s %s %s", self.webtour_useridno, self.webtour_groupidno, self.webtour_needidno)
        transfererror = False
        needtransfered = False
        dic = {};
        
        if (self.webtour_groupidno == False or self.webtour_useridno == False) and self.webtour_needidno : # Let us try to recover the missing info
            _logger.info("%s get_create_usneed_tron: Try to recover missing ref's N: %s G:%s U:%s", self.id, self.webtour_needidno, self.webtour_groupidno,self.webtour_useridno)
            root1 = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/GetByIDno/?IDno=' + self.webtour_needidno}).responce.encode('utf-8'))             
            idno = getidno(root1) #Let us check response
            try:
                content1 = root1.find("i:Content",ns) #Let's find the contenr Section
            except:
                content1 = False
            
            group1=get_tag_data_from_node(content1,'a:GroupIDno')
            user1=get_tag_data_from_node(content1,'a:UserIDno')
            
            if group1 and user1:              
                if self.webtour_groupidno != group1: dic['webtour_groupidno'] = group1
                if self.webtour_useridno != user1: dic['webtour_useridno'] = user1
                _logger.info("%s get_create_usneed_tron: Updated group and user from need  %s G:%s %s U:%s %s", self.id, self.webtour_needidno, self.webtour_groupidno,group1,self.webtour_useridno, user1)
        
        newgroup = self.webtour_groupidno
        if (newgroup == False) or (newgroup == "0"): 
            newgroup = minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/GetByName/?Name='+str(self.registration_id.id)}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data 
            
            if (newgroup <> "0") and newgroup:
                dic['webtour_groupidno'] = newgroup
                _logger.info("%s %s get_create_usneed_tron: Recovered usGroup by name:%s G:%s", self.id, self.webtour_needidno, self.registration_id.id,newgroup)
            else: #Try to Create group
                newgroup = minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/Create/?Name=' + str(self.registration_id.id)}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data 
           
                if (newgroup <> "0") and newgroup:
                    _logger.info("%s %s get_create_usneed_tron: Created usGroup by name:%s G:%s", self.id, self.webtour_needidno,self.registration_id.id,newgroup)
                    self.registration_id.webtourusgroupidno = newgroup
                    dic['webtour_groupidno'] = newgroup
                else:
                    _logger.info("%s %s get_create_usneed_tron: Coud not created usGroup by name:%s ", self.id, self.webtour_needidno,self.registration_id.id)
    
        if (newgroup <> "0") and newgroup and (self.webtour_useridno == False):
            webtoutexternalid_prefix = self.registration_id.event_id.webtourconfig_id.webtoutexternalid_prefix
            extid = webtoutexternalid_prefix+str(self.participant_id.id)+self.participant_id.webtour_externalid_suffix
            if self.extra_destination_id  or self.extra_participant_id or self.extra_passengername or self.extra_registration_id or self.extra_traveldate_id:
                extid = extid + str(self.id)
        
            newidno = minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usUser/Get/ExternalID/?ExternalID='+extid}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data 
            if (newidno != "0") and newidno:
                _logger.info("%s %s get_create_usneed_tron: Recoved usUser P:%s G:%s E:%s U:%s", self.id, self.webtour_needidno,self.participant_id.id,newgroup,extid,newidno) 
                dic['webtour_useridno'] = newidno 
            else:    
                req="usUser/Create/WithGroupIDno/?FirstName=" + str(self.participant_id.id) + "&LastName=" + str(self.registration_id.id) + "&ExternalID=" + extid + "&GroupIDno=" + newgroup
                newidno=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':req}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data            
                  
                if (newidno != "0") and newidno:
                    _logger.info("%s %s get_create_usneed_tron: Created usUser P:%s G:%s E:%s U:%s", self.id, self.webtour_needidno,self.participant_id.id,newgroup,extid,newidno) 
                    dic['webtour_useridno'] = newidno 
                    
                else:
                    _logger.info("%s %s get_create_usneed_tron: Coud not created usUser P:%s G:%s E:%s", self.id, self.webtour_needidno,self.participant_id.id,newgroup,extid)  
                        
        if len(dic) > 0:    
            self.write(dic)
            return True                
                
        if  ((self.webtour_groupidno == False) or (self.webtour_useridno == False)
              or (((self.campos_startdestinationidno == False) or (self.campos_traveldate == False) or (self.campos_enddestinationidno == False)) and (self.campos_demandneeded == True))):
            _logger.info("%s get_create_usneed_tron: Info missing %s %s %s %s %s", self.id, self.webtour_useridno,self.webtour_groupidno,self.campos_traveldate,self.campos_startdestinationidno,self.campos_enddestinationidno)
            transfererror = 'Info missing'
            if self.webtour_transfererror != transfererror : self.webtour_transfererror = transfererror
            return True

        # check for changes in travel data
        if ((self.campos_demandneeded != self.campos_transfered_demandneeded)
            or (self.campos_demandneeded and self.webtour_needidno == False)
            or (self.campos_demandneeded == False and self.webtour_deleted == False and self.webtour_pending_pendingtype !="DELETE" and self.webtour_rejected_rejecttype !="DELETE")
            or (self.travelneed_deadline != self.campos_transfered_deadline)
            or (self.travelneed_travelconnectiondetails != self.campos_transfered_travelconnectiondetails)
            or (self.campos_traveldate != self.campos_transfered_traveldate)
            or (self.campos_startdestinationidno != self.campos_transfered_startdestinationidno)
            or (self.campos_enddestinationidno != self.campos_transfered_enddestinationidno)    
            ):
            _logger.info("%s 1A. Change in travel data",self.id)       
                 
            #compose note (for non Danish groups)
            note = False
            if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                note = 'Deadline: ' + self.travelneed_id.deadline
              
            if self.travelneed_id.travelconnectiondetails:
                if note:
                    note = note + ', Connection: ' + self.travelneed_id.travelconnectiondetails 
                else:
                    note = 'Connection: ' + self.travelneed_id.travelconnectiondetails 
            
            if note: # Limit to 80 Chars
                note = note[:80]            
                         
            if self.travelneed_id.campos_TripType_id.returnjourney: #Return jurney
                startnote = False
                endnote = note
                if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                    enddatetime = self.campos_traveldate+"T"+self.travelneed_id.deadline
                else:
                    enddatetime = self.campos_traveldate
                startdatetime = self.campos_traveldate
            else: 
                startnote = note
                endnote = False
                if self.travelneed_id.deadline and (self.travelneed_id.deadline != 'Select'):
                    startdatetime = self.campos_traveldate+"T"+self.travelneed_id.deadline
                else:
                    startdatetime = self.campos_traveldate
                enddatetime = self.campos_traveldate                
            
            if (self.campos_demandneeded == True): # there is demand
                _logger.info("%s 2A. demand needed",self.id)
                
                recreate = False
                if (self.webtour_needidno != False and self.webtour_needidno != "0" and self.webtour_rejected_rejecttype =='CREATE'): #We can reuse a rejected Need
                    _logger.info("%s 2AA. We cant reuse a rejected Usneed",self.id,self.webtour_needidno)
                    recreate= True
                
                if (self.webtour_needidno == False or self.webtour_needidno == "0" or recreate): #no need known, so try to create
                    _logger.info("%s 3. No need - Try to create",self.id)
                    request="UserIDno=" + self.webtour_useridno
                    request=request+"&GroupIDno="+self.webtour_groupidno
                    request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                    request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                    request=request+"&StartDateTime="+startdatetime
                    request=request+"&EndDateTime="+enddatetime
                    if startnote == False:
                        startnote=""
                    if endnote == False:
                        endnote=""
                           
                    request=request+"&StartNote="+startnote
                    request=request+"&EndNote="+endnote                        
                    
                    _logger.info("%s 3a. request %s",self.id,request)
                    responceroot = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/Create/?' + request}).responce.encode('utf-8'))
                    
                    idno = getidno(responceroot) #Let us check response
                                       
                    if (idno <> "0") and idno:
                        _logger.info("%s 4a. New usNeed Created",self.id)
                        updatewebtourfields17(responceroot)
                        needtransfered = True
                    else: 
                        _logger.info("%s 4b.usNeed NOT created",self.id)
                        transfererror = 'Could not Create';
                        
                else: # There is a Need to try to update
                         
                    request = ''
                    
                    if ((self.travelneed_deadline != self.campos_transfered_deadline)
                        or (self.travelneed_travelconnectiondetails != self.campos_transfered_travelconnectiondetails) or self.webtour_deleted or self.webtour_pending_pendingtype =="DELETE"):
                        if startnote == False: 
                            request=request+"&StartNote="
                        else:
                            request=request+"&StartNote="+startnote
                        
                        if endnote == False:
                            request=request+"&EndNote="
                        else:    
                            request=request+"&EndNote="+endnote
                        
                        request=request+"&StartDateTime="+startdatetime
                        request=request+"&EndDateTime="+enddatetime      
                    else:        
                        if (self.campos_traveldate != self.campos_transfered_traveldate or self.webtour_deleted or self.webtour_pending_pendingtype =="DELETE"):
                            request=request+"&StartDateTime="+startdatetime
                            request=request+"&EndDateTime="+enddatetime                        
                        
                    if (self.campos_startdestinationidno != self.campos_transfered_startdestinationidno or self.webtour_deleted or self.webtour_pending_pendingtype =="DELETE"):
                        request=request+"&StartDestinationIDno="+self.campos_startdestinationidno
                           
                    if (self.campos_enddestinationidno != self.campos_transfered_enddestinationidno or self.webtour_deleted or self.webtour_pending_pendingtype =="DELETE"):
                        request=request+"&EndDestinationIDno="+self.campos_enddestinationidno                          

                    if request == '':
                        request="&StartDestinationIDno="+self.campos_startdestinationidno
                        request=request+"&EndDestinationIDno="+self.campos_enddestinationidno
                        request=request+"&StartDateTime="+startdatetime
                        request=request+"&EndDateTime="+enddatetime
                        if startnote == False:
                            startnote=""
                        if endnote == False:
                               endnote=""
                        request=request+"&StartNote="+startnote
                        request=request+"&EndNote="+endnote   
                    
                    request="NeedIDno="+self.webtour_needidno + request
                    
                    responceroot = webtour_updatereq(request)
                    # ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/Update/?' + request}).responce.encode('utf-8'))
                    idno = getidno(responceroot) #Let us check response
                    
                    if idno <> "0": # Stil OK?
                        _logger.info("%s 9A. Need updated with the Request %s",self.id, request)
                        updatewebtourfields17(responceroot)
                        needtransfered = True
                    else:
                        _logger.info("%s 9B. Problem with the Request %s",self.id, request)
                        transfererror = 'Cound not Update';
                        self.webtour_needidno=False
                                                                                        
            else: #No demand now        
                _logger.info("%s 2B. No demand needed",self.id)
                if not self.webtour_deleted:
                    _logger.info("%s 10. Deleting usNeed %s",self.id, self.webtour_needidno)
                    if self.webtour_needidno and (self.webtour_needidno <> '0'):
                        _logger.info("%s 11. There is usNeedID No - Try to delete",self.id)
                        responceroot = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/Delete/?NeedIDno=' + self.webtour_needidno}).responce.encode('utf-8'))
                        idno = getidno(responceroot) #Let us check response
                        if idno <> "0": # Stil OK?
                            updatewebtourfields17(responceroot)
                            needtransfered = True
                            _logger.info("%s 12A. Deleted",self.id)
                        else:
                            transfererror = 'Could not Delete';                       
                            _logger.info("%s 12B. Dit not Get usNeed Delete responce",self.id)                        
        else: 
            _logger.info("%s 1B. No changes in travel data",self.id)
            if self.webtour_needidno and self.webtour_needidno <> '0':
                _logger.info("%s 13. There is usNeed IDno",self.id)

                responceroot = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/GetByIDno/?IDno=' + self.webtour_needidno}).responce.encode('utf-8'))             
                idno = getidno(responceroot) #Let us check response
                
                if idno <> "0":
                    _logger.info("%s 14A. Got usNeed reponce",self.id)
                    updatewebtourfields17(responceroot)
                else:
                    transfererror = 'Could not Get';                     
                    _logger.info("%s 14B. Dit not Get usNeed reponce !!!!!!!!!!!!!!!!!!!!! %s",self.id,self.webtour_needidno)

        dicto ={}
        if transfererror != self.webtour_transfererror:
            dicto['webtour_transfererror'] = transfererror

        if (needtransfered): ## usNeed has been updated :-)
            if self.campos_transfered_demandneeded != self.campos_demandneeded: dicto['campos_transfered_demandneeded']  = self.campos_demandneeded
            if self.campos_transfered_deadline != self.travelneed_deadline: dicto['campos_transfered_deadline']  = self.travelneed_deadline
            if self.campos_transfered_travelconnectiondetails != self.travelneed_travelconnectiondetails: dicto['campos_transfered_travelconnectiondetails']  = self.travelneed_travelconnectiondetails
            if self.campos_transfered_traveldate != self.campos_traveldate:dicto['campos_transfered_traveldate']  = self.campos_traveldate
            if self.campos_transfered_startdatetime != startdatetime: dicto['campos_transfered_startdatetime']  = startdatetime
            if self.campos_transfered_enddatetime != enddatetime : dicto['campos_transfered_enddatetime']  = enddatetime
            if self.campos_transfered_startdestinationidno != self.campos_startdestinationidno: dicto['campos_transfered_startdestinationidno']  = self.campos_startdestinationidno
            if self.campos_transfered_enddestinationidno != self.campos_enddestinationidno: dicto['campos_transfered_enddestinationidno']  = self.campos_enddestinationidno
            if self.campos_transfered_startnote != startnote: dicto['campos_transfered_startnote']  = startnote
            if self.campos_transfered_endnote != endnote: dicto['campos_transfered_endnote']  = endnote

        if len(dicto) > 0:
            self.write(dicto)
                                     
        self.env.cr.commit()                                                                
        return True
    
    @api.model
    def get_create_usneed_tron(self):
        MAX_LOOPS_usNeed = 100  #Max No of Needs pr Scheduled call
        
        # find usneeds not beeing transfered
        rs_needs= self.env['campos.webtourusneed'].search([('campos_transfered', '=', False),('campos_demandneeded', '=', True)])

        _logger.info("get_create_usneed_tron: Here we go... %i usNeeds to update in Webtour", len(rs_needs))
        
        loops=0
        for need in rs_needs:
            
            if  need.webtour_groupidno == False or need.webtour_useridno == False or need.campos_startdestinationidno == False or need.campos_traveldate == False or need.campos_enddestinationidno == False:
                _logger.info("get_create_usneed_tron: Info missing %s %s %s %s %s", need.webtour_useridno,need.webtour_groupidno,need.campos_startdestinationidno,need.campos_traveldate,need.campos_enddestinationidno)
            else:
                need.get_create_webtour_need()
                loops = loops + 1
            
            if loops > MAX_LOOPS_usNeed:
                break
    
    @api.multi
    def action_do_delayed_get_create_webtour_need_job(self):
        for rec in self:
            session = ConnectorSession.from_env(self.env)
            do_delayed_get_create_webtour_need_job.delay(session, 'campos.webtourusneed', rec.id)    

    @api.multi
    def action_do_delayed_get_create_webtour_need_job_changedsence(self,event_id):
        ns = {'i': 'http://schemas.datacontract.org/2004/07/webTourManager',
              'a': 'http://schemas.datacontract.org/2004/07/webTourManager.Classes'}
        webtourconfig= self.env['campos.webtourconfig'].search([('event_id', '=', event_id)])
        _logger.info("action_do_delayed_get_create_webtour_need_job_changedsence %s %s",event_id,webtourconfig.webtourusneedchangessince)  
        
        root = ET.fromstring(self.env['campos.webtour_req_logger'].create({'name':'usNeed/GetByLastUpdated/?LastUpdated=' + webtourconfig.webtourusneedchangessince}).responce.encode('utf-8'))
        content = root.find("i:Content",ns) #Let's find the contet Section         
        if content is not None:
            array = content.find("i:Array",ns) 
            if array is not None:
                curentdaytime = root.find("i:CurrentDateTime",ns).text
                for usneed in array.findall('a:usNeedMinimum',ns):
                    tag = usneed.findall('a:IDno',ns)                            
                    if tag is not None:
                        try:
                            idno = tag[0].text
                        except:
                            idno = False    
                        
                        if idno:
                            needs=self.env['campos.webtourusneed'].search([('webtour_needidno', '=',idno)])
                    
                            for need in needs:
                                session = ConnectorSession.from_env(self.env)
                                do_delayed_get_create_webtour_need_job.delay(session, 'campos.webtourusneed', need.id)
                
                webtourconfig.webtourusneedchangessince = curentdaytime[:16]
                         
    
class WebtourNeedOverview(models.Model):
    _name = 'campos.webtourusneed.overview'
    _description = 'Campos Webtour usneed Overview'
    _auto = False
    _log_access = False

    registration_id = fields.Many2one('event.registration','Registration ID')
    travelgroup = fields.Char('Travel Group')
    webtour_groupidno = fields.Char('Webtour us Group ID no')
    campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','Webtour Trip Type')    
    campos_transfered_startdatetime = fields.Char('CampOs StartDateTime')
    campos_startdestinationidno = fields.Char('CampOs Start Destination IdNo')
    campos_enddestinationidno = fields.Char('CampOs End Destination IdNo')    
    pax = fields.Integer('CampOS PAX')
        
    excessdemand = fields.Integer('Excess demand in WEBTour')
    nottransfered = fields.Integer('Needs Not transfered to WEBTour')
    notdeleted = fields.Integer('Needs Not Deleted in WEBTour')
    startdestdiffer = fields.Integer('Needs where start destination differ')    
    enddestdiffer = fields.Integer('Needs where end destination differ')   
    startdatetimediffer = fields.Integer('Needs where startdatetime differ')
    enddatetimediffer = fields.Integer('Needs where end datetime differ')
    startnotediffer = fields.Integer('Needs where start note differ')    
    endnotediffer = fields.Integer('Needs where end note differ')
     
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_overview as
                    SELECT case when travelneed_id is not null then travelneed_id else -min(campos_webtourusneed.id) end as id, campos_event_participant.registration_id as registration_id,travelgroup,webtour_groupidno, "campos_TripType_id",campos_transfered_startdatetime::timestamp,campos_startdestinationidno,campos_enddestinationidno
                    , count(campos_webtourusneed.id) as pax
                    , sum(case when campos_demandneeded then 0 else 1 end) as excessdemand 
                    , sum(case when campos_transfered then 0 else 1 end) as nottransfered
                    , sum(case when campos_deleted and not webtour_deleted then 1 else 0 end) as notdeleted
                    , sum(case when webtour_startdestinationidno = campos_startdestinationidno then 0 else 1 end) as startdestdiffer
                    , sum(case when webtour_enddestinationidno = campos_enddestinationidno then 0 else 1 end) as enddestdiffer
                    , sum(case when campos_transfered_startdatetime::timestamp = webtour_startdatetime::timestamp then 0 else 1 end) as startdatetimediffer
                    , sum(case when campos_transfered_enddatetime::timestamp = webtour_enddatetime::timestamp then 0 else 1 end) as enddatetimediffer
                    , sum(case when (case when campos_transfered_startnote isnull then '' else campos_transfered_startnote end) = (case when webtour_startnote isnull then '' else webtour_startnote end) then 0 else 1 end) as startnotediffer
                    , sum(case when (case when campos_transfered_endnote isnull then '' else campos_transfered_endnote end) = (case when webtour_endnote isnull then '' else webtour_endnote end) then 0 else 1 end) as endnotediffer
                    FROM campos_webtourusneed
                    left outer join campos_event_participant on campos_event_participant.id = participant_id
                    where campos_demandneeded or( not webtour_deleted and webtour_needidno::INT4>0)
                    group by travelneed_id, travelgroup            
                    ,campos_event_participant.registration_id,webtour_groupidno,"campos_TripType_id",campos_transfered_startdatetime::timestamp
                    ,campos_startdestinationidno
                    ,campos_enddestinationidno
                    """
                    )

class WebtourUsNeedTravelNeedPax(models.Model):
    _name = 'campos.webtourusneed.travelneedpax'
    _description = 'Campos Webtour usneed Travelneed pax'
    _auto = False
    _log_access = False
  
    pax = fields.Integer('TravelNeed PAX')

    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_travelneedpax as
                    SELECT  travelneed_id as id
                    , count(id) as pax
                    FROM campos_webtourusneed
                    where campos_demandneeded
                    group by travelneed_id          
                    """
                    )
 
class WebtourUsNeedTravelNeedPaxDay(models.Model):
    _name = 'campos.webtourusneed.travelneedpax.day'
    _description = 'Campos Webtour usneed Travelneed pax pr day'
    _auto = False
    _log_access = False
    
    registration_id  = fields.Many2one('event.registration', 'Registration', ondelete='set null')
    traveldate = fields.Date('Date', required=True) 
    fromcamp = fields.Boolean('From Camp', required=True)  
    pax = fields.Integer('TravelNeed PAX')

    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_travelneedpax_day as
                    SELECT  min(n.id) as id
                    ,registration_id
                    ,campos_traveldate as traveldate
                    ,tt.returnjourney as fromcamp
                    , count(n.id) as pax
                    FROM campos_webtourusneed n
                    inner join campos_event_participant on campos_event_participant.id = participant_id
                    inner join campos_webtourconfig_triptype tt on tt.id = "campos_TripType_id"
                    where campos_demandneeded
                    group by registration_id,campos_traveldate,tt.returnjourney      
                    """
                    )
 
    
class WebtourUsNeedTicketsSent(models.Model):
    _name = 'campos.webtourusneed.tickets.sent'
    _description = 'campos webtour usNeed Tickets Sent'
  
    ticket_id = fields.Integer('Tickets Id')
    sentdatetime = fields.Datetime('sent datetime')
    registration_id = fields.Many2one('event.registration','Registration ID')
    touridno = fields.Char('Tour IDno')
    startdatetime = fields.Char('Start Date Time')
    enddatetime = fields.Char('End Date Time')  
    busterminaldate = fields.Char('Busterminal Date')
    busterminaltime = fields.Char('Busterminal Time') 
    direction = fields.Char('Direction')
    stop = fields.Char('Stop')
    address = fields.Char('Address')
    seats_confirmed = fields.Integer('Seats confirmed')
    seats_pending = fields.Integer('Seats pending')
    seats_not_confirmed = fields.Integer('Seats not confirmed')

        
class WebtourUsNeedTickets(models.Model):
    _description = 'campos webtour usNeed Tickets'
    _name = 'campos.webtourusneed.tickets'
    _auto = False
    _log_access = False
  
    registration_id = fields.Many2one('event.registration','Registration ID')
    touridno = fields.Char('Tour IDno')
    startdatetime = fields.Char('Start Date Time')
    enddatetime = fields.Char('End Date Time')  
    busterminaldate = fields.Char('Busterminal Date')
    busterminaltime = fields.Char('Busterminal Time') 
    direction = fields.Char('Direction')
    stop = fields.Char('Stop')
    address = fields.Char('Address')
    seats_confirmed = fields.Integer('Seats confirmed')
    seats_pending = fields.Integer('Seats pending')
    seats_not_confirmed = fields.Integer('Seats not confirmed')
    create_date = fields.Datetime('Create_date')
    create_uid = fields.One2many('res.users','id')
    write_date = fields.Datetime('write_date')
    write_uid = fields.One2many('res.users','id')
    write_uid = fields.One2many('res.users','id')
    sameaslastmail = fields.Boolean('Same as last mail')
    lastmaildatetime = fields.Datetime('last mail datetime')
    lastmailtxt = fields.Char('last mail')
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_tickets as      
                    select t.*, ((COALESCE(t.startdatetime,'-') = COALESCE(s.startdatetime,'-')) and 
                    (COALESCE(t.enddatetime,'-') = COALESCE(s.enddatetime,'-')) and 
                    (COALESCE('' || t.touridno,'-2') = COALESCE('' || s.touridno,'-2')) and
                    (COALESCE(t.direction,'-') = COALESCE(s.direction,'-')) and
                    (COALESCE(t.stop,'-') = COALESCE(s.stop,'-')) and 
                    (replace(replace(replace(trim(COALESCE(t.address,'-')),' '||chr(10),''),chr(10),''),chr(13),'')= replace(replace(replace(trim(COALESCE(s.address,'-')),' '||chr(10),''),chr(10),''),chr(13),''))) as sameaslastmail,
                    s.sentdatetime as lastmaildatetime,
                    COALESCE(s.direction,'-') || ', '  || COALESCE(s.startdatetime,'-') || ', ' || COALESCE(s.enddatetime,'-') || ', ' || COALESCE(s.stop,'-') || ', ' || COALESCE('' || s.seats_confirmed,'-') || ', ' || COALESCE('' || s.seats_pending,'-')  || ', ' || COALESCE('' || s.seats_not_confirmed,'-') || ', ' || COALESCE('' || s.touridno,'-') || ', ' || COALESCE(s.address,'-') as lastmailtxt from (            
                    select min(n.id) as id 
                    ,p.registration_id
                    ,n.webtour_touridno as touridno
                    ,left(replace(webtour_startdatetime,'T',' '),16) as startdatetime
                    ,left(replace(webtour_enddatetime,'T',' '),16)  as enddatetime
                    ,left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,10) as busterminaldate
                    ,right(left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,14),3) || right('0'|| right(left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,16),2)::int/15*15,2) as busterminaltime            
                    ,tt.name as direction
                    ,d.name as Stop
                    ,replace(d.address,E'\nDK','') as address
                    ,sum(case when needstatus in ('1','5') then 1 else 0 end) as seats_confirmed
                    ,sum(case when needstatus in ('2','3','4') then 1 else 0 end) as seats_pending
                    ,sum(case when needstatus in ('6','7') then 1 else 0 end) as seats_not_confirmed
                    ,min(n.create_date) as create_date 
                    ,min(n.create_uid) as  create_uid
                    ,max(n.write_date) as write_date
                    ,min(n.write_uid) as write_uid
                    from campos_webtourusneed  n 
                    inner join campos_webtourconfig_triptype tt on tt.id = "campos_TripType_id"
                    left outer join campos_webtourusdestination d on d.destinationidno = case when returnjourney then campos_enddestinationidno else campos_startdestinationidno end 
                    inner join campos_event_participant p on p.id = n.participant_id 
                    inner join event_registration r on r.id = p.registration_id
                    where needstatus <> '0' 
                    group by p.registration_id,r.name,webtour_touridno,tt.name,returnjourney,webtour_startdatetime, webtour_enddatetime,d.name,d.address,tt.returnjourney 
                    order by 2,case when returnjourney then 2 else 1 end ,5   ) t 
                    left outer join (select ts.ticket_id, max(ts.id) as lastid from campos_webtourusneed_tickets_sent ts group by ts.ticket_id) lastsent on lastsent.ticket_id = t.id
                    left outer join campos_webtourusneed_tickets_sent as s on s.id  = lastsent.lastid
                    """
                    )        

class WebtourUsNeedTicketsOverview(models.Model):
    _name = 'campos.webtourusneed.tickets.overview'
    _description = 'campos webtour usNeed Tickets overview'
    _auto = False
    _log_access = False

    ticketscnt =  fields.Integer('Tickets Cnt')
    ticketsentcnt = fields.Integer('Tickets sent Cnt')
    sameaslastmail = fields.Integer('Same as last mail')
    create_date = fields.Datetime('Create_date')
    create_uid = fields.One2many('res.users','id')
    write_date = fields.Datetime('write_date')
    write_uid = fields.One2many('res.users','id')  
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_tickets_overview as      
                    select registration_id as id
                        ,count(registration_id) as ticketscnt
                        ,sum( case when lastmaildatetime is not null then 1 else 0 end)  as ticketsentcnt
                        ,min(case when sameaslastmail then 1 else 0 end) as sameaslastmail 
                        ,min(create_date) as create_date 
                        ,min(create_uid) as  create_uid
                        ,max(write_date) as write_date
                        ,min(write_uid) as write_uid
                    from (                    
                    select t.*, ((COALESCE(t.startdatetime,'-') = COALESCE(s.startdatetime,'-')) and 
                        (COALESCE(t.enddatetime,'-') = COALESCE(s.enddatetime,'-')) and 
                        (COALESCE('' || t.touridno,'-2') = COALESCE('' || s.touridno,'-2')) and
                        (COALESCE(t.direction,'-') = COALESCE(s.direction,'-')) and
                        (COALESCE(t.seats_confirmed,0) = COALESCE(s.seats_confirmed,0)) and 
                        (COALESCE(t.seats_pending,0) = COALESCE(s.seats_pending,0)) and 
                        (COALESCE(t.seats_not_confirmed,0) = COALESCE(s.seats_not_confirmed,0)) and 
                        (COALESCE(t.stop,'-') = COALESCE(s.stop,'-')) and 
                        (replace(replace(replace(trim(COALESCE(t.address,'-')),' '||chr(10),''),chr(10),''),chr(13),'')= replace(replace(replace(trim(COALESCE(s.address,'-')),' '||chr(10),''),chr(10),''),chr(13),''))) as sameaslastmail,
                        s.sentdatetime as lastmaildatetime,
                        COALESCE(s.direction,'-') || ', '  || COALESCE(s.startdatetime,'-') || ', ' || COALESCE(s.enddatetime,'-') || ', ' || COALESCE(s.stop,'-') || ', ' || COALESCE('' || s.seats_confirmed,'-') || ', ' || COALESCE('' || s.seats_pending,'-')  || ', ' || COALESCE('' || s.seats_not_confirmed,'-') || ', ' || COALESCE('' || s.touridno,'-') || ', ' || COALESCE(s.address,'-') as lastmailtxt from (            
                        select min(n.id) as id 
                        ,p.registration_id
                        ,n.webtour_touridno as touridno
                        ,left(replace(webtour_startdatetime,'T',' '),16) as startdatetime
                        ,left(replace(webtour_enddatetime,'T',' '),16)  as enddatetime
                        ,left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,10) as busterminaldate
                        ,right(left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,14),3) || right('0'|| right(left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,16),2)::int/15*15,2) as busterminaltime            
                        ,tt.name as direction
                        ,d.name as Stop
                        ,replace(d.address,E'\nDK','') as address
                        ,sum(case when needstatus in ('1','5') then 1 else 0 end) as seats_confirmed
                        ,sum(case when needstatus in ('2','3','4') then 1 else 0 end) as seats_pending
                        ,sum(case when needstatus in ('6','7') then 1 else 0 end) as seats_not_confirmed
                        ,min(n.create_date) as create_date 
                        ,min(n.create_uid) as  create_uid
                        ,max(n.write_date) as write_date
                        ,min(n.write_uid) as write_uid
                    from campos_webtourusneed  n 
                    inner join campos_webtourconfig_triptype tt on tt.id = "campos_TripType_id"
                    left outer join campos_webtourusdestination d on d.destinationidno = case when returnjourney then campos_enddestinationidno else campos_startdestinationidno end 
                    inner join campos_event_participant p on p.id = n.participant_id 
                    inner join event_registration r on r.id = p.registration_id
                    where needstatus <> '0' 
                    group by p.registration_id,r.name,webtour_touridno,tt.name,returnjourney,webtour_startdatetime, webtour_enddatetime,d.name,d.address,tt.returnjourney 
                    ) t 
                    left outer join (select ts.ticket_id, max(ts.id) as lastid from campos_webtourusneed_tickets_sent ts group by ts.ticket_id) lastsent on lastsent.ticket_id = t.id
                    left outer join campos_webtourusneed_tickets_sent as s on s.id  = lastsent.lastid
                    ) tt
                    group by registration_id
                    """
                    )   

class WebtourUsNeedTicketsParticipant(models.Model):
    _name = 'campos.webtourusneed.ticketsparticipant'
    _description = 'campos webtour usNeed Tickets Participant'
    _auto = False
    _log_access = False
  
    participant_id = fields.Many2one('campos.event.participant','Participant ID')
    touridno = fields.Char('Tour IDno')
    startdatetime = fields.Char('Start Date Time')
    enddatetime = fields.Char('End Date Time')  
    busterminaldate = fields.Char('Busterminal Date')
    busterminaltime = fields.Char('Busterminal Time') 
    direction = fields.Char('Direction')
    stop = fields.Char('Stop')
    address = fields.Char('Address')
    seats_confirmed = fields.Integer('Seats confirmed')
    seats_pending = fields.Integer('Seats pending')
    seats_not_confirmed = fields.Integer('Seats not confirmed')
    create_date = fields.Datetime('Create_date')
    create_uid = fields.One2many('res.users','id')
    write_date = fields.Datetime('write_date')
    write_uid = fields.One2many('res.users','id')    
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_ticketsparticipant as                  
                    select min(n.id) as id 
                    ,COALESCE(parent_jobber_id , n.participant_id )  as participant_id
                    ,webtour_touridno as touridno
                    ,left(replace(webtour_startdatetime,'T',' '),16) as startdatetime
                    ,left(replace(webtour_enddatetime,'T',' '),16)  as enddatetime
                    ,left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,10) as busterminaldate
                    ,right(left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,14),3) || right('0'|| right(left(case when tt.returnjourney then webtour_startdatetime else webtour_enddatetime end,16),2)::int/15*15,2) as busterminaltime            
                    ,tt.name as direction
                    ,d.name as Stop
                    ,replace(address,E'\nDK','') as address
                    ,sum(case when needstatus in ('1','5') then 1 else 0 end) as seats_confirmed
                    ,sum(case when needstatus in ('2','3','4') then 1 else 0 end) as seats_pending
                    ,sum(case when needstatus in ('6','7') then 1 else 0 end) as seats_not_confirmed 
                    ,min(n.create_date) as create_date 
                    ,min(n.create_uid) as  create_uid
                    ,max(n.write_date) as write_date
                    ,min(n.write_uid) as write_uid                    
                    from campos_webtourusneed  n 
                    inner join campos_webtourconfig_triptype tt on tt.id = "campos_TripType_id"
                    left outer join campos_webtourusdestination d on d.destinationidno = case when returnjourney then campos_enddestinationidno else campos_startdestinationidno end 
                    inner join campos_event_participant p on p.id = n.participant_id 
                    where needstatus <> '0' 
                    group by COALESCE(parent_jobber_id , n.participant_id ) ,webtour_touridno,tt.name,returnjourney,webtour_startdatetime, webtour_enddatetime,d.name,address,tt.returnjourney
                    order by 2,case when returnjourney then 2 else 1 end ,5       
                    """
                    )  


class WebtourUsNeedSeats(models.Model):
    _name = 'campos.webtourusneed.seats'
    _description = 'campos webtour usneed seats'
    _auto = False
    _log_access = False
  
    registration_id = fields.Many2one('event.registration','Registration ID')
    seats_confirmed = fields.Integer('Seats confirmed')
    seats_pending = fields.Integer('Seats pending')
    seats_not_confirmed = fields.Integer('Seats not confirmed')
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_seats as                  
                    select p.registration_id as id 
                    ,sum(case when needstatus in ('1','5') then 1 else 0 end) as seats_confirmed
                    ,sum(case when needstatus in ('2','3','4') then 1 else 0 end) as seats_pending
                    ,sum(case when needstatus in ('6','7') then 1 else 0 end) as seats_not_confirmed 
                    from campos_webtourusneed  n 
                    inner join campos_webtourconfig_triptype tt on tt.id = "campos_TripType_id"
                    left outer join campos_webtourusdestination d on d.destinationidno = case when returnjourney then campos_enddestinationidno else campos_startdestinationidno end 
                    inner join campos_event_participant p on p.id = n.participant_id 
                    inner join event_registration r on r.id = p.registration_id 
                    where needstatus <> '0' 
                    group by p.registration_id
                    order by 1       
                    """
                    )

class WebtourUsNeedSeatsParticipant(models.Model):
    _name = 'campos.webtourusneed.seatsparticipant'
    _description = 'campos webtour usneed seats participant'
    _auto = False
    _log_access = False
  
    participant_id = fields.Many2one('campos.event.participant','Participant ID')
    seats_confirmed = fields.Integer('Seats confirmed')
    seats_pending = fields.Integer('Seats pending')
    seats_not_confirmed = fields.Integer('Seats not confirmed')
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view campos_webtourusneed_seatsparticipant as                  
                    select participant_id as id 
                    ,sum(case when needstatus in ('1','5') then 1 else 0 end) as seats_confirmed
                    ,sum(case when needstatus in ('2','3','4') then 1 else 0 end) as seats_pending
                    ,sum(case when needstatus in ('6','7') then 1 else 0 end) as seats_not_confirmed 
                    from campos_webtourusneed  n 
                    inner join campos_webtourconfig_triptype tt on tt.id = "campos_TripType_id"
                    left outer join campos_webtourusdestination d on d.destinationidno = case when returnjourney then campos_enddestinationidno else campos_startdestinationidno end 
                    where needstatus <> '0' 
                    group by participant_id     
                    """
                    )
        
     
class WebtourUsNeedChanges(models.Model):
    _name = 'campos.webtourusneed.changes'
    _description = 'Campos Webtour usNeed Changes'
    WebtourUsNeed_id = fields.Many2one('campos.webtourusneed','id', ondelete='set null')
    idno = fields.Char('webtour_needidno')
    touridno = fields.Char('TourIDno', required=False)
    useridno = fields.Char('UserIDno', required=False)
    groupidno = fields.Char('GroupIDno', required=False)
    startdatetime = fields.Char('StartDateTime', required=False)
    startdestinationidno = fields.Char('StartDestinationIDno', required=False)
    startnote = fields.Char('StartNote', required=False)
    enddatetime = fields.Char('EndDateTime', required=False)
    enddestinationidno = fields.Char('EndDestinationIDno', required=False)
    endnote = fields.Char('EndNote', required=False)
    action = fields.Char('Action', required=False)
    actiondatetime = fields.Char('ActionDateTime', required=False)
    currentdatetime = fields.Char('CurrentDateTime', required=False)
    
    def sameasWebtourusneed(self):
        sdt = (self.WebtourUsNeed_id.webtour_startdatetime == fields.Date.from_string(self.startdatetime)) 
        sdi = (self.WebtourUsNeed_id.webtour_startdestinationidno ==  self.startdestinationidno)
        sn = ((self.WebtourUsNeed_id.webtour_startnote ==  self.startnote) or (self.WebtourUsNeed_id.webtour_startnote == "" and self.startnote == False)) 
        edi = (self.WebtourUsNeed_id.webtour_enddestinationidno ==  self.enddestinationidno) 
        en = ((self.WebtourUsNeed_id.cwebtour_endnote ==  self.endnote) or (self.WebtourUsNeed_id.webtour_endnote == "" and self.endnote == False))
        #_logger.info("sameasWebtourusneed %s %s %s %s %s",sdt , sdi , sn , edi , en)
        _logger.info("sameasWebtourusneed")
        return sdt and sdi and sn and edi and en
    
    
    
class Webtour_usNeedMinimum(models.Model):
    _name = 'campos.webtour.usneedminimum'
    _description = 'Campos Webtour usNeedminimum'
    idno = fields.Char('IDno')
    groupidno = fields.Char('GroupIDno')
    group_name = fields.Char('Group Name', compute='_compute_groupname')
    touridno = fields.Char('TourIDno')
    useridno = fields.Char('UserIDno')
    user_externalid = fields.Char('User ExternalID', compute='_compute_userexternalid', store=True)
    user_groupidno = fields.Char('User GroupIDno', compute='_compute_userexternalid', store=True)
    user_groupissame = fields.Boolean('Need and User Group same', compute='_compute_userexternalid', store=True)
    alias = fields.Char('Alias')
    
    
    @api.depends('groupidno')
    def _compute_groupname(self):
        groups = self.env['campos.webtour.usgroup']
        for rec in self:
            group = groups.search([('idno','=',rec.groupidno)])
            if len(group) > 0:
                rec.group_name = group[0].name

    @api.depends('useridno')
    def _compute_userexternalid(self):
        users = self.env['campos.webtour.ususerminimum']
        for rec in self:
            user = users.search([('idno','=',rec.useridno)])
            if len(user) > 0:
                rec.user_externalid = user[0].externalid
                rec.user_groupidno = user[0].groupidno
                rec.user_groupissame = rec.groupidno == user[0].groupidno

  
    @api.multi
    def getfromwebtour(self):
        usneed_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usNeed/GetAll/'}).responce.encode('utf-8'))
        
        alias=usneed_doc.getElementsByTagName("a:Alias")[0].firstChild.data        
        webtourneeds = usneed_doc.getElementsByTagName("a:usNeedMinimum")
   
        for webtourneed in webtourneeds:
            dicto = {}
            dicto["idno"] = webtourneed.getElementsByTagName("a:IDno")[0].firstChild.data
            dicto["groupidno"] = webtourneed.getElementsByTagName("a:GroupIDno")[0].firstChild.data
            dicto["touridno"] = webtourneed.getElementsByTagName("a:TourIDno")[0].firstChild.data
            dicto["useridno"] = webtourneed.getElementsByTagName("a:UserIDno")[0].firstChild.data
            dicto["alias"] = alias
            self.create(dicto)

class Webtour_usNeedError(models.Model):
    _name = 'campos.webtour.usneederror'
    _description = 'Campos Webtour usNeed error'
    idno = fields.Char('IDno')        

    @api.multi
    def action_deleteinwebtour(self):
        for rec in self:
            _logger.info("action_deleteinwebtour Deleting %s",rec.idno)
            self.env['campos.webtour_req_logger'].create({'name':'usNeed/Delete/?NeedIDno=' + rec.idno})

class Webtour_usUserMinimum(models.Model):
    _name = 'campos.webtour.ususerminimum'
    _description = 'Campos Webtour usUserminimum'
    idno = fields.Char('IDno')
    groupidno = fields.Char('GroupIDno')
    externalid = fields.Char('ExternalID')    
    alias = fields.Char('Alias')
    
    @api.multi
    def getfromwebtour(self):
        responce_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usUser/GetAll/'}).responce.encode('utf-8'))
        
        alias=responce_doc.getElementsByTagName("a:Alias")[0].firstChild.data        
        rs = responce_doc.getElementsByTagName("a:usUserMinimum")
   
        for rec in rs:
            dicto = {}
            dicto["idno"] = rec.getElementsByTagName("a:IDno")[0].firstChild.data
            dicto["groupidno"] = rec.getElementsByTagName("a:GroupIDno")[0].firstChild.data
            dicto["externalid"] = rec.getElementsByTagName("a:ExternalID")[0].firstChild.data
            dicto["alias"] = alias
            self.create(dicto)
       

class Webtour_usGroup(models.Model):
    _name = 'campos.webtour.usgroup'
    _description = 'Campos Webtour usGroup'
    idno = fields.Char('IDno')
    name = fields.Char('Name')
    alias = fields.Char('Alias')

    @api.multi
    def getfromwebtour(self):
        responce_doc=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/GetAll/'}).responce.encode('utf-8'))
        
        alias=responce_doc.getElementsByTagName("a:Alias")[0].firstChild.data        
        rs = responce_doc.getElementsByTagName("a:usGroup")
   
        for rec in rs:
            dicto = {}
            dicto["idno"] = rec.getElementsByTagName("a:IDno")[0].firstChild.data
            dicto["name"] = rec.getElementsByTagName("a:Name")[0].firstChild.data

            dicto["alias"] = alias
            self.create(dicto)

    