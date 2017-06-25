'''
Created on 2. dec. 2016

@author: jda.dk
'''
import logging

_logger = logging.getLogger(__name__)

from openerp import models, fields, api, tools
#from ..interface import webtourinterface
from math import sin, cos, sqrt, atan2, radians
from operator import itemgetter
import googlemaps
from xml.dom import minidom

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
def do_delayed_webtourdefaulthomedestination(session, model, reg_id):
    reg = session.env['event.registration'].browse(reg_id)
    if reg.exists():
        reg.set_webtourdefaulthomedestination()

@job(default_channel='root.webtour')
@related_action(action=related_action_generic)
def do_delayed_webtourupdate(session, model, reg_id):
    reg = session.env['event.registration'].browse(reg_id)
    if reg.exists():
        reg.webtourupdate()               

@job(default_channel='root.webtour')
@related_action(action=related_action_generic)
def do_delayed_owntransport_paxs(session, model, reg_id):
    reg = session.env['event.registration'].browse(reg_id)
    if reg.exists():
        reg.action_owntransport_paxs()    

class WebtourRegistration(models.Model):
    _inherit = 'event.registration'
    webtourusgroupidno = fields.Char('Webtour us Group ID no', required=False, Default='')
    webtourdefaulthomedestination = fields.Many2one('campos.webtourusdestination','id',ondelete='set null')
    webtourdefaulthomedestination_name  = fields.Char(related='webtourdefaulthomedestination.name', string='Default Pickup Place', readonly=True)
    webtourgrouptocampdestination_id = fields.Many2one('campos.webtourusdestination','Selected Pick up to Camp',ondelete='set null')
    webtourgroupfromcampdestination_id = fields.Many2one('campos.webtourusdestination','Selected Drop off from Camp',ondelete='set null')
    webtourdefaulthomedistance = fields.Float('Webtour Pickup Map Distance')
    webtourdefaulthomeduration = fields.Char('Webtour Pickup Map Duration')
    webtourPreregTotalSeats = fields.Integer(compute='_compute_webtourPreregBusToCamptotal', string='webtour Prereg Total Seats', store = True)
    webtourhasgeoadd = fields.Boolean(compute='_compute_webtourhasgeoadd', string='webtour Has Geo Adress', store = False)
    webtourtravelneed_ids = fields.One2many('event.registration.travelneed','registration_id','Special travel needs')
    webtourtravelneed2_ids = fields.One2many('event.registration.travelneed','registration_id','Special travel needs 2')
    #webtourhasbeeninitialized = fields.Boolean('Webtour has been initialized')
    group_country_code2 = fields.Char(related='partner_id.country_id.code', string='Country Code2', readonly=True)
    org_country_code2 = fields.Char(related='organization_id.country_id.code', string='Org Country Code2', readonly=True)
    org_name = fields.Char(related='organization_id.name', string='Org Name', readonly=True)
    
    groupisdanish = fields.Boolean(compute='_compute_groupisdanish', string='groupisdanish', store = False)
    webtourgroup_entrypointname = fields.Char(related="group_entrypoint.defaultdestination_id.name")
    webtourgroup_exitpointname = fields.Char(related="group_exitpoint.defaultdestination_id.name")
    webtourusneedtickets_ids = fields.One2many('campos.webtourusneed.tickets','registration_id','usNeed Tickets')
    webtourextrausneed_ids = fields.One2many('campos.webtourusneed','extra_registration_id','Extra usNeed')
    webtourusneed_seats_reg_id = fields.One2many('campos.webtourusneed.seats','id',ondelete='set null')
    webtourusneed_seats_confirmed = fields.Integer(string = 'Webtour Seats confirmed', related='webtourusneed_seats_reg_id.seats_confirmed',ondelete='set null') 
    webtourusneed_seats_pending = fields.Integer(string = 'Webtour Seats pending', related='webtourusneed_seats_reg_id.seats_pending',ondelete='set null') 
    webtourusneed_seats_not_confirmed = fields.Integer(string = 'Webtour Seats not confirmed', related='webtourusneed_seats_reg_id.seats_not_confirmed',ondelete='set null') 

    webtourusneed_ticket_overview_reg_id = fields.One2many('campos.webtourusneed.tickets.overview','id',ondelete='set null') 
    webtourusneed_ticketscnt =  fields.Integer(string = 'Webtour usNeed Tickets Cnt', related='webtourusneed_ticket_overview_reg_id.ticketscnt',ondelete='set null') 
    webtourusneed_ticketsentcnt = fields.Integer(string = 'Webtour usNeed Tickets sent Cnt', related='webtourusneed_ticket_overview_reg_id.ticketsentcnt',ondelete='set null') 
    webtourusneed_sameaslastmail = fields.Integer(string = 'Webtour usNeed Same as last mail', related='webtourusneed_ticket_overview_reg_id.sameaslastmail',ondelete='set null')
    
    arrival_ids   = fields.One2many('event.registration.campos.arrivaldeparture','registration_id','Arrivals', domain=[('fromcamp', '=', False)])  
    departure_ids = fields.One2many('event.registration.campos.arrivaldeparture','registration_id','Departures', domain=[('fromcamp', '=', True)])  
    
    
    
    @api.multi
    def write(self, vals):
        _logger.info("Write Entered %s", vals.keys())
        ret = super(WebtourRegistration, self).write(vals)
    
        for reg in self:
            
            if ('webtourdefaulthomedestination' in vals):
                dicto={}
                dicto["recalctoneed"]=True
                dicto["recalcfromneed"]=True
                for par in reg.participant_ids:
                    par.write(dicto)  
            else:  
                if  ('webtourgrouptocampdestination_id' in vals or 'group_entrypoint' in vals):
                    for par in reg.participant_ids:
                        par.recalctoneed=True
        
                if  ('webtourgroupfromcampdestination_id' in vals or 'group_exitpoint' in vals ):
                    for par in reg.participant_ids:
                        par.recalcfromneed=True                               
        return ret
    
    @api.depends('group_country_code2','org_name','org_country_code2')
    def _compute_groupisdanish(self):
        for record in self:
                       
            if record.org_name == 'Dansk Spejderkorps Sydslesvig':
                record.groupisdanish = True
            elif record.group_country_code2:
                if (record.group_country_code2 == 'DK'):
                    record.groupisdanish = True
                else:
                    if record.org_country_code2:
                        if (record.group_country_code2 == 'DK'):
                            record.groupisdanish = True
                        elif len(record.group_country_code2) == 2 and record.group_country_code2 != '  ':
                            record.groupisdanish = False
                        else: 
                            record.groupisdanish = True                           
            else:
                if record.org_country_code2:
                    if (record.org_country_code2 == 'DK'):
                        record.groupisdanish = True
                    elif len(record.org_country_code2) == 2 and record.org_country_code2 != '  ':
                        record.groupisdanish = False
                    else: 
                        record.groupisdanish = True    
                else: 
                    record.groupisdanish = True 
    
    @api.depends('prereg_participant_ids.participant_total','prereg_participant_ids.participant_own_transport_to_camp_total','prereg_participant_ids.participant_own_transport_from_camp_total')
    def _compute_webtourPreregBusToCamptotal(self):
        for record in self:
            record.webtourPreregTotalSeats = sum(2*line.participant_total - line.participant_own_transport_to_camp_total -line.participant_own_transport_from_camp_total for line in record.prereg_participant_ids)

    @api.depends('partner_id.partner_latitude','partner_id.partner_longitude')
    def _compute_webtourhasgeoadd(self):
        for record in self:
            record.webtourhasgeoadd = record.partner_id.partner_latitude <> 0 and record.partner_id.partner_longitude <> 0
           
    @api.one
    def set_webtourdefaulthomedestination(self):
        if self.groupisdanish:
            # If gep point is missing, try to calculate
            if (self.partner_id.partner_latitude==0):
                self.partner_id.geocode_address()
                if (self.partner_id.partner_latitude > 0):
                    _logger.info("Try to commit Non Google geocode")
                    self.env.cr.commit()
                
            # if still no result try geocode with Googlemap
            if (self.partner_id.partner_latitude==0):
                gmaps2 = googlemaps.Client(key=self.env['ir.config_parameter'].get_param('campos_transportation_googlemaps_key.geocode'))
    
                _logger.info("Try to Geocode with Googlemaps %s %s %s",self.partner_id.street,self.partner_id.zip,self.partner_id.city)
                
                try:
                    a = self.partner_id.street+', '+ self.partner_id.zip+' '+self.partner_id.city
                    geocode_result = gmaps2.geocode(a)
                    lat=geocode_result[0]['geometry']['location']['lat']
                    lng=geocode_result[0]['geometry']['location']['lng']
                    self.partner_id.partner_latitude = float(lat)
                    self.partner_id.partner_longitude = float(lng)
                    _logger.info("Got Googlemap Geocoding  %f %f",self.partner_id.partner_latitude,self.partner_id.partner_longitude)
                    self.env.cr.commit()
                except:
                    pass
                                    
            # If geo point pressent lets go.... GOOGLEMAP DIAABLED          
            if (self.partner_id.partner_latitude<>0):    
    
                destinations = self.env['campos.webtourusdestination'].search([('name', '<>', '')])
                
                # approximate radius of earth in km
                R = 6373.0
                
                #Home adresse cord
                lat1 = radians(self.partner_id.partner_latitude)
                lon1 = radians(self.partner_id.partner_longitude)  
    
                dists=[] #placeholder for beeline distance from home to all destinations
                
                for d in destinations:
                    lat2 = radians(float(d.latitude))
                    lon2 = radians(float(d.longitude))
                    
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
    
                    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                    c = 2 * atan2(sqrt(a), sqrt(1 - a))
                    distance = R * c
                    
                    dists.append([d.id,distance,float(d.latitude),float(d.longitude)]) 
                  
                sdists = sorted(dists, key=itemgetter(1)) #we need the distance i acending order
    
                lat1 = self.partner_id.partner_latitude
                lon1 = self.partner_id.partner_longitude
                  
                n = 0;  #counter for no of dist to googlemaps
                origins=[] #placeholder list for origons to googlemaps
                destinations =[] #placeholder list for desinations to googlemaps
                origins.append((lat1,lon1)) #Home add            
                homedestination = False
                homedistance = False
                homeduration = False
                for d in sdists: # loop through sorted pickuplocations and prepare datat for googlemaps request
    
                    destinations.append((d[2],d[3])) # get geo point stored in loop above
                    n = n+1 
                    if (n > 4):
                        break       #Max 5 distinations    
                      
                # call googlemap to find distances by car to the neerst distinations
                gmaps = googlemaps.Client(key=self.env['ir.config_parameter'].get_param('campos_transportation_googlemaps_key.distance_matrix'))
                matrix = gmaps.distance_matrix(origins, destinations)
                _logger.info("Google maps responce %s", matrix)
                
                n = 0
                for d in sdists: # loop through sorted pickuplocations and evaluate corosponing googlemaps responce
                    distance=matrix['rows'][0]['elements'][n]['distance']['value']
                    distancekm =  distance/1000.0             
                    duration=matrix['rows'][0]['elements'][n]['duration']['text']
                    
                    if (n == 0): 
                        homedistance = distancekm
                        homeduration = duration
                        homedestination = d[0]
                    else:
                        if (homedistance > distancekm):
                            homedestination = d[0]
                            homedistance = distancekm
                            homeduration = duration                    
                    
                    n = n+1 
                    if (n > 4):
                        break       #Max 5 distinations
                            
                if homedestination:
                    _logger.info("Closest Home Destination found %s %f %s",homedestination, homedistance,homeduration)    
                    self.webtourdefaulthomedistance = homedistance
                    self.webtourdefaulthomeduration = homeduration
                    self.webtourdefaulthomedestination = homedestination
                else:
                    _logger.info("!!!!!!!!!!!! No Home Destination found")
                                               
        else:
            self.webtourdefaulthomedistance = False
            self.webtourdefaulthomeduration = False
            if self.webtourdefaulthomedestination: self.webtourdefaulthomedestination = False
            dicto={}
            dicto["recalctoneed"]=True
            dicto["recalcfromneed"]=True
            for par in self.participant_ids:
                    par.write(dicto)       
    
    @api.one
    def webtourupdate(self):
        _logger.info('%s webtourupdate Entered', self.id)
        webtoutexternalid_prefix = self.event_id.webtourconfig_id.webtoutexternalid_prefix
        
        if self.webtourusgroupidno:
            # Test if usGroup exist in Webtour
            newidno=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/GetByName/?Name='+str(self.id)}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data
      
            if newidno == "0": #If not try to Create new usGroup
                _logger.info("%s webtourupdate Group Could not find usGroup in Webtour: %s %s",str(self.id), self.name, self.webtourusgroupidno)
                '''
                newidno=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/Create/?Name='+str(self.id)}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data
                
                if newidno <> "0": # usGroup created succesfully
                    _logger.info("%s webtourupdate Recreate usGroup %s %s %s",str(self.id), self.name, self.webtourusgroupidno, newidno)
                    self.webtourusgroupidno = newidno
                else:
                    _logger.info("%s webtourupdate Could not Recreate usGroup %s %s",str(self.id), self.name, self.webtourusgroupidno) 
                '''   
            elif newidno <> self.webtourusgroupidno : #STRANGE got other usGroup Id
                _logger.info("%s webtourupdate usGroup NOT SAME in WEBTOUR %s %s %s",str(self.id), self.name, self.webtourusgroupidno, newidno)
                self.webtourusgroupidno = newidno

        else: #If not try to Create new usGroup
            newidno=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usGroup/Create/?Name='+str(self.id)}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data
            
            if newidno <> "0": # usGroup created succesfully
                _logger.info("%s webtourupdate Created usGroup %s %s %s",str(self.id), self.name, self.webtourusgroupidno, newidno)
                self.webtourusgroupidno = newidno
            else:
                _logger.info("%s webtourupdate Could not Create usGroup %s %s",str(self.id), self.name, self.webtourusgroupidno) 
         
        if self.webtourusgroupidno: # Check usUser
            
            #Get all usUserIDno's from webtour and conver to a simple list
            response_doc = minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':'usUser/GetAll/GroupIDno/?GroupIDno='+self.webtourusgroupidno}).responce.encode('utf-8'))                  
            ususers = response_doc.getElementsByTagName("a:IDno")
            ususerslist=[]
            for u in ususers:
                ususerslist.append(str(u.firstChild.data))
                
            #find participants not in list and try to Create usUser
            rs_missingususeridno= self.env['campos.event.participant'].search([('webtourusgroupidno', '=', self.webtourusgroupidno),('webtourususeridno', 'not in', ususerslist)
                                                                          ,'|',('transport_to_camp', '=', True),('transport_from_camp', '=', True)])           
            for par in rs_missingususeridno:
                extid = webtoutexternalid_prefix+str(par.id)+par.webtour_externalid_suffix
                req="usUser/Create/WithGroupIDno/?FirstName=" + str(par.id) + "&LastName=" + str(par.registration_id.id) + "&ExternalID=" + extid + "&GroupIDno=" + par.webtourusgroupidno
                newidno=minidom.parseString(self.env['campos.webtour_req_logger'].create({'name':req}).responce.encode('utf-8')).getElementsByTagName("a:IDno")[0].firstChild.data            
                
                if newidno <> "0":
                    _logger.info("%s webtourupdate Created usUser: %s %s %s",str(par.id), par.name, par.webtourusgroupidno, newidno)
                    par.webtourususeridno=newidno
                else:
                    _logger.info("%s webtourupdate Could not Create usUser: %s %s",str(par.id), par.name, par.webtourusgroupidno)
                    par.webtourususeridno=False

            usneeds= self.env['campos.webtourusneed'].search([('webtour_groupidno', '=', self.webtourusgroupidno),('webtour_useridno', '!=', False)])           
            _logger.info('%s webtourupdate No of usNeeds to update %s',self.id,len(usneeds))
            for usneed in usneeds:
                usneed.get_create_webtour_need()
            
    @api.multi
    def action_update_webtourtravelneed_ids(self):
        for reg in self:
            for par in reg.participant_ids:
                par.tocampusneed_id.calc_travelneed_id()
                par.fromcampusneed_id.calc_travelneed_id()
                
    @api.multi
    def action_update_webtourdefaulthomedestination(self):
        for reg in self:
            reg.set_webtourdefaulthomedestination()               
        
    @api.multi
    def action_batchupdate_webtourdefaulthomedestination(self):
        for reg in self:
            session = ConnectorSession.from_env(self.env)
            do_delayed_webtourdefaulthomedestination.delay(session, 'event.registration', reg.id)
 
    @api.multi
    def action_webtourupdate(self):
        for reg in self:
            session = ConnectorSession.from_env(self.env)
            do_delayed_webtourupdate.delay(session, 'event.registration', reg.id)
 
    @api.multi
    def action_makejob_owntransport_paxs(self,event_id):
        _logger.info("action_makejob_owntransport_paxs %s %s %s",self,len(self), event_id)
        
        regs = self.search([('event_id','=',event_id),('partner_id.scoutgroup','=',True),('state','!=','cancel')])
        _logger.info("action_makejob_owntransport_paxs regd %s",len(regs))
        
        for reg in regs:
            #_logger.info("action_makejob_owntransport_paxs %s",reg.id) 
            session = ConnectorSession.from_env(self.env)
            do_delayed_owntransport_paxs.delay(session, 'event.registration', reg.id)            

    
    @api.multi
    def action_send_traveltimeemail(self):
        sentdatetime = fields.Datetime.now()[:17] + '00'
        for reg in self:
            _logger.info('action_send_traveltimeemail entered')
            template = self.env.ref('campos_transportation.webtour_ticket_mail_group')
            assert template._name == 'email.template'
            sent = False
            _logger.info('%s action_send_traveltimeemail try to send', reg.id)
            try:
                template.send_mail(reg.id)
                sent = True
            except:
                pass               
            
            if sent:
                for ticket in reg.webtourusneedtickets_ids:
                    dic = {}
                    dic['ticket_id'] = ticket.id
                    dic['sentdatetime'] = sentdatetime 
                    dic['registration_id'] = ticket.registration_id.id
                    dic['touridno'] = ticket.touridno 
                    dic['startdatetime'] = ticket.startdatetime 
                    dic['enddatetime'] = ticket.enddatetime
                    dic['busterminaldate'] = ticket.busterminaldate
                    dic['busterminaltime'] = ticket.busterminaltime 
                    dic['direction'] = ticket.direction 
                    dic['stop'] = ticket.stop
                    dic['address'] = ticket.address
                    dic['seats_confirmed'] = ticket.seats_confirmed
                    dic['seats_pending'] = ticket.seats_pending
                    dic['seats_not_confirmed'] = ticket.seats_not_confirmed
                    self.env['campos.webtourusneed.tickets.sent'].create(dic)
                    _logger.info('%s action_send_traveltimeemail sent %s', reg.id,dic)

    @api.one
    def action_owntransport_paxs(self):
        _logger.info('%s action_owntransport_pax here we go',self.id)
        for day in self.env['event.registration.campos.arrivaldeparture.pax'].search([('registration_id','=',self.id)]):
            #_logger.info('%s action_owntransport_paxs %s', day)
            arivalday = self.env['event.registration.campos.arrivaldeparture'].search([('registration_id','=',self.id),('traveldate','=',day.traveldate),('fromcamp','=',False)])
            departday = self.env['event.registration.campos.arrivaldeparture'].search([('registration_id','=',self.id),('traveldate','=',day.traveldate),('fromcamp','=',True)])
            
            #_logger.info('%s action_owntransport_paxs %s %s', self.id,arivalday,departday)
            
            usneedto =   self.env['campos.webtourusneed.travelneedpax.day'].search([('registration_id', '=', self.id),('traveldate','=',day.traveldate),('fromcamp','=',False)])
            usneedfrom = self.env['campos.webtourusneed.travelneedpax.day'].search([('registration_id', '=', self.id),('traveldate','=',day.traveldate),('fromcamp','=',True)])
            
            topax = 0
            frompax = 0            
            if day.arrivalpax > usneedto.pax:
                topax= day.arrivalpax - usneedto.pax
            
            if day.departpax > usneedfrom.pax:
                frompax= day.departpax - usneedfrom.pax                          
                        
            if arivalday:
                arivalday.pax=topax
            else:
                if topax:
                    self.env['event.registration.campos.arrivaldeparture'].create({'registration_id':self.id,'traveldate':day.traveldate,'fromcamp':False,'pax':topax})
                    
            if departday:
                departday.pax=frompax
            else:
                if frompax:
                    self.env['event.registration.campos.arrivaldeparture'].create({'registration_id':self.id,'traveldate':day.traveldate,'fromcamp':True,'pax':frompax})

