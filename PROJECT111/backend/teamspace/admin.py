from django.contrib import admin
from .models import (
    Users, Projects, Skills, UserSkills,
    Teams, TeamMembers, MatchScores,
    Evaluations, Portfolios
)

admin.site.register(Users)
admin.site.register(Projects)
admin.site.register(Skills)
admin.site.register(UserSkills)
admin.site.register(Teams)
admin.site.register(TeamMembers)
admin.site.register(MatchScores)
admin.site.register(Evaluations)
admin.site.register(Portfolios)
