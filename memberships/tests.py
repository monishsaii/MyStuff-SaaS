from django.test import TestCase
from accounts.models import User
from memberships.models import Membership
from organizations.models import Organization
from django.utils import timezone
from memberships.services import (
    invite_member,
    has_permission,
    get_active_membership,
) 


class InviteMemberTests(TestCase):
    def setUp(self):

        self.org = Organization.objects.create(
            name = 'myStuff'
        )

        self.owner = User.objects.create_user(
            username = 'monish',
            email = 'monish@example.com',
            first_name = 'monish',
            last_name = 'owner',
            password = '1234'
        )  

        self.admin = User.objects.create_user(
            username = 'admin',
            email = 'admin@example.com',
            first_name = 'ad',
            last_name = 'admin',
            password = '2020'
        )  

        self.manager = User.objects.create_user(
            username = 'min',
            email = 'min@example.com',
            first_name = 'min',
            last_name = 'manager',
            password = '1010'
        )  

        self.membership1 = Membership.objects.create(
            user = self.owner,
            organization = self.org,
            role = Membership.Role.OWNER,
            status = Membership.Status.ACTIVE,
        )

        self.membership2 = Membership.objects.create(
            user = self.admin,
            organization = self.org,
            role = Membership.Role.ADMIN,
            status = Membership.Status.ACTIVE,
        )

        self.membership3 = Membership.objects.create(
            user = self.manager,
            organization = self.org,
            role = Membership.Role.MANAGER,
            status = Membership.Status.ACTIVE,
        )

        self.recipient = User.objects.create_user(
            username = 'max',
            email = 'max@example.com',
            first_name = 'max',
            last_name = 'recipient',
            password = '5678'
        )

    def test_owner_can_invite_member(self):

        result = invite_member(
            self.recipient,
            self.org,
            self.owner, 
            'MEMBER'
        )

        self.assertTrue(
            result["success"], 
            msg = 'The result should be success.'
        )
        
        self.assertTrue(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org,
                role=Membership.Role.MEMBER,
                status=Membership.Status.INVITED
            ).exists()
        )

    def test_manager_cannot_invite_member(self):

        result = invite_member(
            self.recipient,
            self.org,
            self.manager, 
            'MEMBER'
        )

        self.assertFalse(
            result["success"], 
            msg = 'Manager cannot invite members.'
        )

        self.assertFalse(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org,
                role=Membership.Role.MEMBER,
                status=Membership.Status.INVITED
            ).exists()
        )

    def test_admin_can_invite_member(self):
        result = invite_member(
            self.recipient,
            self.org,
            self.admin, 
            'MEMBER'
        )

        self.assertTrue(
            result["success"], 
            msg = 'Admin can invite member.'
        )

        self.assertTrue(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org,
                role=Membership.Role.MEMBER,
                status=Membership.Status.INVITED
            ).exists()
        )

    def test_admin_can_invite_manager(self):
        result = invite_member(
            self.recipient,
            self.org,
            self.admin, 
            'MANAGER'
        )

        self.assertTrue(
            result["success"], 
            msg = 'Admin can invite manager.'
        )

        self.assertTrue(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org,
                role=Membership.Role.MANAGER,
                status=Membership.Status.INVITED
            ).exists()
        )

    def test_admin_cannot_invite_admin(self):
        result = invite_member(
            self.recipient,
            self.org,
            self.admin, 
            'ADMIN'
        )

        self.assertFalse(
            result["success"], 
            msg = 'Admin cannot invite admin.'
        )

        self.assertFalse(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org,
                role=Membership.Role.ADMIN,
                status=Membership.Status.INVITED
            ).exists()
        )

    def test_admin_cannot_invite_owner(self):
        result = invite_member(
            self.recipient,
            self.org,
            self.admin, 
            'OWNER'
        )

        self.assertFalse(
            result["success"], 
            msg = 'Admin cannot invite owner.'
        )

        self.assertFalse(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org,
                role=Membership.Role.OWNER,
                status=Membership.Status.INVITED
            ).exists()
        )

    def test_removed_member_can_be_reinvited(self):
        membership = Membership.objects.create(
            user = self.recipient,
            organization = self.org,
            role = Membership.Role.MEMBER,
            status = Membership.Status.REMOVED
        )
        
        result = invite_member(
            self.recipient,
            self.org,
            self.owner, 
            'MEMBER'
        )

        self.assertTrue(
            result["success"], 
            msg = 'Owner can invite removed members.'
        )

        membership.refresh_from_db()
        
        self.assertEqual(
            membership.status,
            Membership.Status.INVITED
        )

        self.assertEqual(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org
            ).count(), 1
        )

    def test_reinvitation_preserves_original_joined_at(self):
        membership = Membership.objects.create(
            user = self.recipient,
            organization = self.org,
            role = Membership.Role.MEMBER,
            status = Membership.Status.REMOVED,
            joined_at = timezone.now()
        )
        original_joined_at = membership.joined_at

        result = invite_member(
            self.recipient,
            self.org,
            self.owner, 
            'MEMBER'
        )

        self.assertTrue(
            result["success"], 
            msg = 'Owner can invite removed members.'
        )

        membership.refresh_from_db()

        self.assertEqual(
            membership.status,
            Membership.Status.INVITED
        )

        self.assertEqual(
            membership.joined_at,
            original_joined_at
        )

    def test_owner_cannot_invite_into_another_organization(self):

        self.other_org = Organization.objects.create(
            name = 'notmyStuff'
        )

        result = invite_member(
            self.recipient,
            self.other_org,
            self.owner,
            Membership.Role.MEMBER
        )

        self.assertFalse(
            result["success"], 
            msg = 'Owner cannot invite members into another organization.'
        )

        self.assertEqual(
            Membership.objects.filter(
                user = self.recipient,
                organization = self.other_org
            ).count(), 0
        )

    def test_get_active_membership_returns_active_membership(self):
        result = get_active_membership(
            self.owner,
            self.org
        )

        self.assertEqual(
            result,
            self.membership1
        )
    
    def test_get_active_membership_returns_none_for_inactive_membership(self):

        self.membership1.status = Membership.Status.REMOVED
        self.membership1.save()

        result = get_active_membership(self.owner, self.org)

        self.assertIsNone(result)
    
    def test_get_active_membership_returns_none_when_no_membership_exists(self):
        result = get_active_membership(self.recipient, self.org)
        self.assertIsNone(result)
    
    def test_only_owner_can_delete_organization(self):
        result = has_permission(self.owner, self.org, "delete_organization")
        self.assertTrue(
            result,
            msg = 'Authorized.'
        )

        result = has_permission(self.admin, self.org, "delete_organization")
        self.assertFalse(
            result,
            msg = 'Unauthorized.'
        )
    
    def test_unknown_action_is_denied(self):
        result = has_permission(
            self.owner,
            self.org,
            "launch_rocket"
        )

        self.assertFalse(result)
    
    def test_removed_owner_has_no_permissions(self):
        self.membership1.status = Membership.Status.REMOVED
        self.membership1.save()

        result = has_permission(
            self.owner,
            self.org,
            "delete_organization"
        )

        self.assertFalse(result)
    
    def test_owner_has_no_permission_in_another_organization(self):
        other_org = Organization.objects.create(
            name="OtherOrg"
        )

        result = has_permission(
            self.owner,
            other_org,
            "delete_organization"
        )

        self.assertFalse(result)
    
    def test_invite_member_rejects_invalid_role(self):
        result = invite_member(
            self.recipient,
            self.org,
            self.owner,
            "SUPERADMIN"
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Role does not exist.")
    
    def test_removed_owner_cannot_invite_member(self):
        self.membership1.status = Membership.Status.REMOVED
        self.membership1.save()

        result = invite_member(
            self.recipient,
            self.org,
            self.owner,
            Membership.Role.MEMBER
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["message"],
            "Inadequate permission to invite."
        )
    
    def test_duplicate_invitation_is_rejected(self):
        Membership.objects.create(
            user=self.recipient,
            organization=self.org,
            role=Membership.Role.MEMBER,
            status=Membership.Status.INVITED,
            invited_by=self.owner
        )

        result = invite_member(
            self.recipient,
            self.org,
            self.owner,
            Membership.Role.MEMBER
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["message"],
            "User is already invited or is an active member."
        )

        self.assertEqual(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org
            ).count(),
            1
        )

    def test_invitation_rejected_for_active_member(self):
        Membership.objects.create(
            user=self.recipient,
            organization=self.org,
            role=Membership.Role.MEMBER,
            status=Membership.Status.ACTIVE,
            invited_by=self.owner
        )

        result = invite_member(
            self.recipient,
            self.org,
            self.owner,
            Membership.Role.MEMBER
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            result["message"],
            "User is already invited or is an active member."
        )

        self.assertEqual(
            Membership.objects.filter(
                user=self.recipient,
                organization=self.org
            ).count(),
            1
        )

    def test_has_permission_to_invite_by_role(self):
        self.assertTrue(
            has_permission(self.owner, self.org, "invite_member")
        )

        self.assertTrue(
            has_permission(self.admin, self.org, "invite_member")
        )

        self.assertFalse(
            has_permission(self.manager, self.org, "invite_member")
        )

        self.assertFalse(
            has_permission(self.recipient, self.org, "invite_member")
        )