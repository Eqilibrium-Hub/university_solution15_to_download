import pdb
from odoo import fields, models, api, _

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # module_alifzerocms_activity = fields.Boolean(string="Activity")
    # module_alifzerocms_facility = fields.Boolean(string="Facility")
    # module_alifzerocms_parent = fields.Boolean(string="Parent")
    # module_alifzerocms_assignment = fields.Boolean(string="Assignment")
    # module_alifzerocms_classroom = fields.Boolean(string="Classroom")
    module_alifzerocms_academic = fields.Boolean(string="Academic")
    module_alifzerocms_fee = fields.Boolean(string="Fee")
    module_alifzerocms_admission = fields.Boolean(string="Admission")
    module_alifzerocms_registration = fields.Boolean(string="Registration")
    module_alifzerocms_timetable = fields.Boolean(string="Timetable")
    module_alifzerocms_exam = fields.Boolean(string="Exam")
    module_alifzerocms_faculty_portal = fields.Boolean(string="Faculty Portal")
    # module_alifzerocms_library = fields.Boolean(string="Library")
    # module_alifzerocms_attendance = fields.Boolean(string="Attendance")

    pdf_converter = fields.Char(string="PDF Converter", config_parameter='alifzerocms.pdf_converter', default='/usr/bin/unoconv')
    
    current_term = fields.Many2one('alifzerocms.academic.term', config_parameter='alifzerocms.current_term',
                                                string="Current Academic Term", help="Add Current Academic Semester")

    bokeh_server_address = fields.Char(string="Bokeh Server Address", config_parameter='alifzerocms.bokeh_server_address')
    bokeh_secret_key = fields.Char(string="Bokeh Secret Key", config_parameter='alifzerocms.bokeh_secret_key')
    
    #FTP Server details
    ftp_server_address = fields.Char(string="FTP Server Address", config_parameter='alifzerocms.ftp_server_address')
    ftp_server_user = fields.Char(string="FTP Server User", config_parameter='alifzerocms.ftp_server_user')
    ftp_server_password = fields.Char(string="FTP Server Password", config_parameter='alifzerocms.ftp_server_password')
    ftp_server_source = fields.Char(string="Files Path", config_parameter='alifzerocms.ftp_server_source', default = 'ftp/files/')

    # Exam
    repeat_grades_allowed = fields.Char(string="Repeat Grades Allowed", config_parameter='alifzerocms.repeat_grades_allowed', default='F')
    repeat_grades_allowed_time = fields.Char(string="Repeat Time-Gap Allowed", config_parameter='alifzerocms.repeat_grades_allowed_time', default='3')
    x_st_repeat_grades_allowed_time = fields.Char(string="Repeat Time-gap Allowed for X-Final", config_parameter='alifzerocms.x_st_repeat_grades_allowed_time', default='2')

    repeat_grades_allowed_no = fields.Char(string="Repeat Times Allowed", config_parameter='alifzerocms.repeat_grades_allowed_no', default='1')

    failed_grades = fields.Char(string="Failed Grades", config_parameter='alifzerocms.failed_grades', default='F,W')
