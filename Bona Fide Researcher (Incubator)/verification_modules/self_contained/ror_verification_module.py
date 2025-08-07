from email_validator import EmailNotValidError, validate_email

from models.researcher import Researcher
from temp.ror_verification_script import find_org_associated_with_email
from verification_modules.self_contained.self_contained_verification_module import \
    (SelfContainedVerificationModule)


class RorVerificationModule(SelfContainedVerificationModule):
    def __init__(self, verbose: bool = False, is_active: bool = True):
        super().__init__(verbose, is_active, "ROR", "email_domain_verification")
        self._RESULT_DISPLAY_LIMIT = 5

    def verify(self, researcher: Researcher) -> dict:
        if not self.is_active:
            return {}

        if not researcher.email:
            no_email_warning_message = (f"{self.data_source_name} researcher "
                                        f"email "
                                        f"domain verification was attempted "
                                        f"but no "
                                        f"email was provided, skipping this "
                                        f"check.")
            print(no_email_warning_message)
            return {"warning": no_email_warning_message}
        try:
            validated = validate_email(researcher.email)
            print(
                f"Analyzing email domain '{researcher.email}' using "
                f"{self.data_source_name}")
            org_info = find_org_associated_with_email(validated.normalized,
                                           self._RESULT_DISPLAY_LIMIT)
            print(
                f"{self.data_source_name} researcher email domain "
                f"verification was successful.\n"
            )
            return org_info
        except EmailNotValidError as e:
            invalid_mail_warning_message = (
                f"{self.data_source_name} researcher email domain "
                f"verification was attempted with mail '{researcher.email}' "
                f"that was invalid. The issue was: {e}.")
            print(invalid_mail_warning_message)
            
            return {"warning": invalid_mail_warning_message}
