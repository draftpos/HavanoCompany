frappe.ready(function() {
	// Initialize form validation
	init_form_validation();
	
	// Setup form submission
	setup_form_submission();
	
	// Setup field validations
	setup_field_validations();
	
	// Auto-populate user information
	auto_populate_user_info();
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
			.form-control-plaintext {
				background-color: #f8f9fa !important;
				border: 1px solid #dee2e6 !important;
				color: #6c757d !important;
				font-style: italic;
			}
			.form-control-plaintext:focus {
				background-color: #f8f9fa !important;
				border-color: #dee2e6 !important;
				box-shadow: none !important;
			}
		`)
		.appendTo('head');
}

function setup_form_submission() {
	// Override the default form submission
	$('.web-form').on('submit', function(e) {
		if (!validate_form()) {
			e.preventDefault();
			return false;
		}
		
		// Show loading state
		var submit_btn = $('.btn-primary');
		var original_text = submit_btn.html();
		submit_btn.prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> ' + __('Creating Company...'));
		
		// Re-enable button after 10 seconds as fallback
		setTimeout(function() {
			submit_btn.prop('disabled', false).html(original_text);
		}, 10000);
	});
	
	// Handle button click
	$('.btn-primary').on('click', function(e) {
		if (!validate_form()) {
			e.preventDefault();
			return false;
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
	var required_fields = ['full_name', 'email', 'organization_name'];
	required_fields.forEach(function(fieldname) {
		if (!form_data[fieldname] || form_data[fieldname].trim() === '') {
			show_field_error(fieldname, __('This field is required'));
			is_valid = false;
		}
	});
	
	
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



function setup_field_validations() {
	
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
	
}

function clear_field_error(fieldname) {
	var field = $('[data-fieldname="' + fieldname + '"]');
	field.removeClass('error');
	field.siblings('.field-error').remove();
}

function auto_populate_user_info() {
	// Get current user information and populate the form
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'User',
			name: frappe.session.user
		},
		callback: function(r) {
			if (r.message) {
				var user = r.message;
				
				// Populate full name
				var full_name = '';
				if (user.first_name && user.last_name) {
					full_name = user.first_name + ' ' + user.last_name;
				} else if (user.first_name) {
					full_name = user.first_name;
				} else if (user.full_name) {
					full_name = user.full_name;
				} else {
					full_name = user.name;
				}
				
				// Set the values
				$('[data-fieldname="full_name"]').val(full_name);
				$('[data-fieldname="email"]').val(user.email || '');
				$('[data-fieldname="phone"]').val(user.phone || '');
				$('[data-fieldname="status"]').val('Created');
				
				// Make the fields read-only since they're from the logged-in user
				$('[data-fieldname="full_name"]').prop('readonly', true);
				$('[data-fieldname="email"]').prop('readonly', true);
				
				// Add visual indication that these fields are auto-populated
				$('[data-fieldname="full_name"]').addClass('form-control-plaintext');
				$('[data-fieldname="email"]').addClass('form-control-plaintext');
			}
		},
		error: function(err) {
			console.error('Error fetching user information:', err);
		}
	});
}

// Show success message if redirected from successful submission
$(document).ready(function() {
	if (window.location.search.includes('success=1')) {
		frappe.msgprint({
			title: __('Company Created Successfully!'),
			message: __('Company has been created successfully! You now have full access to ERPNext with comprehensive roles.'),
			indicator: 'green'
		});
	}
});