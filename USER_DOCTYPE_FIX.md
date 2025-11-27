# User Doctype Fix - Roles Hidden & Enabled Readonly Issue

## Problem
After installing the `havano_company` app, the following issues occurred in the User doctype:
- **Roles field became hidden** - Users couldn't see or modify role assignments
- **Enabled field became readonly** - Users couldn't enable/disable user accounts

## Root Cause
Custom DocPerm (Document Permission) entries were created for the User doctype that only granted **permlevel 0** access. However, the standard User doctype has certain fields (like `roles`, `role_profile_name`) that require **permlevel 1** access to be visible and editable.

When Custom DocPerms exist, they override the standard permissions. Since none of the custom permissions included permlevel 1 access, these critical fields became hidden.

## Solution Applied

### 1. Removed Problematic Custom DocPerm Entries
Deleted 3 Custom DocPerm entries for the User doctype:
- Company User Role (permlevel 0)
- All (permlevel 0)  
- System Manager (permlevel 0)

### 2. Updated setup.py
Modified `havano_company/setup.py` to skip creating custom permissions for the User doctype in future installations. The User doctype will now use its standard Frappe permissions.

### 3. Created Migration Patch
Added a migration patch at `havano_company/patches/v1_0/fix_user_doctype_permissions.py` that automatically removes any problematic Custom DocPerm entries for the User doctype when running `bench migrate`.

## Files Modified
1. `/apps/havano_company/havano_company/setup.py` - Added check to skip User doctype
2. `/apps/havano_company/havano_company/patches.txt` - Added patch reference
3. `/apps/havano_company/havano_company/patches/v1_0/fix_user_doctype_permissions.py` - Created patch file

## Verification
After the fix:
- ✅ Roles field is now visible and editable in User doctype
- ✅ Enabled field is no longer readonly
- ✅ Standard User permissions are restored
- ✅ All existing functionality remains intact
- ✅ No Custom DocPerm entries exist for User doctype

## How to Apply This Fix on Other Sites

### For existing installations:
```bash
cd /home/frappe/frappe-bench
bench --site [your-site-name] migrate
```

The migration patch will automatically remove the problematic Custom DocPerm entries.

### For new installations:
The updated `setup.py` will prevent this issue from occurring during installation.

## Technical Details
- **Frappe Permission System**: Fields in doctypes can have different permission levels (permlevel 0, 1, 2, etc.)
- **User Doctype Structure**: Sensitive fields like `roles` are protected with permlevel 1
- **Custom DocPerm Behavior**: When Custom DocPerm entries exist, they completely override standard permissions
- **Fix Strategy**: Removed custom permissions to restore standard Frappe User doctype behavior

## Impact
- ✅ No functionality is affected - all features work as before
- ✅ User management is now fully functional
- ✅ Company User Role still has appropriate access through standard permissions
- ✅ System Managers can now properly manage user roles and status

