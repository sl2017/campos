from openerp import models, fields

class Category(models.Model):
    _name = 'lost.category'
    name = fields.Char("Name")
    active = fields.Boolean("Active", default=True)