# Havano Company Registration System

This system allows companies to register through a webform and automatically creates users with company-specific access.

## Features

1. **Webform Registration**: Companies can register through a public webform
2. **Automatic User Creation**: Creates user accounts with company-specific access
3. **Company Isolation**: Users can only access data belonging to their company
4. **Auto-population**: New documents automatically get the company field set
5. **Role-based Permissions**: Custom role with company-specific restrictions

## Setup Instructions

### 1. Install the App
```bash
bench --site your-site install-app havano_company
```

### 2. Access the Webform
The company registration webform is available at:
```
https://your-site.com/company-registration
```

### 3. Configure Email Settings
Ensure your site has email settings configured to send welcome emails to new users.

## How It Works

### Registration Process
1. User fills out the company registration webform
2. System validates username and email uniqueness
3. Creates a new Company record
4. Creates a new User with "Company User Role"
5. Assigns the user to the company
6. Sends welcome email with login credentials

### Company Isolation
- Users with "Company User Role" can only see documents belonging to their company
- New documents automatically get the company field populated
- Permission queries filter data based on company field

### Supported Document Types
The system automatically applies company filtering to these doctypes:
- Company Registration
- User
- Company
- Customer
- Supplier
- Item
- Sales Invoice
- Purchase Invoice
- Quotation
- Sales Order
- Purchase Order
- Stock Entry
- Delivery Note
- Purchase Receipt

## Customization

### Adding New Document Types
To add company filtering to new document types:

1. Add the doctype to the `doctypes_to_permit` list in `setup.py`
2. Ensure the doctype has a company field (company, company_name, or organization)
3. Run the setup function again

### Modifying Permissions
Edit the permissions in `setup.py` to customize what actions company users can perform.

## Troubleshooting

### Common Issues

1. **Email not sending**: Check email settings in System Settings
2. **Permission denied**: Ensure the user has the correct role assigned
3. **Company field not auto-populating**: Check that the doctype has a company field

### Logs
Check the error logs for detailed error messages:
- Company Registration errors
- Permission check errors
- Email sending errors

## Security Notes

- Users can only access data belonging to their company
- Administrator and Guest users bypass company restrictions
- All operations are logged for audit purposes
- Password validation ensures secure user creation

## Support

For issues or questions, contact the development team or check the error logs for detailed information.
