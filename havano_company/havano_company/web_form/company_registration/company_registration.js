frappe.ready(function() {
	// Initialize form validation
	init_form_validation();
	
	// Setup form submission
	setup_form_submission();
	
	// Setup field validations
	setup_field_validations();
});

function init_form_validation() {
	// Add CSS for error styling
	$('<style>')
		.prop('type', 'text/css')
		.html(`
			.error {
				border-color: #e74c3c !important;
				box-shadow: 0 0 0 2px rgba(231, 76, 60, 0.2) !important;
			}
			.field-error {
				color: #e74c3c;
				font-size: 12px;
				margin-top: 5px;
			}
		`)
		.appendTo('head');
}

function setup_form_submission() {
	// Override the default form submission
	$('.web-form').on('submit', function(e) {
		e.preventDefault();
		
		if (validate_form()) {
			submit_form();
		}
	});
	
	// Handle button click
	$('.btn-primary').on('click', function(e) {
		e.preventDefault();
		
		if (validate_form()) {
			submit_form();
		}
	});
}

function submit_form() {
	var submit_btn = $('.btn-primary');
	var original_text = submit_btn.html();
	
	// Show loading state
	submit_btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> ' + __('Creating Account...'));
	
	// Get form data
	var form_data = get_form_data();
	
	// Set doctype status to submitted
	form_data.docstatus = 1;
	
	// Submit using Frappe's webform accept API
	frappe.call({
		method: 'frappe.website.doctype.web_form.web_form.accept',
		args: {
			web_form: 'company-registration',
			data: JSON.stringify(form_data)
		},
		callback: function(r) {
			if (r.message) {
				// Success - redirect to success page
				window.location.href = '/company-registration?success=1';
			} else {
				// Error
				submit_btn.prop('disabled', false).html(original_text);
				frappe.msgprint(__('Registration failed. Please try again.'));
			}
		},
		error: function(r) {
			submit_btn.prop('disabled', false).html(original_text);
			frappe.msgprint(__('Registration failed. Please try again.'));
		}
	});
}

function validate_form() {
	var is_valid = true;
	var errors = [];
	
	// Clear previous errors
	$('.field-error').remove();
	$('.form-control').removeClass('error');
	
	// Get form values
	var form_data = get_form_data();
	
	// Validate required fields
	var required_fields = ['full_name', 'email', 'organization_name', 'username', 'password', 'confirm_password'];
	required_fields.forEach(function(fieldname) {
		if (!form_data[fieldname] || form_data[fieldname].trim() === '') {
			show_field_error(fieldname, __('This field is required'));
			is_valid = false;
		}
	});
	
	// Validate password
	if (form_data.password && form_data.password.length < 6) {
		show_field_error('password', __('Password must be at least 6 characters long'));
		is_valid = false;
	}
	
	// Validate password confirmation
	if (form_data.password !== form_data.confirm_password) {
		show_field_error('confirm_password', __('Passwords do not match'));
		is_valid = false;
	}
	
	// Validate company name
	if (form_data.organization_name && form_data.organization_name.length < 3) {
		show_field_error('organization_name', __('Company name must be at least 3 characters long'));
		is_valid = false;
	}
	
	// Validate email format
	if (form_data.email && !is_valid_email(form_data.email)) {
		show_field_error('email', __('Please enter a valid email address'));
		is_valid = false;
	}
	
	// Validate username format
	if (form_data.username && !is_valid_username(form_data.username)) {
		show_field_error('username', __('Username can only contain letters, numbers, and underscores'));
		is_valid = false;
	}
	
	return is_valid;
}

function get_form_data() {
	var data = {};
	$('.web-form [data-fieldname]').each(function() {
		var fieldname = $(this).data('fieldname');
		var value = $(this).val();
		data[fieldname] = value;
	});
	return data;
}

function show_field_error(fieldname, message) {
	var field = $('[data-fieldname="' + fieldname + '"]');
	field.addClass('error');
	
	var error_div = $('<div class="field-error">' + message + '</div>');
	field.after(error_div);
}

function is_valid_email(email) {
	var email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
	return email_regex.test(email);
}

function is_valid_username(username) {
	var username_regex = /^[a-zA-Z0-9_]+$/;
	return username_regex.test(username);
}


function setup_field_validations() {
	// Real-time validation for password
	$('[data-fieldname="password"]').on('blur', function() {
		var password = $(this).val();
		if (password && password.length < 6) {
			show_field_error('password', __('Password must be at least 6 characters long'));
		} else {
			clear_field_error('password');
		}
	});
	
	// Real-time validation for password confirmation
	$('[data-fieldname="confirm_password"]').on('blur', function() {
		var password = $('[data-fieldname="password"]').val();
		var confirm_password = $(this).val();
		
		if (confirm_password && password !== confirm_password) {
			show_field_error('confirm_password', __('Passwords do not match'));
		} else {
			clear_field_error('confirm_password');
		}
	});
	
	// Real-time validation for company name
	$('[data-fieldname="organization_name"]').on('blur', function() {
		var company_name = $(this).val();
		if (company_name && company_name.length < 3) {
			show_field_error('organization_name', __('Company name must be at least 3 characters long'));
		} else {
			clear_field_error('organization_name');
		}
	});
	
	// Real-time validation for email
	$('[data-fieldname="email"]').on('blur', function() {
		var email = $(this).val();
		if (email && !is_valid_email(email)) {
			show_field_error('email', __('Please enter a valid email address'));
		} else {
			clear_field_error('email');
		}
	});
	
	// Real-time validation for username
	$('[data-fieldname="username"]').on('blur', function() {
		var username = $(this).val();
		if (username && !is_valid_username(username)) {
			show_field_error('username', __('Username can only contain letters, numbers, and underscores'));
		} else {
			clear_field_error('username');
		}
	});
}

function clear_field_error(fieldname) {
	var field = $('[data-fieldname="' + fieldname + '"]');
	field.removeClass('error');
	field.siblings('.field-error').remove();
}

// Show success message if redirected from successful submission
$(document).ready(function() {
	if (window.location.search.includes('success=1')) {
		frappe.msgprint({
			title: __('Registration Successful!'),
			message: __('Your account has been created successfully. Please check your email for login credentials.'),
			indicator: 'green'
		});
	}
});