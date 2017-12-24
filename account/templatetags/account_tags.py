from django import template

from account.models import Account

register = template.Library()


@register.inclusion_tag('account/profile_tag.html')
def render_profile(profile):
    return {'profile': profile}


@register.inclusion_tag('account/profile_tag.html')
def render_profile_by_user(user):
    profile = Account.objects.get(user=user)

    return {'profile': profile}
