from chats.models import ChatGroup, Message
from django.contrib.auth import get_user_model
from model_mommy import mommy
from rest_framework.test import APITestCase

from chats.chat_client import ChatTestApiClient

User = get_user_model()


class E2ETestCase(APITestCase):
    def setUp(self):
        self.superuser = mommy.make(User, username="dev", is_superuser=True)
        self.superuser.set_password("dev")
        self.superuser.save()

    def test_end_to_end(self):
        # Test 1: Login as Superuser
        superuser_client = ChatTestApiClient("dev", "dev")
        # Loggin in
        self.assertIsNone(superuser_client._login, None)
        superuser_client.login()
        self.assertIsNotNone(superuser_client._login, None)
        # Test 2: User Creation as SuperUser
        current_users = User.objects.count()
        self.assertEqual(current_users, 1)
        create_user_response = superuser_client.create_user("nondev")
        self.assertEqual(create_user_response.status_code, 201)
        current_users = User.objects.count()
        self.assertEqual(current_users, 2)

        # Test 3: Login for normal user
        non_superuser = User.objects.get(username="nondev")
        self.assertEqual(non_superuser.is_superuser, False)
        non_superuser_client = ChatTestApiClient("nondev", "P@ssw0rd")
        self.assertIsNone(non_superuser_client._login, None)
        non_superuser_client.login()
        self.assertIsNotNone(non_superuser_client._login, None)

        # Test 4: User creation should not be possible for Normal user
        current_users = User.objects.count()
        self.assertEqual(current_users, 2)
        create_user_response = non_superuser_client.create_user("nondev1")
        self.assertEqual(create_user_response.status_code, 401)
        current_users = User.objects.count()
        self.assertEqual(current_users, 2)

        # Test 5: Edit user for superuser
        self.assertEqual(non_superuser.first_name, "Rishikesh")
        update_user_response = superuser_client.update_user("nondev", "RishikeshNew")
        self.assertEqual(update_user_response.status_code, 200)
        non_superuser = User.objects.get(username="nondev")
        self.assertEqual(non_superuser.first_name, "RishikeshNew")

        # Test 6: Get Users for all users
        all_user_counts = User.objects.count()
        all_users_for_superuser = superuser_client.get_user()
        self.assertEqual(len(all_users_for_superuser.json()), all_user_counts)
        all_users_for_nonsuperuser = non_superuser_client.get_user()
        self.assertEqual(len(all_users_for_nonsuperuser.json()), all_user_counts)

        # Test 6: Create/update groups for all users
        all_groups = ChatGroup.objects.count()
        self.assertEqual(all_groups, 0)
        group_creation_with_superuser = superuser_client.create_chat_group("TestGroup1")
        self.assertEqual(group_creation_with_superuser.status_code, 201)
        all_groups = ChatGroup.objects.count()
        self.assertEqual(all_groups, 1)
        group = ChatGroup.objects.get(name="TestGroup1")
        group_update_with_superuser = superuser_client.update_chat_group(
            group.pk, "TestGroup1_updated"
        )
        self.assertEqual(group_update_with_superuser.status_code, 200)
        # no of groups remain same
        all_groups = ChatGroup.objects.count()
        self.assertEqual(all_groups, 1)
        # group name updated
        group = ChatGroup.objects.get(name="TestGroup1_updated")

        group_creation_with_non_superuser = non_superuser_client.create_chat_group(
            "TestGroup2"
        )
        self.assertEqual(group_creation_with_non_superuser.status_code, 201)
        all_groups = ChatGroup.objects.count()
        self.assertEqual(all_groups, 2)
        group = ChatGroup.objects.get(name="TestGroup2")
        group_update_with_non_superuser = non_superuser_client.update_chat_group(
            group.pk, "TestGroup2_updated"
        )
        self.assertEqual(group_update_with_non_superuser.status_code, 200)
        # no of groups remain same
        all_groups = ChatGroup.objects.count()
        self.assertEqual(all_groups, 2)
        # group name updated
        group = ChatGroup.objects.get(name="TestGroup2_updated")

        # Test 7: Adding members to group by any user
        # adding a 3rd user for future case
        superuser_client.create_user("nondev2")
        all_user_counts = User.objects.count()
        self.assertEqual(all_user_counts, 3)
        group1 = ChatGroup.objects.get(name="TestGroup1_updated")
        group2 = ChatGroup.objects.get(name="TestGroup2_updated")
        self.assertEqual(group1.members.count(), 1)  # 1 owner of the group by default
        self.assertEqual(group2.members.count(), 1)  # 1 owner of the group by default
        adding_member_superuser = superuser_client.add_members(
            group1.pk, ["nondev", "nondev2"]
        )
        adding_member_non_superuser = non_superuser_client.add_members(
            group2.pk, ["nondev2"]
        )
        self.assertEqual(adding_member_non_superuser.status_code, 200)
        self.assertEqual(adding_member_superuser.status_code, 200)
        self.assertEqual(
            group1.members.count(), 3
        )  # 2 new + 1 owner of the group by default
        self.assertEqual(
            group2.members.count(), 2
        )  # 1 new + 1 owner of the group by default
        # Test 8: Sending message in group by members:
        non_superuser_client2 = ChatTestApiClient("nondev2", "P@ssw0rd")
        non_superuser_client2.login()

        message1_group1_user1 = superuser_client.post_message("Hello! Admin", group1.pk)
        message1_group1_user2 = non_superuser_client.post_message(
            "Hello! nondev", group1.pk
        )
        message1_group1_user3 = non_superuser_client2.post_message(
            "Hello! nondev2", group1.pk
        )

        message2_group2_user1 = superuser_client.post_message("Hello! Admin", group2.pk)
        message2_group2_user2 = non_superuser_client.post_message(
            "Hello! nondev", group2.pk
        )
        message2_group2_user3 = non_superuser_client2.post_message(
            "Hello! nondev2", group2.pk
        )

        self.assertEqual(message1_group1_user1.status_code, 201)
        self.assertEqual(message1_group1_user2.status_code, 201)
        self.assertEqual(message1_group1_user3.status_code, 201)
        self.assertEqual(
            message2_group2_user1.status_code, 401
        )  # This is not allowed as admin user is not part of group2
        self.assertEqual(message2_group2_user2.status_code, 201)
        self.assertEqual(message2_group2_user3.status_code, 201)

        # Test 9: Liking/Unliking messages
        # Any user can like/dislike/heart or remove status of any message by any user
        message_obj = Message.objects.first()
        current_likes = superuser_client.get_all_likes_on_message(message_obj.pk)
        self.assertEqual(current_likes.status_code, 200)
        self.assertEqual(current_likes.data, {})

        like_message_user1 = superuser_client.like_message(message_obj.pk)
        like_message_user2 = non_superuser_client.like_message(message_obj.pk)
        like_message_user3 = non_superuser_client2.like_message(message_obj.pk)
        current_likes = superuser_client.get_all_likes_on_message(message_obj.pk)
        self.assertEqual(current_likes.status_code, 200)
        self.assertEqual(
            current_likes.json(),
            {
                "data": [
                    {"id": 1, "message": 1, "owner": 1, "status": "like"},
                    {"id": 2, "message": 1, "owner": 2, "status": "like"},
                    {"id": 3, "message": 1, "owner": 3, "status": "like"},
                ]
            },
        )
