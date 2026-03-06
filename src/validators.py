from __future__ import annotations

import re
import typing

from src.exceptions import (
    BalanceException,
    CreditCardException,
    PaymentException,
    UsernameException,
)

if typing.TYPE_CHECKING:
    from src.main import User


class UserValidator:
    @staticmethod
    def validate_username(*, username: str):
        is_valid = re.match("^[A-Za-z0-9_\\-]{4,15}$", username)
        if is_valid:
            return

        raise UsernameException("Username not valid.")

    @staticmethod
    def validate_balance(*, balance: float):
        if balance is None:
            raise BalanceException("The balance value can't be None")


class CreditCardValidator:
    @staticmethod
    def validate_credit_card(*, credit_card_number: str):
        if credit_card_number is None:
            raise CreditCardException("The Credit card number can't be none")

        if credit_card_number == "":
            raise CreditCardException("The Credit card number can't be void")

        is_valid = credit_card_number in ["4111111111111111", "4242424242424242"]
        if not is_valid:
            raise CreditCardException("The Credit Card number is not valid.")


class Paymentvalidator:
    # NOTE: We can make it better if we split each validate method in different functions
    @staticmethod
    def validate_payment(
        *,
        user: User,
        target: User,
        amount: float,
    ):
        is_same_user = user.username == target.username
        if is_same_user:
            raise PaymentException("User can not pay themselves")

        is_a_valid_amount = amount >= 0.0
        if not is_a_valid_amount:
            raise PaymentException("The amount need to bigger than 0")
