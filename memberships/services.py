from memberships.models import Membership


def get_active_membership(user, organization):
    membership = Membership.objects.filter(
        user=user,
        organization=organization,
        status=Membership.Status.ACTIVE
    ).first()

    return membership

def has_permission(user, organization, action):
    membership = get_active_membership(user, organization)
    if not membership:
        return False

    if action == "invite_member":
        return membership.role in [
            Membership.Role.OWNER,
            Membership.Role.ADMIN                     
        ]

    elif action == "delete_organization":
        return membership.role == Membership.Role.OWNER

    return False

def invite_member(user, organization, invited_by, role):
    action = "invite_member"
    if role not in Membership.Role.values:
        return {
            "success": False,
            "message": "Role does not exist."
        }

    if not has_permission(invited_by, organization, action):
        return {
            "success": False,
            "message": "Inadequate permission to invite."
        }

    inviter = get_active_membership(invited_by, organization)

    if inviter.role == Membership.Role.ADMIN and (role == Membership.Role.OWNER or role == Membership.Role.ADMIN) :
        return {
            "success": False,
            "message": "Inadequate permissions."
        }
    
    membership = Membership.objects.filter(
        user=user,
        organization=organization
    ).first()

    if not membership:
        membership = Membership.objects.create(
            user = user,
            organization = organization,
            invited_by = invited_by,
            role = role
        )
            
    else:
        if membership.status == Membership.Status.REMOVED:
            membership.status = Membership.Status.INVITED
            membership.role = role
            membership.invited_by = invited_by
            membership.save()
        else :
            return {
                "success" : False,
                "message" : "User is already invited or is an active member."
            }
    return {
        "success": True,
        "message": "Invitation created successfully.",
        "membership": membership
    }