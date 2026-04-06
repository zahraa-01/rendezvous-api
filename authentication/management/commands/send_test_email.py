from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send a test email to verify the configured email backend'

    def add_arguments(self, parser):
        parser.add_argument('recipient', type=str, help='Email address to send the test email to')

    def handle(self, *args, **options):
        recipient = options['recipient']

        self.stdout.write(f'Email backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'From address:  {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'SendGrid:      {"enabled" if settings.USE_SENDGRID else "disabled (console fallback)"}')
        self.stdout.write(f'Sending to:    {recipient}')
        self.stdout.write('')

        email = EmailMessage(
            subject='Rendezvous — Test Email',
            body=(
                'This is a test email from Rendezvous.\n\n'
                'If you are reading this in your inbox, SendGrid SMTP delivery is working correctly.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )

        try:
            email.send()
            self.stdout.write(self.style.SUCCESS(f'Email sent successfully to {recipient}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))
