# services/email_service.py
import resend
from services.service_setting import service_setting

async def send_email(email: str, token: str):
    try:
        
        resend.api_key = service_setting.RESEND_API_KEY
        
        verification_link = f"http://localhost:8000/api/auth/verification/verify_email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body>
            <div class="container">
                <h2>Welcome! 🎉</h2>
                <p>Thanks for signing up. Please verify your email by clicking the button below:</p>
                <a href="{verification_link}" class="button">Verify Email</a>
                <p>Or copy this link: <a href="{verification_link}">{verification_link}</a></p>
                <p>This link expires in 1 hour.</p>
                <p>Your verification token: <code>{token}</code></p>
            </div>
        </body>
        </html>
        """
        
        r = resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": email,
            "subject": "Verify Your Email Address",
            "html": html_content
        })
        
        return r
        
    except resend.exceptions.ResendError as e:
        raise
    except Exception as e:
        raise