
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class alifzerocmsStudent(models.Model):
    _inherit = 'alifzerocms.student'
    
    application_id = fields.Many2one('alifzerocms.application', string="Application ref")
    application_date = fields.Datetime(string="Application Date", related='application_id.application_date', store=True)
    quota_id = fields.Many2one('alifzerocms.admission.quota' ,'Student Quota', tracking=True)
    entry_date = fields.Date(string="Entry Date")
    

    def student_documents(self):
        self.ensure_one()
        domain = [
            ('student_id', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'alifzerocms.application.documents',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                Click to Create for New Documents
                </p>'''),
            'limit': 80,
            'context': "{'default_student_id': %s,'default_application_id': %s}" % (self.id, self.application_id.id)
        }