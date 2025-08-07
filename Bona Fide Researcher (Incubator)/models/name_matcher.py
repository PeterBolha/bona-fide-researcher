import re

from rapidfuzz import fuzz


class NameMatcher:
    def __init__(self, uncertain_name_order: bool = False, match_threshold: float = 65):
        self.uncertain_name_order = uncertain_name_order
        self.match_threshold = match_threshold
        self._NAME_INITIAL_REGEX = re.compile(r"^[^.]\.?$")

    def get_name_match_ratio(self, candidate_given_name: str, candidate_surname: str, target_given_name: str, target_surname: str) -> float:
        if not candidate_given_name or not candidate_surname or not target_given_name or not target_surname:
            return 0

        combined_max_match_ratio = 0

        given_name_match_ratio = fuzz.ratio(candidate_given_name, target_given_name)
        surname_match_ratio = fuzz.ratio(candidate_surname, target_surname)

        combined_max_match_ratio = max(given_name_match_ratio + surname_match_ratio, combined_max_match_ratio)

        # Handle initials only - give at least minimum match threshold
        is_name_initial = re.match(self._NAME_INITIAL_REGEX, candidate_given_name)

        if is_name_initial and candidate_given_name and target_given_name:
            if candidate_given_name[0] == target_given_name[0]:
                given_name_match_ratio = self.match_threshold
                combined_max_match_ratio = max(given_name_match_ratio + surname_match_ratio, combined_max_match_ratio)

        if self.uncertain_name_order:
            given_name_match_ratio = fuzz.ratio(candidate_given_name, target_surname)
            surname_match_ratio = fuzz.ratio(candidate_surname, target_given_name)

            combined_max_match_ratio = max(given_name_match_ratio + surname_match_ratio, combined_max_match_ratio)

            if is_name_initial and candidate_given_name and target_surname:
                if candidate_given_name[0] == target_surname[0]:
                    given_name_match_ratio = self.match_threshold
                    combined_max_match_ratio = max(given_name_match_ratio + surname_match_ratio, combined_max_match_ratio)

        return combined_max_match_ratio

