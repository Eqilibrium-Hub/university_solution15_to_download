from datetime import date
from odoo.tools.translate import _
from odoo import models, fields, api


class hr_holidays(models.Model):
	_name = 'alifzerocms.holidays.public'
	_description = 'Public Holidays'
	_order = "date, name desc"
	
	name = fields.Char('Name', required=True)
	date = fields.Date('Date', required=True)
	term_id = fields.Many2one('alifzerocms.academic.term','Academic Term')
	variable = fields.Boolean('Date may change')


class alifzerocmsAcademicTerm(models.Model):
	_inherit = 'alifzerocms.academic.term'

	pubilc_holidays_ids = fields.One2many('alifzerocms.holidays.public', 'term_id', string='Public Holidays')