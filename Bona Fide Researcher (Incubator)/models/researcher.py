class Researcher:
    def __init__(self, given_name: str = None, surname: str = None, email: str = None, orcid: str = None, has_uncertain_name_order: bool = False):
        self.given_name = given_name
        self.surname = surname
        self.email = email
        self.orcid = orcid
        self.has_uncertain_name_order = has_uncertain_name_order
