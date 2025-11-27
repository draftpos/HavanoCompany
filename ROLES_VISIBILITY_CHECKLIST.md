# ✓ Roles Field Visibility - Troubleshooting Checklist

## Backend Status: ✅ ALL FIXED
The backend verification shows:
- ✅ No Custom DocPerm entries interfering with permissions
- ✅ Permlevel 1 permission restored for System Manager
- ✅ Roles field properly configured (permlevel 1, not hidden)
- ✅ Enabled field is not read-only

## If Roles Field Still Not Visible in UI:

### Step 1: Clear Browser Cache (CRITICAL)
The UI may be cached. You MUST do this:

**Chrome/Edge:**
- Press `Ctrl + Shift + R` (Windows/Linux) or `Cmd + Shift + R` (Mac)
- OR: Press `F12` → Right-click refresh button → "Empty Cache and Hard Reload"

**Firefox:**
- Press `Ctrl + Shift + Delete` → Clear "Cache" → Clear Now
- Then reload page with `Ctrl + F5`

### Step 2: Clear Server Cache
```bash
cd /home/frappe/frappe-bench
bench --site buz.havano.cloud clear-cache
bench --site buz.havano.cloud clear-website-cache
```

### Step 3: Verify You're Logged in as System Manager
The roles field requires **System Manager** role to be visible (permlevel 1).

To check your current role:
1. Click your profile picture (top right)
2. Go to "My Settings"
3. Check your roles

If you don't have System Manager role, ask an administrator to assign it.

### Step 4: Log Out and Log Back In
Sometimes the session cache needs to be refreshed:
1. Log out completely
2. Close all browser tabs for this site
3. Log back in
4. Navigate to User list → Open any user

### Step 5: Try Incognito/Private Mode
Open the site in a private/incognito window to rule out browser extensions or persistent cache.

### Step 6: Check What You Should See
When opening a User document as System Manager, you should see:

**User Details Tab:**
- ✅ Enabled (checkbox - should be editable)
- ✅ Email, Name fields
- ✅ Full Name
- ✅ Company field

**Roles & Permissions Tab:**
- ✅ **Role Profile** (dropdown)
- ✅ **Roles Assigned** (table with list of roles)
- ✅ Module access settings

## Verification Command
Run this to verify backend is correct:
```bash
cd /home/frappe/frappe-bench
bench --site buz.havano.cloud execute havano_company.verify_user_fix.verify_user_doctype_fix
```

Should show: "✓ ALL CHECKS PASSED"

## Still Not Working?

### Check User Permission Rules
If you're testing with a specific user that has "Company User Role", verify:
```bash
cd /home/frappe/frappe-bench
bench --site buz.havano.cloud console
```

Then:
```python
import frappe
frappe.connect()

# Check your current user's roles
user = frappe.session.user
user_doc = frappe.get_doc("User", user)
print("Your roles:", [r.role for r in user_doc.roles])

# Verify you have System Manager
has_system_manager = any(r.role == "System Manager" for r in user_doc.roles)
print("Has System Manager:", has_system_manager)

exit()
```

### Check for Client Scripts
If there are custom client scripts hiding fields:
```bash
cd /home/frappe/frappe-bench
bench --site buz.havano.cloud mariadb -e "SELECT name, dt FROM \`tabClient Script\` WHERE dt='User';"
```

If any scripts exist, review them for code that might be hiding the roles field.

## Technical Details

The fix involved:
1. **Removed Custom DocPerm entries** that were overriding standard permissions
2. **Restored permlevel 1 permission** for System Manager role
3. **Updated setup.py** to prevent future interference with User doctype
4. **Created migration patches** to apply fix automatically

The roles field requires **permlevel 1** access because it controls sensitive permissions.
Only users with **System Manager** role can see and edit roles.

