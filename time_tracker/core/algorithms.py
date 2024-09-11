from datetime import timedelta

def allocate_time(goals, free_time_slots):
    """
    Allocates time for a list of goals based on priority, estimated time, and available free time slots.
    
    :param goals: List of Goal objects.
    :param free_time_slots: List of dictionaries with 'start' and 'end' as datetime objects.
    :return: List of dictionaries with goal title, start, and end time.
    """

    # Sort goals by priority (ascending) and due date (ascending)
    goals = sorted(goals, key=lambda g: (g.priority, g.due_date))

    allocated_time = []

    for goal in goals:
        goal_time_remaining = timedelta(minutes=goal.estimated_time)

        for slot in free_time_slots:
            slot_duration = slot['end'] - slot['start']

            if slot_duration >= goal_time_remaining:
                # Allocate entire goal time within this slot
                start_time = slot['start']
                end_time = start_time + goal_time_remaining
                allocated_time.append({
                    'goal': goal.title,
                    'start': start_time,
                    'end': end_time
                })

                # Update the slot start time
                slot['start'] = end_time
                break

            elif slot_duration > timedelta(minutes=0):
                # Partially allocate time within this slot
                allocated_time.append({
                    'goal': goal.title,
                    'start': slot['start'],
                    'end': slot['end']
                })

                goal_time_remaining -= slot_duration
                slot['start'] = slot['end']

    return allocated_time
