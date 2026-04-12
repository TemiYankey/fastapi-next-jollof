# Supabase Email Templates

These templates are designed to be copied into your Supabase Dashboard for authentication emails.

## How to Use

1. Go to your Supabase Dashboard
2. Navigate to **Authentication** → **Email Templates**
3. For each template type, copy the HTML content from the corresponding file
4. Paste it into the Supabase email template editor
5. Update the **Subject** line as indicated in each file

## Template Variables

Supabase uses these variables in email templates:

| Variable | Description |
|----------|-------------|
| `{{ .ConfirmationURL }}` | Email confirmation link |
| `{{ .Token }}` | OTP token (6 digits) |
| `{{ .TokenHash }}` | Hashed token for magic links |
| `{{ .SiteURL }}` | Your site URL |
| `{{ .RedirectTo }}` | Redirect URL after action |
| `{{ .Email }}` | User's email address |

## Available Templates

- **confirm_email.html** - Email confirmation for new signups
- **magic_link.html** - Passwordless login magic link
- **reset_password.html** - Password reset link
- **change_email.html** - Email change confirmation
- **invite_user.html** - Team/organization invite

## Customization

Before copying, search and replace these placeholders:

- `YOUR_APP_NAME` - Your application name
- `YOUR_PRIMARY_COLOR` - Your brand color (e.g., `#6366f1`)
- `YOUR_LOGO_URL` - URL to your logo image (optional)

## Tips

1. Test emails after updating templates
2. Keep subject lines short and clear
3. Ensure all links work correctly
4. Check mobile responsiveness
