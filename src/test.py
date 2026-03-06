import unittest

from src.exceptions import CreditCardException, UsernameException
from src.main import MiniVenmo, User
from src.services import ActiviesService


class TestUser(unittest.TestCase):
    def test_user_should_be_created_with_a_valid_name(self):
        valid_name = "Danilo"

        user = User(username=valid_name)

        assert user.username == "Danilo"

    def test_user_creation_should_raise_exception_when_invalid_username(self):
        invalid_name = "Invalid name"
        with self.assertRaises(UsernameException):
            User(username=invalid_name)


class TestUserPayments(unittest.TestCase):
    def test_user_when_pay_with_enough_money_should_use_balance(self):
        user = User(username="Danilo")
        user.add_to_balance(amount=10.0)

        target = User(username="Diego")

        user.pay(target=target, amount=2.0, note="Dummy")

        assert user.balance == 8

    def test_user_when_pay_with_not_enough_money_should_use_credit_card(self):
        user = User(username="Danilo")
        user.add_to_balance(amount=10.0)
        user.add_credit_card(credit_card_number="4111111111111111")

        target = User(username="Diego")
        user.add_credit_card(credit_card_number="4242424242424242")

        user.pay(target=target, amount=12.0, note="Dummy")

        assert user.balance == 10.0

    def test_user_cannot_pay_with_credit_card_if_not_set(self):
        user = User(username="Danilo")
        user.add_to_balance(amount=10.0)

        target = User(username="Diego")

        with self.assertRaises(CreditCardException):
            user.pay(target=target, amount=12.0, note="Dummy")

        assert user.balance == 10


class TestUserPaymentActivities(unittest.TestCase):
    def setUp(self):
        ActiviesService._db = {}

    def test_user_retrieve_activity_should_show_payment_activities(self):
        user_1 = User(username="Danilo")
        user_1.add_to_balance(amount=10.0)

        user_2 = User(username="Diego")
        user_2.add_to_balance(amount=3.0)

        user_1.pay(target=user_2, amount=2.0, note="Coffee")
        user_2.pay(target=user_1, amount=3.0, note="Chocolat")

        activities = user_1.retrieve_activity()

        assert activities[0] == "Danilo paid Diego $2.00 for Coffee"
        assert activities[1] == "Diego paid Danilo $3.00 for Chocolat"


class TestUserFriendShipActivities(unittest.TestCase):
    def setUp(self):
        ActiviesService._db = {}

    def test_user_retrieve_activity_should_show_friendship_activities(self):
        user = User(username="Danilo")
        friend = User(username="Diego")

        user.add_friend(new_friend=friend)

        activities = user.retrieve_activity()

        assert activities[0] == "Danilo added Diego as a new friend"


class TestMiniVenmoRun(unittest.TestCase):
    def setUp(self):
        ActiviesService._db = {}

    def test_minivenmo_run(self):
        venmo = MiniVenmo()

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

        assert bobby.balance == 5.00
        assert carol.balance == 10.00

        bobby.pay(target=carol, amount=5.00, note="Coffee")
        assert bobby.balance == 0.00
        assert carol.balance == 15.00

        carol.pay(target=bobby, amount=15.00, note="Lunch")
        assert carol.balance == 0.00
        assert bobby.balance == 15.00

        feed = bobby.retrieve_activity()
        assert feed[0] == "Bobby paid Carol $5.00 for Coffee"
        assert feed[1] == "Carol paid Bobby $15.00 for Lunch"

        venmo.render_feed(feed)

        def cb():
            venmo.render_feed(feed)

        bobby.add_friend(new_friend=carol, callback=cb)
        assert feed[0] == "Bobby paid Carol $5.00 for Coffee"
        assert feed[1] == "Carol paid Bobby $15.00 for Lunch"
        assert feed[2] == "Bobby added Carol as a new friend"
