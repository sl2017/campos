# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ..interface import webtourinterface
class WebtourParticipant(models.Model):
    _name = 'webtour.campos.event.participant'
    _description = 'Webtour Event Participant'
#    _inherit = 'campos.event.participant'

    participant_id = fields.Char('participant ID', required=True)
    troop_id = fields.Char('troop ID', required=True)
    ususeridno = fields.Char('US User ID', required=False)
    usgroupidno = fields.Char('US Group ID', required=False)
	
    tocampfromdestination = fields.Many2one('campos.webtourusdestination',
                                            'destinationidno',
                                            ondelete='set null')
    fromcamptodestination = fields.Many2one('campos.webtourusdestination',
                                            'destinationidno',
                                            ondelete='set null')
    tocampdate = fields.Date('To Camp Date', required=False)
    fromcampdate = fields.Date('From Camp Date', required=False)
    usecamptransporttocamp = fields.Boolean('Use Camp Transport to Camp', required=True, default=True)
    usecamptransportfromcamp = fields.Boolean('Use Camp Transport from Camp', required=True, default=True)
    tocampneedidno = fields.Char('To Camp Need ID', required=False)
    fromcampneedidno = fields.Char('From Camp Need ID', required=False)

	 #This method will be called when the field troop_id changes.
    def on_change_troop(self,cr,user,ids,troop_id,context=None):
		groupidno = self.groupidno # prepare to retun current value

		#Try to get Webtour usGroupIDno
		if troop_id <> None:
			# get or create usgroup from webtour matching troop_id
			groupidno=webtourinterface.usgroup_getbyname(troop_id)
			if groupidno == "0":
				groupidno=webtourinterface.usgroup_create(troop_id)
		
		res = {
			'value': {
				'usgroupidno' : 'hi'#groupidno	
				}
			}
		#Return the values to update it in the view.
		return res

	 #This method will be called when either the field participant_id or the field groupidno changes.
    def on_change_participant(self,cr,user,ids,participant_id,groupidno,context=None):	
		ususeridno = self.ususeridno # prepare to retun current value
		
		#Try to get Webtour usUserIDno
		if usgroupidno <> None and participant_id <> None:
			ususeridno=webtourinterface.ususer_getbyexternalid(participant_id)
			if ususeridno == "0":
				ususeridno=webtourinterface.ususer_create(participant_id, usgroupidno, participant_id, troop_id)
		
		res = {
			'value': {
			'ususeridno': ususeridno	
			}
			}
		#Return the values to update it in the view.
		return res

    def create_update_needs_online(self, cr, uid, ids, context=None):
        webtourususer_obj = self.pool.get('campos.webtourususer')
        webtourususer_obj.get_create_webtourususer(cr, uid, self, context)

    def create_update_needs(self, cr, uid, context=None):

        def get_tag_data(nodetag):
            try:
                tag_data = usDestination.getElementsByTagName(nodetag)[0].firstChild.data
            except:
                tag_data = None

            return tag_data

        webtourusdestination_obj = self.pool.get('campos.webtourusdestination')

        response_doc=webtourinterface.usdestinations_getall()

        destinations = response_doc.getElementsByTagName("a:usDestination")

        for usDestination in destinations:
            destinationidno = get_tag_data("a:IDno")
            webtour_dict = {}
            webtour_dict["destinationidno"] = destinationidno
            webtour_dict["name"] = get_tag_data("a:Name")
            webtour_dict["placename"] = get_tag_data("a:PlaceName")
            webtour_dict["address"] = get_tag_data("a:Address")
            webtour_dict["latitude"] = get_tag_data("a:Latitude")
            webtour_dict["longitude"] = get_tag_data("a:Longitude")
            webtour_dict["note"] = get_tag_data("a:Note")

            rs_webtourdestination = self.pool.get('campos.webtourusdestination').search(cr, uid, [('destinationidno','=',destinationidno)])
            rs_webtourdestination_count = len(rs_webtourdestination)
            if rs_webtourdestination_count == 0:
                webtourusdestination_obj.create(cr, uid, webtour_dict)
            else:
                webtourusdestination_obj.write(cr, uid, rs_webtourdestination, webtour_dict)

        return True

    @api.onchange('troop_id') #This method will be called when the field troop_id changes.
    def on_change_troop(self):
    #Try to get Webtour usGroupIDno
        if self.troop_id <> None:
        # get or create usgroup from webtour matching troop_id
            newidno=webtourinterface.usgroup_getbyname(self.troop_id)
            if newidno == "0":
                newidno=webtourinterface.usgroup_create(self.troop_id)

                if newidno <> "0":
                    self.groupidno = newidno

    @api.onchange('participant_id','groupidno') #This method will be called when either the field participant_id or the field groupidno changes.
    def on_change_participant(self):                
        #Try to get Webtour usUserIDno
        if self.usgroupidno <> None and self.usgroupidno <> "0" and self.participant_id <> None:
            newidno=webtourinterface.ususer_getbyexternalid(self.participant_id)
            if newidno == "0":
                newidno=webtourinterface.ususer_create(self.participant_id, self.usgroupidno, self.participant_id, self.troop_id)
                if newidno <> "0":
                    self.usgroupidno = newidno 

