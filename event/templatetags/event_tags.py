from django import template

from ..models import Event

register = template.Library()


@register.inclusion_tag('event/event_tag_large.html', takes_context=True)
def render_event_large(context, event):
    # Get group info
    event_groups = list(event.eventgroup_set.all())
    group1 = event_groups[0]
    group2 = None
    if event.numGroups == 2:
        group2 = event_groups[1]

    # First group info
    group1_participants = group1.get_registered_participants_accounts()
    group1_filled_count = group1_participants.count()
    group1_filled_percentage = round(float(group1_filled_count) / event.maxParticipantsInGroup * 100)
    group1_can_join = False

    # Second group info
    group2_filled_percentage = 0
    group2_can_join = False
    if event.numGroups == 2:
        group2_participants = group2.get_registered_participants_accounts()
        group2_filled_count = group2_participants.count()
        group2_filled_percentage = round(float(group2_filled_count) / event.maxParticipantsInGroup * 100)

    current_user = context.request.user

    # Check if user can join each group and leave event
    if current_user.is_authenticated and current_user is not None:
        is_authenticated = True
        try:
            group1_can_join = group1.can_user_register(current_user)
        except Exception:
            group1_can_join = False

        if event.numGroups == 2:
            try:
                group2_can_join = group2.can_user_register(current_user)
            except Exception:
                group2_can_join = False
    else:
        is_authenticated = False
        group1_can_join = True
        group2_can_join = True

    context = {
        'event': event,
        'group1': group1,
        'group2': group2,
        'group1_filled_percentage': group1_filled_percentage,
        'group2_filled_percentage': group2_filled_percentage,
        'group1_can_join': group1_can_join,
        'group2_can_join': group2_can_join,
        'is_authenticated': is_authenticated
    }

    return context


@register.inclusion_tag('event/event_tag_small.html')
def render_event_small(event):
    context = {
        'event': event,
    }

    return context


@register.inclusion_tag('event/event_tag_labels.html', takes_context=True)
def event_labels(context, event):
    current_user = context.request.user

    if current_user.is_authenticated:
        is_registered = event.is_user_registered(current_user)
    else:
        is_registered = False

    is_starting_within_a_day = event.is_starting_within_a_day()
    is_starting_soon = event.is_starting_soon()
    hours_until_start = event.get_hours_until_start()
    is_cancelled = event.stage == Event.CANCELLED

    return {
        'is_registered': is_registered,
        'is_starting_within_a_day': is_starting_within_a_day,
        'is_starting_soon': is_starting_soon,
        'hours_until_start': hours_until_start,
        'is_cancelled': is_cancelled,
        'is_hidden': event.hidden,
        'is_promoted': event.promoted
    }


@register.inclusion_tag('event/event_tag_labels_small.html', takes_context=True)
def event_labels_small(context, event):
    current_user = context.request.user

    if current_user.is_authenticated:
        is_registered = event.is_user_registered(current_user)
    else:
        is_registered = False

    is_starting_within_a_day = event.is_starting_within_a_day()
    is_starting_soon = event.is_starting_soon()
    hours_until_start = event.get_hours_until_start()
    is_cancelled = event.stage == Event.CANCELLED

    return {
        'is_registered': is_registered,
        'is_starting_within_a_day': is_starting_within_a_day,
        'is_starting_soon': is_starting_soon,
        'hours_until_start': hours_until_start,
        'is_cancelled': is_cancelled,
        'is_hidden': event.hidden,
        'is_promoted': event.promoted
    }
