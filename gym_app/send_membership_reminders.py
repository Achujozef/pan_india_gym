from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from gym_app.models import AssignTrainer

class Command(BaseCommand):
    help = 'Send membership expiration reminders for past due dates'

    def handle(self, *args, **options):
        # Get the AssignTrainer instances with past due exp_date
        past_due_assignments = AssignTrainer.objects.filter(exp_date__lt=timezone.now().date() - timedelta(days=3))

        for assignment in past_due_assignments:
            subject = 'Membership Expiration Reminder'
            message = f"Hi {assignment.member.user.username}, your membership has expired..."
            from_email = 'midhunkbalpha@gmail.com'
            recipient_list = [assignment.member.user.email]
            send_mail(subject, message, from_email, recipient_list)

        self.stdout.write(self.style.SUCCESS('Membership expiration reminders sent.'))
