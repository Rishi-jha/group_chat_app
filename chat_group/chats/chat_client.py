from rest_framework.test import APIClient


class ChatTestApiClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = APIClient()
        self._login = None

    def login(self):
        response = self.client.post(
            "/api/v1/login/",
            data={"username": self.username, "password": self.password},
        )
        auth_token = response.data["access_token"]
        token = f"Bearer {auth_token}"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        self._login = token

    def logout(self):
        self.client.post("/api/v1/logout/")
        self._login = None

    def get_user(self, user_id=""):
        return self.client.get(f"/api/v1/users/{user_id}")

    def create_user(self, username, is_superuser=False):
        data = {
            "username": username,
            "first_name": "Rishikesh",
            "last_name": "Jha",
            "email": "rishi@mail.com",
            "is_superuser": is_superuser,
        }
        response = self.client.post("/api/v1/users/", data=data)
        return response

    def update_user(self, username, first_name):
        data = {"first_name": first_name}

        response = self.client.patch(f"/api/v1/users/{username}", data=data)
        return response

    def get_chat_groups(self, id=""):
        return self.client.get(f"/api/v1/chatgroups/{id}")

    def create_chat_group(self, name):
        data = {
            "name": name,
        }
        response = self.client.post("/api/v1/chatgroups/", data=data)
        return response

    def update_chat_group(self, id, name):
        data = {
            "name": name,
        }
        response = self.client.patch(f"/api/v1/chatgroups/{id}", data=data)
        return response

    def delete_chat_group(self, id):
        response = self.client.delete(f"/api/v1/chatgroups/{id}")
        return response

    def add_members(self, id, usernames):
        data = {"members": usernames}
        response = self.client.post(f"/api/v1/chatgroups/{id}/members/", data=data)
        return response

    def remove_members(self, id, usernames):
        data = {"memebers": usernames}
        response = self.client.delete(f"/api/v1/chatgroups/{id}/members/", data=data)
        return response

    def get_messages(self, group_id):
        response = self.client.get(f"/api/v1/chatgroups/{id}/messages/")
        return response

    def post_message(self, text, group):
        data = {"text": text, "group": group}
        response = self.client.post(f"/api/v1/messages/", data=data)
        return response

    def edit_message(self, id, text):
        data = {
            "text": text,
        }
        response = self.client.patch(f"/api/v1/messages/{id}", data=data)
        return response

    def like_message(self, id, status="like"):
        data = {
            "status": status,
        }
        response = self.client.post(f"/api/v1/messages/{id}/status/", data=data)
        return response

    def update_like_message(self, id, status="like"):
        data = {
            "status": status,
        }
        response = self.client.patch(f"/api/v1/messages/{id}/status/", data=data)
        return response

    def unlike_message(self, id):
        response = self.client.delete(f"/api/v1/messages/{id}/status/")
        return response

    def get_all_likes_on_message(self, id):
        response = self.client.get(f"/api/v1/messages/{id}/status/")
        return response
