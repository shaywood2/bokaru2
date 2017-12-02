from django import template
register = template.Library()


@register.inclusion_tag('account/profile_tag.html')
def render_profile(profile):
    return {'profile': profile}
