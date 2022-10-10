import pdb
import time
from odoo import api, fields, models,_, tools
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class NonSubSidizedFormWizard(models.TransientModel):
    _name = 'non.subsidized.form.wizard'
    _description = 'Non SubSidized Form Report Wizard'
    
    @api.model
    def _get_applicant(self):
        applicant_id = self.env['alifzerocms.application'].browse(self._context.get('active_id',False))
        if applicant_id:
            return applicant_id.id

    
    application_id = fields.Many2one('alifzerocms.application', 'Applicant', default=_get_applicant)


    def print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'alifzerocms.application',
            'form': data
        }

        return self.env.ref('alifzerocms_admission.action_report_non_subsidized_form').report_action(self, data=datas, config=False)





