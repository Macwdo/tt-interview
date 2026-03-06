from __future__ import annotations

from src.main import User


class ActiviesService:
    _db: dict[str, list[str]] = {}

    def get_activities(self, username: str):
        user_activities = ActiviesService._db.get(username)
        if user_activities is None:
            return []

        return user_activities

    def add_payment_activity(
        self,
        *,
        username: str,
        target_username: str,
        amount: float,
        note: str,
    ):
        activity = f"{username.title()} paid {target_username.title()} ${amount:.2f} for {note}"
        self._add_activity(
            username=username,
            target_username=target_username,
            activity=activity,
        )

    def add_friendship_activity(
        self,
        *,
        username: str,
        new_friend_username: str,
    ):
        activity = (
            f"{username.title()} added {new_friend_username.title()} as a new friend"
        )
        self._add_activity(
            username=username,
            target_username=new_friend_username,
            activity=activity,
        )

    def _add_activity(
        self,
        *,
        username: str,
        target_username: str,
        activity: str,
    ):
        user = ActiviesService._db.get(username)
        if not user:
            ActiviesService._db[username] = []

        target = ActiviesService._db.get(target_username)
        if not target:
            ActiviesService._db[target_username] = []

        ActiviesService._db[username].append(activity)
        ActiviesService._db[target_username].append(activity)


class FriendShipService:
    def __init__(self):
        self._db: list[User] = []

    def get_friends(self) -> list[User]:
        return self._db

    def add_friend(self, new_friend: User):
        pass
