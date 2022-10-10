# -*- coding: utf-8 -*-
import pdb
from odoo import api, fields, models,_


class alifzerocmsChangeStudentState(models.TransientModel):
	_name ='alifzerocms.student.state.change'
	_description = 'Change Student State'
				
	@api.model
	def _get_students(self):
		if self.env.context.get('active_model', False) == 'alifzerocms.student' and self.env.context.get('active_ids', False):
			return self.env.context['active_ids']
			
	student_ids = fields.Many2many('alifzerocms.student', string='Students', default=_get_students,
		help="""Only selected students will be Processed.""")   #,
	state = fields.Selection([
		('draft', 'Draft'), ('enroll', 'Admitted'), ('alumni', 'Alumni'), ('suspend', 'Suspend'), ('struck', 'Struck Off'),
		('defer', 'Deferred'), ('cancel', 'Cancel'),
	], string='Status',
		default='enroll')
	rule_id = fields.Many2one('alifzerocms.student.change.state.rule', string = "Reason",)

	def change_student_state(self):
		for student in self.student_ids:
			if not student.batch_id:
				continue
			if not student.section_id:
				if student.batch_id and len(student.batch_id.section_ids) == 1:
					student.section_id = student.batch_id.section_ids[0].id
				else:
					continue
			
			if self.state == 'enroll':
				if not student.term_id:
					student.term_id = student.batch_id.term_id.id
				if not student.semester_id:
					student.semester_id = student.batch_id.semester_id.id
			
			
			# if (student.state == 'enroll' and (self.state in ('draft','suspend', 'cancel'))):
			# 	student.update({'state': self.state})
			# elif (student.state in ('draft','suspend', 'cancel') and self.state == 'enroll'):
			# 	student.update({'state': 'enroll'})

			student.state = self.state
		return {'type': 'ir.actions.act_window_close'}



