from django import template

from account.models import Account
from event.models import Pick

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


@register.inclusion_tag('account/profile_tag_labels.html', takes_context=True)
def account_labels(context, user):
    current_user = context.request.user

    if current_user.is_authenticated:
        is_match = Pick.objects.is_match(current_user, user)
        is_familiar = Pick.objects.is_familiar(current_user, user)
    else:
        is_match = False
        is_familiar = False

    return {'is_match': is_match, 'is_familiar': is_familiar}