'''
    @api.one
    def createTestParticipants(self):
                
        for age_group in self.participant_ids:
            _logger.info("createTestParticipants: %s",age_group.participant_age_group_id.name)
            for i in range(0,age_group.participant_total):
                    dicto0 = {}
                    dicto0["name"] = age_group.registration_id.name + ' ' + age_group.participant_age_group_id.name + 'Test ID ' + str(i)   
                    dicto0["email"] = 'jd@darum.name'             
                
                    partner_obj = self.env['res.partner']                
                    newpartner = partner_obj.create(dicto0)
                    dicto1 = {}
                    dicto1["partner_id"] = newpartner.id 
                    dicto1["registration_id"] = self.id
                    dicto1["participant"] = True     
                    #dicto1["tocampfromdestination_id"] = self.env['campos.webtourusdestination'].search([('destinationidno','=',4390)]).id     
                    #dicto1["fromcamptodestination_id"] = dicto1["tocampfromdestination_id"]  
                    dicto1["tocampdate"] = age_group.participant_from_date
                    dicto1["fromcampdate"] = age_group.participant_to_date
                    dicto1["transport_to_camp"] = i > age_group.participant_own_transport_to_camp_total
                    dicto1["transport_from_camp"] = i > age_group.participant_own_transport_from_camp_total

                    _logger.info("createTestParticipants: %s",dicto1)
                                                  
                    newparticipant_obj = self.env['campos.event.participant']                
                    newparticipant = newparticipant_obj.create(dicto1)
                    newparticipant.tocampfromdestination_id = self.webtourdefaulthomedestination
                    newparticipant.fromcamptodestination_id = self.webtourdefaulthomedestination
                
    @api.one
    def createTestParticipantsAll(self):
        regs = self.env['event.registration'].search([('webtourdefaulthomedestination', '=', False),('partner_id', '<>', False),('webtourPreregTotalSeats', '>', 0)])
        _logger.info("createTestParticipantsAll Stil to go %s", len(regs)) 
        n=0
        for reg in regs:
            reg.set_webtourdefaulthomedestination()
            _logger.info("createTestParticipantsAll %s, Dest: %s, Participants:  %s",reg.name, reg.webtourdefaulthomedestination.id, len(reg.participant_ids)) 
            reg.createTestParticipants()
            n= n+1
            if n> 30: 
                break
    
    @api.one
    def seteventdaysRegParticipantsAll(self):
        #regs = self.env['event.registration'].search([('event_id', '=', 1),('partner_id', '<>', False),('jdatemp1','=',True)])
        #for reg in regs:
        #    reg.jdatemp1=False
                                
        regs = self.env['event.registration'].search([('event_id', '=', 1),('partner_id', '<>', False),('jdatemp1','=',False),('partner_id.scoutgroup', '=', True)])
        _logger.info("seteventdaysRegParticipantsAll Stil to go %s", len(regs))
        n = 0 
        for reg in regs:
            _logger.info("seteventdaysRegParticipantsAll Here we go %s", reg.name)
            reg.seteventdaysRegParticipants()
            reg.jdatemp1=True
            n= n+1
            if n> 4000:
                break
 
    @api.one
    def seteventdaysRegParticipants(self):
        _logger.info("seteventdaysRegParticipant %s %s", self.name, len(self.participant_ids)) 

        for par in self.participant_ids:
            par.check_camp_days()
            for day in par.camp_day_ids:
                day.will_participate = False
                     
        for age_group in self.prereg_participant_ids:
            _logger.info("seteventdaysRegParticipant in agegroup: %s",age_group.participant_age_group_id.name)

            for i in range(0,age_group.participant_total):
                found = False
                s= age_group.registration_id.name + ' ' + age_group.participant_age_group_id.name + 'Test ID ' + str(i)
                _logger.info("seteventdaysRegParticipant in agegroup %s, %s, %s",str(i),s,age_group.participant_from_date)

                for p in self.participant_ids.search([('partner_id.name','=',age_group.registration_id.name + ' ' + age_group.participant_age_group_id.name + 'Test ID ' + str(i))]):                 
                    if p.dates_summery == False and found == False:
                        for day in p.camp_day_ids:
                            if day.the_date >= age_group.participant_from_date and day.the_date <= age_group.participant_to_date:
                                day.will_participate = True
                        _logger.info("seteventdaysRegParticipant in agegroup TRANSPORT %s, %s, %s",str(i),age_group.participant_own_transport_to_camp_total,age_group.participant_own_transport_from_camp_total )                   
                        p.transport_to_camp = i > age_group.participant_own_transport_to_camp_total
                        p.transport_from_camp = i > age_group.participant_own_transport_from_camp_total        
                        found = True
                    
                    if found:
                        break            
''' 


