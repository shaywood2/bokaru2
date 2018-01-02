from django import template

from account.models import Account

register = template.Library()


@register.inclusion_tag('account/profile_tag_small.html')
def render_profile(profile):
    return {'profile': profile}


@register.inclusion_tag('account/profile_tag_small.html')
def render_profile_by_user(user):
    profile = Account.objects.get(user=user)

    return {'profile': profile}


@register.inclusion_tag('account/profile_tag_medium.html')
def render_profile_medium_by_user(user):
    profile = Account.objects.get(user=user)

    return {'profile': profile, 'email': user.email}


@register.inclusion_tag('account/profile_tag_large.html')
def render_profile_large(profile, memo):
    memo_content = ''
    if memo:
        memo_content = memo.content

    return {'profile': profile, 'memo': memo_content}
