class Researcher:
    def __init__(self, given_name: str = None, surname: str = None, email: str = None, orcid: str = None, has_uncertain_name_order: bool = False):
        self.given_name = given_name
        self.surname = surname
        self.email = email
        self.orcid = orcid
        self.has_uncertain_name_order = has_uncertain_name_order
        self.search_results = []

    def rank_results(self):
        for result in self.search_results:
            result.calculate_internal_rank()

    def sort_results(self):
        self.search_results = sorted(self.search_results)

    def print_search_results(self, verbose: bool = False):
        for result in self.search_results:
            result.print(verbose)