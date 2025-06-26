from email_validator import EmailNotValidError, validate_email

from models.researcher import Researcher
from temp.ror_verification_script import find_org_associated_with_email
from verification_modules.self_contained.self_contained_verification_module import \
    SelfContainedVerificationModule


class RorVerificationModule(SelfContainedVerificationModule):
    def __init__(self, verbose: bool = False, is_active: bool = True):
        super().__init__(verbose, is_active, "ROR")
        self._RESULT_DISPLAY_LIMIT = 5

    def verify(self, researcher: Researcher) -> None:
        if not self.is_active:
            return

        if not researcher.email:
            print(f"{self.data_source_name} researcher email domain "
                  f"verification was attempted but no email was provided, "
                  f"skipping this check.")
            return

        try:
            validated = validate_email(researcher.email)
            print(f"Analyzing email domain '{researcher.email}' using {self.data_source_name}")
            find_org_associated_with_email(validated.normalized,
                                           self._RESULT_DISPLAY_LIMIT)
            print(
                f"{self.data_source_name} researcher email domain "
                f"verification was successful.\n"
            )
        except EmailNotValidError as e:
            print(f"{self.data_source_name} researcher email domain "
                  f"verification was attempted with mail '{researcher.email}' "
                  f"that was invalid. The issue was: {e}.")
