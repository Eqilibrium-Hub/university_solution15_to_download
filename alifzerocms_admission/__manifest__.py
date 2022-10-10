# -*- coding: utf-8 -*-

{
    'name': "AlifZero Admission",
    'version': '15.0',
    'license': 'LGPL-3',
    'category': 'alifzerocms',
    'sequence': 3,
    'summary': "Admission Module of Educational""",
    'author': 'AlifZero',
    'company': 'Alifzro',
    'website': "http://www.alifzero.com/",
    'depends': ['alifzerocms'],   # 'utm','website_mail','website_partner','mail','website_form','website'
    'data': [
        'security/alifzerocms_admission_security.xml',
        'security/ir.model.access.csv',
        
        
        'views/sequence.xml',
        'menus/alifzerocms_admission_menu.xml',
        
        # 'wizard/application_reject_view.xml',
        # 'wizard/non_subsidized_form_wizard_view.xml',
        # 'wizard/alifzerocms_merit_register_wizard_view.xml',
        # 'wizard/alifzerocms_merit_status_view.xml',
        # 'wizard/alifzerocms_close_register_wizard_view.xml',
        #
        # 'wizard/report/alifzerocms_preference_wizard_view.xml',
        # 'wizard/report/alifzerocms_meritlist_report_wizard_view.xml',
        # 'wizard/report/alifzerocms_merit_interview_wizard_view.xml',
        # 'wizard/report/alifzerocms_final_merit_list_wizard_view.xml',

        'views/admission_register_view.xml',
        'views/alifzerocms_admission_quota.xml',
        'views/alifzerocms_application_view.xml',
        'views/documents_view.xml',
        'views/alifzerocms_merit_list.xml',
        'views/alifzerocms_admission_common.xml',
        'views/student_view.xml',
        'views/test_schedule.xml'

        # 'reports_opf/student_preference_report.xml',
        # 'reports_opf/non_subsidized_form_report.xml',
        # 'reports_opf/student_meritlist_report.xml',
        # 'reports_opf/student_merit_interview_report.xml',
        # 'reports_opf/student_final_merit_list_report.xml',
        # 'reports_opf/report.xml',
        
        
        
        
        
        
        
        #'views/admission_template.xml',
        #'views/portal_templates.xml',
        
        
        
        
        
    



        
    ],
    'demo': [
        # 'demo/admission_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
