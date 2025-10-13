app_name = "havano_company"
app_title = "Havano Company"
app_publisher = "nasirucode"
app_description = "Havano Companyt"
app_email = "akingbolahan12@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "havano_company",
# 		"logo": "/assets/havano_company/logo.png",
# 		"title": "Havano Company",
# 		"route": "/havano_company",
# 		"has_permission": "havano_company.api.permission.has_app_permission"
# 	}
# ]
doc_events = {
    "POS Opening Entry": {
        "after_insert": "havano_pos_integration.api.submit_pos_opening_entry"
    },
    "POS Closing Entry": {
        "after_insert": "havano_pos_integration.api.submit_pos_closing_entry"
    },
    "POS Invoice": {
        "after_insert": "havano_pos_integration.api.submit_pos_invoice"
    }
}
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/havano_company/css/havano_company.css"
# app_include_js = "/assets/havano_company/js/havano_company.js"

# include js, css files in header of web template
# web_include_css = "/assets/havano_company/css/havano_company.css"
# web_include_js = "/assets/havano_company/js/havano_company.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "havano_company/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "havano_company/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "havano_company.utils.jinja_methods",
# 	"filters": "havano_company.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "havano_company.install.before_install"
after_install = "havano_company.setup.after_install"

# Uninstallation
# ------------

# before_uninstall = "havano_company.uninstall.before_uninstall"
# after_uninstall = "havano_company.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "havano_company.utils.before_app_install"
# after_app_install = "havano_company.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "havano_company.utils.before_app_uninstall"
# after_app_uninstall = "havano_company.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "havano_company.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"*": "havano_company.permissions.get_permission_query_conditions",
# }

# has_permission = {
# 	"*": "havano_company.permissions.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"before_insert": "havano_company.utils.set_company_field"
	# },
    # "Company Registration": {
	# 	"before_insert": "havano_company.apis.company.submit_company_registration"
	# }
	# "Company Registration": {
	# 	"validate": "havano_company.havano_company.web_form.company_registration.company_registration.on_submit"
	# }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"havano_company.tasks.all"
# 	],
# 	"daily": [
# 		"havano_company.tasks.daily"
# 	],
# 	"hourly": [
# 		"havano_company.tasks.hourly"
# 	],
# 	"weekly": [
# 		"havano_company.tasks.weekly"
# 	],
# 	"monthly": [
# 		"havano_company.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "havano_company.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "havano_company.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "havano_company.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["havano_company.utils.before_request"]
# after_request = ["havano_company.utils.after_request"]

# Job Events
# ----------
# before_job = ["havano_company.utils.before_job"]
# after_job = ["havano_company.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"havano_company.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

