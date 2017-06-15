# -*- coding: utf-8 -*-
# Copyright 2017 Stein & Gabelgaard ApS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import tools, api, fields, models, _
from openerp.exceptions import Warning

class CamposActivityActivity(models.Model):

    _name = 'campos.activity.activity'
    _description = 'Campos Activity'
    _order = 'name'
    _inherit = 'mail.thread'
    
    name = fields.Char('Name', size=128, translate=True, track_visibility='onchange')
    code = fields.Char('Code', size=20, track_visibility='onchange')
    activity_type_id = fields.Many2one('campos.activity.type', string='Type', track_visibility='onchange')
    committee_id = fields.Many2one('campos.committee', 'Committee', track_visibility='onchange')
    teaser = fields.Text('Teaser', translate=True, track_visibility='onchange')
    desc = fields.Html('Description', translate=True, track_visibility='onchange')
    equipment = fields.Text('Equipment', translate=True, track_visibility='onchange')
    leader_req = fields.Text('Leader req', translate=True, track_visibility='onchange')
    special_req = fields.Html('Special Req.', translate=True, track_visibility='onchange')
    duration = fields.Text('Duration', translate=True, track_visibility='onchange')
    comment = fields.Text('Internal Note')
    age_from =  fields.Integer('Age from', default=0, track_visibility='onchange')
    age_to = fields.Integer('Age to', default=99, track_visibility='onchange')
    #    'points' : fields.integer('Points'),
    
    audience_ids = fields.Many2many('campos.activity.audience', relation='campos_act_audience', string='Audience')
    act_ins_ids = fields.One2many('campos.activity.instanse', 'activity_id', 'Instanses')
    lang_ok = fields.Many2many('res.lang', string="Translation status")
    tag_ids = fields.Many2many('campos.activity.tag', relation='campos_act_tag', string='Tags')
    pitag_ids = fields.Many2many('campos.activity.pitag', relation='campos_act_pitag', string='PI Tags')
    state = fields.Selection([('idea', 'Idea'),
                              ('planning', 'Planning'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], 'State', default='idea', track_visibility='onchange')
    
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary('Image')
    image_filename = fields.Char("Image Filename")

    # Scaled Images
    image_medium = fields.Binary(string="Medium-sized image",
                                 store=False,
                                 compute="_get_image",
                                 inverse="_set_image",
                                 help="Medium-sized image of this activity. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")

    image_small = fields.Binary(string="Small-sized image",
                                store=False,
                                compute="_get_image",
                                inverse="_set_image",
                                help="Small sized image of this activity. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field in form views or some kanban views.")
    has_image = fields.Boolean('Ha Image', compute='_compute_has_image')
    
    @api.multi
    def unlink(self):
        if any(act.act_ins_ids for act in self):
            raise Warning(_('You can only delete unused activities!'))
    
    
    @api.multi
    def _compute_has_image(self):
        for a in self:
            a.has_image = bool(a.image)

    @api.one
    @api.depends("image")
    def _get_image(self):
        """ calculate the images sizes and set the images to the corresponding
            fields
        """
        image = self.image

        # check if the context contains the magic `bin_size` key
        if self.env.context.get("bin_size"):
            # refetch the image with a clean context
            image = self.env[self._name].with_context({}).browse(self.id).image

        data = tools.image_get_resized_images(image)
        self.image_medium = data["image_medium"]
        self.image_small = data["image_small"]
        return True
    
    def _set_image(self):
        return self.write({'image': tools.image_resize_image_big(self.image_medium)})