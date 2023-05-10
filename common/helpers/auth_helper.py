from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User, Departments, UserProfiles


def get_tokens_for_user(user, payload={"organisation": "nodata", "utype": "ENDUSER"}):

    refresh = GetModifiedToken.for_user(user, payload)

    return {"refresh": str(refresh), "access": str(refresh.access_token)}


class GetModifiedToken(RefreshToken):
    @classmethod
    def for_user(cls, user, payload):
        token = super().for_user(user)
        token["organisation"] = payload["organisation"]
        token["utype"] = payload["utype"]
        department = payload["organisation"]
        role = "ADMIN"
        permissions = {}
        if payload["utype"] == User.UserTypes.STAFF:
            user_profile = UserProfiles.objects.get(
                status=True,
                user=user,
                is_active=True,
                organisation=user.organisation,
            )
            department = str(user_profile.department.id)
            role = str(user_profile.role.name)
            permissions = user_profile.role.permissions
        token["dept"] = department
        token["role"] = role
        token["permissions"] = permissions
        return token
