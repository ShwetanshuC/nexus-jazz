from django.shortcuts import render
from .models import TeamMember, Department
from collections import defaultdict


def team(request):
    members = TeamMember.objects.filter(is_active=True).select_related("department").order_by("sort_order", "name")
    departments = Department.objects.all().order_by("sort_order", "name")

    grouped = defaultdict(list)
    ungrouped = []
    for member in members:
        if member.department:
            grouped[member.department].append(member)
        else:
            ungrouped.append(member)

    # Build ordered list of (department, members) tuples
    department_groups = [(dept, grouped[dept]) for dept in departments if grouped[dept]]
    if ungrouped:
        department_groups.append((None, ungrouped))

    context = {
        "department_groups": department_groups,
        "all_members": members,
    }
    return render(request, "team/team.html", context)
