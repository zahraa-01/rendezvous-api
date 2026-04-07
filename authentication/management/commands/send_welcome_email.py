from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Send a welcome email to test email delivery'

    def add_arguments(self, parser):
        parser.add_argument('recipient', type=str, help='Email address to send the welcome email to')

    def handle(self, *args, **options):
        recipient = options['recipient']

        self.stdout.write(f'Email backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'From address:  {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'SendGrid:      {"enabled" if getattr(settings, "USE_SENDGRID", False) else "disabled (console fallback)"}')
        self.stdout.write(f'Sending to:    {recipient}')
        self.stdout.write('')

        # Same welcome email as registration
        plain_body = (
            f'Welcome to Rendezvous, zahraakarim!\n\n'
            'Thanks for joining Rendezvous - where every place has a story, told by the people who know it best.\n\n'
            'Locals, travellers, explorers - they all have somewhere special. A hidden courtyard, a rooftop with a view, a café that feels like home. Rendezvous is where these places live.'
            'Discover somewhere new, share somewhere meaningful, and plan your next rendezvous with the people who matter most.\n\n'
            'See you out there.'
        )

        email = EmailMultiAlternatives(
            subject='Welcome to Rendezvous!',
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        # No HTML attachment for cleaner console demo

        try:
            email.send()
            self.stdout.write(self.style.SUCCESS(f'Welcome email sent successfully to {recipient}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send welcome email: {e}'))
