
{
    'name': 'AlifZeroCMS',
    'version': '15.0.1.0.1',
    'summary': """Core Module for CMS""",
    'description': 'Core Module of Educational Institutes',
    'category': 'alifzerocms',
    'sequence': 1,
    'author': 'Alif Zero',
    'company': 'Alif Zero',
    'website': "https://www.alifzero.com/",
    'depends': ['base', 'mail','hr','website','alifzero_activity'],
    'data': [
        'security/alifzerocms_security.xml',
        'security/ir.model.access.csv',
        
        'data/pre_data.xml',
        # # 'data/alifzerocms.campus.csv',
        # # 'data/alifzerocms.institute.csv',
        # # 'data/alifzerocms.program.csv',
        'data/data.xml',
        #
        #
        'views/res_config_setting_view.xml',
        'views/alifzerocms_menu.xml',
        # 'views/assets.xml',
        'views/sequence.xml',
        # 'views/error_reporting_view.xml',
        'views/base_view.xml',
        'views/campus_view.xml',
        'views/institute_view.xml',
        'views/department_view.xml', # discipline views in department file
        'views/career_view.xml',

        'views/program_view.xml', # Specialization views in Program file
        'views/term_view.xml', # Session views in Term File
        #
        'views/course_view.xml',
        'views/course_history_view.xml',
        'views/study_scheme_view.xml',
        #
        'views/student_view.xml',
        'views/student_history_view.xml',
        'views/faculty_staff_view.xml',
        'views/public_holidays_view.xml',

        'views/transcript_history_view.xml',

        'wizard/change_student_state_view.xml',
        'wizard/student_comments_view.xml',
        'wizard/create_user.xml',
        'wizard/change_reg_to_reg.xml',

        # 'reports_opf/report.xml',
        # 'reports_opf/student_provisional_certificate_report.xml',
        # 'reports_opf/student_id_card.xml',

        # 'reports_opf/student_data.xml',

    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}