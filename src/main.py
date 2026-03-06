from __future__ import annotations

import uuid
from typing import Callable

from src.exceptions import PaymentException
from src.validators import CreditCardValidator


class Payment:
    def __init__(
        self,
        *,
        amount: float,
        actor: User,
        target: User,
        note: str,
    ):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class User:
    def __init__(
        self,
        *,
        username: str,
    ):
        from src.services import ActiviesService, FriendShipService

        self.username = username
        self.validate_user()

        self.balance = 0.0
        self.credit_card_number = None

        self._activity_service: ActiviesService = ActiviesService()
        self._friendship_service: FriendShipService = FriendShipService()

    def validate_user(self):
        from src.validators import UserValidator

        UserValidator.validate_username(username=self.username)

    def retrieve_activity(self):
        return self._activity_service.get_activities(username=self.username)

    def add_friend(self, *, new_friend: User, callback: Callable | None = None):
        self._friendship_service.add_friend(new_friend=new_friend)
        self._activity_service.add_friendship_activity(
            username=self.username,
            new_friend_username=new_friend.username,
        )
        if not callback:
            return

        callback()

    def add_to_balance(self, *, amount: float):
        self.balance += float(amount)

    def add_credit_card(self, *, credit_card_number: str):
        from src.validators import CreditCardValidator

        CreditCardValidator.validate_credit_card(credit_card_number=credit_card_number)
        self.credit_card_number = credit_card_number

    def pay(
        self,
        *,
        target: User,
        amount: float,
        note: str,
    ) -> Payment:
        from src.validators import Paymentvalidator

        amount = float(amount)
        Paymentvalidator.validate_payment(user=self, target=target, amount=amount)

        has_enough_money = self.balance >= amount
        if has_enough_money:
            self.pay_with_balance(amount=amount)

        else:
            self.pay_with_card(amount=amount)

        # Create Payment
        payment = Payment(amount=amount, actor=self, target=target, note=note)

        # Add to target balance
        target.add_to_balance(amount=amount)

        # Save Activity
        self._activity_service.add_payment_activity(
            username=self.username,
            target_username=target.username,
            amount=amount,
            note=note,
        )

        return payment

    def pay_with_balance(self, *, amount: float):
        self.balance -= amount

    def pay_with_card(self, *, amount: float):
        CreditCardValidator.validate_credit_card(
            credit_card_number=self.credit_card_number
        )

        self._charge_credit_card(credit_card_number=self.credit_card_number)

    def _charge_credit_card(self, *, credit_card_number: str):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(
        self,
        *,
        username: str,
        balance: float,
        credit_card_number: str,
    ) -> User:

        user = User(username=username)
        user.add_to_balance(amount=balance)
        user.add_credit_card(credit_card_number=credit_card_number)

        return user

    def render_feed(self, feed):
        print("Feed Rendered")
        for activity in feed:
            print(f"Activity -> {activity}")

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user(
            username="Bobby",
            balance=5.00,
            credit_card_number="4111111111111111",
        )

        carol = venmo.create_user(
            username="Carol",
            balance=10.00,
            credit_card_number="4242424242424242",
        )

        try:
            # should complete using balance
            bobby.pay(target=carol, amount=5.00, note="Coffee")

            # should complete using card
            carol.pay(target=bobby, amount=15.00, note="Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_activity()
        venmo.render_feed(feed)

        def cb():
            venmo.render_feed(feed)

        bobby.add_friend(new_friend=carol, callback=cb)


if __name__ == "__main__":
    MiniVenmo.run()
