import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_email(
    to: list,
    subject: str,
    template_name: str,
    template_context: dict,
    cc: list = [],
    bcc: list = [],
):
    msg_html = render_to_string(template_name, template_context)
    msg_text = html2text.html2text(msg_html)

    msg = EmailMultiAlternatives(
        subject, msg_text, settings.DEFAULT_FROM_EMAIL, [to], cc=cc, bcc=bcc
    )
    msg.attach_alternative(msg_html, "text/html")
    msg.send()
