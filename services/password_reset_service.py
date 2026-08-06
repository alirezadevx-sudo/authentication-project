import resend
from services.service_setting import service_setting


def send_password_reset_email(email: str, token: str):

    resend.api_key = service_setting.RESEND_API_KEY

    html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
            </head>
            <body>
                <div class="container">
                    <h2>Password Reset Email</h2>
                    <p>Please take your token using this link:</p>
                    <p>This link expires in 1 hour.</p>
                    <p>Your Password Reset token: <code>{token}</code></p>
                </div>
            </body>
            </html>
            """

    
    r = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": email,
        "subject": "Password Reset Request",
        "html": html_content
    })