from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_email(to, data, template_name):
    subject = render_to_string('email/' + template_name + '_subject.txt', data)
    text_body = render_to_string('email/' + template_name + '.txt', data)
    html_body = render_to_string('email/' + template_name + '.html', data)

    msg = EmailMultiAlternatives(subject=subject, from_email='no-reply@mg.bokaru.com',
                                 to=[to], body=text_body)
    msg.attach_alternative(html_body, 'text/html')
    msg.send()
