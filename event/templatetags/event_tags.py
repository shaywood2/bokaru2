from django import template
register = template.Library()


@register.inclusion_tag('event/event_tag_large.html')
def render_event_large(event):
    # Get group info
    event_groups = list(event.eventgroup_set.all())
    group1 = event_groups[0]
    group2 = None
    if event.numGroups == 2:
        group2 = event_groups[1]

    # First group info
    group1_participants = group1.get_registered_participants_accounts()
    group1_filled_count = group1_participants.count()
    group1_filled_percentage = float(group1_filled_count) / event.maxParticipantsInGroup * 100

    # Second group info
    group2_filled_percentage = 0
    if event.numGroups == 2:
        group2_participants = group2.get_registered_participants_accounts()
        group2_filled_count = group2_participants.count()
        group2_filled_percentage = float(group2_filled_count) / event.maxParticipantsInGroup * 100

    context = {
        'event': event,
        'group1': group1,
        'group2': group2,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage
    }

    return context


@register.inclusion_tag('event/event_tag_small.html')
def render_event_small(event):
    context = {
        'event': event,
    }

    return context