class WebtourRegistrationTravelNeed(models.Model):
    '''
    Special Travel need on a registration
    '''
    _description = 'Webtour Special Travel need on a registration'
    _name='event.registration.travelneed'
    registration_id  = fields.Many2one('event.registration', 'Registration', ondelete='set null')
    travelgroup = fields.Char('Travel Group')
    name = fields.Char('Name', required=True)
    campos_TripType_id = fields.Many2one('campos.webtourconfig.triptype','Webtour_TripType', ondelete='set null')
    traveldate = fields.Date('Travel Date')
    startdestinationidno = fields.Many2one('campos.webtourusdestination.view','From',ondelete='set null')
    enddestinationidno = fields.Many2one('campos.webtourusdestination.view','To',ondelete='set null') 
    travelconnectiondetails = fields.Char('Connection Details')
    deadline = fields.Selection([    ('Select', 'Please Select'),
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

    overview = fields.One2many('campos.webtourusneed.travelneedpax','id',ondelete='set null')
    pax  = fields.Integer(related='overview.pax', string='PAX', readonly=True)
      
    
class WebtourEntryExitPoint(models.Model):
    _inherit = 'event.registration.entryexitpoint'
    address = fields.Char('Address', required=False)
    latitude = fields.Char(string='Latitude', required=False)
    longitude = fields.Char(string='Longitude', required=False)
    defaultdestination_id = fields.Many2one('campos.webtourusdestination','Selected Destination',ondelete='set null')

    @api.multi
    def write(self, vals):
        _logger.info("Write Entered %s", vals.keys())
        ret = super(WebtourEntryExitPoint, self).write(vals)              
        for rec in self:
            if  ('address' in vals):
                gmaps = googlemaps.Client(key=self.env['ir.config_parameter'].get_param('campos_transportation_googlemaps_key.geocode'))
            
                _logger.info("Try to Geocode with Googlemaps %s %s",rec.name,rec.address)
                
                try:
                    geocode_result = gmaps.geocode(rec.address)
                    lat=geocode_result[0]['geometry']['location']['lat']
                    lng=geocode_result[0]['geometry']['location']['lng']
                    rec.latitude = float(lat)
                    rec.longitude = float(lng)
                    _logger.info("Got Googlemap Geocoding  %f %f",rec.latitude,rec.longitude)
                    self.env.cr.commit()
                except:
                    rec.latitude = False
                    rec.longitude = False  
                    
        return ret

class CamposArrivalDeparture(models.Model):
    '''
    Arrival and Departure details (non Camp Transportation)
    '''
    _description = 'Arrival and Departure details (non Camp Transportation)'
    _name='event.registration.campos.arrivaldeparture'
    registration_id  = fields.Many2one('event.registration', 'Registration', ondelete='set null')
    traveldate = fields.Date('Date', required=True) 
    fromcamp = fields.Boolean('From Camp', required=True)
    eta = fields.Selection([('Select', 'Please Select'),
                            ('00:00', '00:00 - 00:59'),
                            ('01:00', '01:00 - 01:59'),
                            ('02:00', '02:00 - 02:59'),
                            ('03:00', '03:00 - 03:59'),
                            ('04:00', '04:00 - 04:59'),
                            ('05:00', '05:00 - 05:59'),                                    
                            ('06:00', '06:00 - 06:59'),
                            ('07:00', '07:00 - 07:59'),
                            ('08:00', '08:00 - 08:59'),
                            ('09:00', '09:00 - 09:59'),                                     
                            ('10:00', '10:00 - 10:59'),                                     
                            ('11:00', '11:00 - 11:59'),
                            ('12:00', '12:00 - 12:59'),
                            ('13:00', '13:00 - 13:59'),
                            ('14:00', '14:00 - 14:59'),
                            ('15:00', '15:00 - 15:59'),                                    
                            ('16:00', '16:00 - 16:59'),
                            ('17:00', '17:00 - 17:59'),
                            ('18:00', '18:00 - 18:59'),
                            ('19:00', '19:00 - 19:59'),                                     
                            ('20:00', '20:00 - 20:59'),                                     
                            ('21:00', '21:00 - 21:59'),
                            ('22:00', '22:00 - 22:59'),
                            ('23:00', '23:00 - 23:59')                                                                         
                             ], default='Select', string='Time')
    pax = fields.Integer('pax')
    cars = fields.Integer('No of Cars')
    trailes = fields.Integer('No of Trailes')
    coaches = fields.Integer('No of Coaches')
    bikes = fields.Integer('pax on Bikes')
    onfoot = fields.Integer('pax on foot')
    bytrain = fields.Integer('pax bytrain')
    
class CamposArrivalDeparturePax(models.Model):
    '''
    Arrival and Departure PAX
    '''
    _description = 'Arrival and Departure participant Registrations pax'
    _name='event.registration.campos.arrivaldeparture.pax'
    _auto = False
    _log_access = False
    
    registration_id  = fields.Many2one('event.registration', 'Registration', ondelete='set null')
    traveldate = fields.Date('Date', required=True) 
    arrivalpax = fields.Integer('Arrival pax') 
    departpax = fields.Integer('Depature pax')
    
    def init(self, cr, context=None):
        tools.sql.drop_view_if_exists(cr, self._table)
        cr.execute("""
                    create or replace view event_registration_campos_arrivaldeparture_pax as      
                    SELECT min(d1.id) as id, d1.registration_id_stored as registration_id,  d1.the_date as traveldate, sum(case when not COALESCE(d2.will_participate,not d1.will_participate) then 1 else 0 end) as arrivalpax , sum(case when not COALESCE(d3.will_participate,not d1.will_participate) then 1 else 0 end) as departpax FROM campos_event_participant_day d1
                    left outer join campos_event_participant_day d2 on d2.participant_id = d1.participant_id and d2.the_date = d1.the_date -1
                    left outer join campos_event_participant_day d3 on d3.participant_id = d1.participant_id and d3.the_date = d1.the_date +1 
                    inner join campos_event_participant p on p.id = d1.participant_id and p.state != 'deregistered'
                    where d1.will_participate and ((not COALESCE(d2.will_participate,not d1.will_participate)) or (not COALESCE(d3.will_participate,not d1.will_participate)))
                    group by d1.registration_id_stored, d1.the_date
                    """
                    )        
    
    