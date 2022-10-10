import pdb
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc
import time

from odoo import http
import logging
_logger = logging.getLogger(__name__)


class AdmissionFinalReport(models.AbstractModel):
    _name = 'report.alifzerocms_admission_portal.report_admission'
    _description = 'Admission Final Report'

    @api.model
    def _get_report_values(self, docsid, data=None):
        application = self.env['alifzerocms.application'].browse(docsid)
        matric_education = http.request.env['alifzerocms.application.academic'].sudo().search(
            [('application_id', '=', application.id), ('degree_level', 'in', ('Matric', 'O-Level'))])
        inter_education = http.request.env['alifzerocms.application.academic'].sudo().search(
            [('application_id', '=', application.id), ('degree_level', 'in', ('A-Level', 'Intermediate', 'DAE'))])
        program_preferences_ordered = http.request.env['alifzerocms.application.preference'].sudo().search([('application_id', '=', application.id)], order='preference asc')
        application_documents = http.request.env['alifzerocms.application.documents'].sudo().search([('application_id', '=', application.id)])
        docargs = {
            'application_ids':application or False,
            'matric_education': matric_education,
            'inter_education': inter_education,
            'program_preferences_ordered': program_preferences_ordered or False,
            'application_documents': application_documents or False,
            'today': date.today() or False,
        }
        return docargs
