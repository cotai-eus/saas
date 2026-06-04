import re


E164_PATTERN = re.compile(r"^\+?[1-9]\d{6,14}$")


class PhoneNumber(str):
    @classmethod
    def validate(cls, value: str) -> "PhoneNumber":
        cleaned = value.strip()
        if not E164_PATTERN.match(cleaned):
            raise ValueError(
                f"Invalid phone number {value!r}. Must be in E.164 format "
                "(e.g. +5511999999999)"
            )
        return cls(cleaned)
