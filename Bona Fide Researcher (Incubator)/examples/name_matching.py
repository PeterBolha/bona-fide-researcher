"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""
from models.name_matcher import NameMatcher

class Person:
    def __init__(self, given_name_accents, surname_accents, given_name_normalized, surname_normalized, nationality):
        self.given_name_accents = given_name_accents
        self.surname_accents = surname_accents
        self.given_name_normalized = given_name_normalized
        self.surname_normalized = surname_normalized
        self.nationality = nationality
        self.initial = given_name_accents[0]

    def __str__(self):
        return f"{self.given_name_accents} {self.surname_accents} ({self.nationality})"

def main():
    match_threshold = 65

    czech = Person("Jiří", "Novák", "Jiri", "Novak", "CZ")
    hungarian = Person("Zoltán", "Szabó", "Zoltan", "Szabo", "HU")
    portuguese = Person("João", "Gonçalves", "Joao", "Goncalves", "PT")

    people = [czech, hungarian, portuguese]

    for person in people:
        name_matcher_certain = NameMatcher(uncertain_name_order=False, match_threshold=match_threshold)
        name_matcher_uncertain = NameMatcher(uncertain_name_order=True, match_threshold=match_threshold)

        exact_match_certain_order = name_matcher_certain.get_name_match_ratio(person.given_name_accents, person.surname_accents, person.given_name_accents, person.surname_accents)
        print(f"Exact match, certain name order: {person.given_name_accents} {person.surname_accents} <-> {person} [MATCH: {int(exact_match_certain_order)}/200]")

        partial_match_certain_order = name_matcher_certain.get_name_match_ratio(
            person.given_name_normalized, person.surname_normalized,
            person.given_name_accents, person.surname_accents)
        print(
            f"Partial match, certain name order: {person.given_name_normalized} {person.surname_normalized} <-> {person} [MATCH: {int(partial_match_certain_order)}/200]")

        exact_match_uncertain_order = name_matcher_uncertain.get_name_match_ratio(
            person.surname_accents, person.given_name_accents,
            person.given_name_accents, person.surname_accents)
        print(
            f"Exact match, certain name order: {person.surname_accents} {person.given_name_accents} <-> {person} [MATCH: {int(exact_match_uncertain_order)}/200]")

        partial_match_uncertain_order = name_matcher_uncertain.get_name_match_ratio(
            person.surname_normalized, person.given_name_normalized,
            person.given_name_accents, person.surname_accents)
        print(
            f"Partial match, certain name order: {person.surname_normalized} {person.given_name_normalized} <-> {person} [MATCH: {int(partial_match_uncertain_order)}/200]")

        initial_match_certain_order_accents = name_matcher_certain.get_name_match_ratio(
            person.initial, person.surname_accents,
            person.given_name_accents, person.surname_accents)
        print(
            f"Initial match, certain name order: {person.initial} {person.surname_accents} <-> {person} [MATCH: {int(initial_match_certain_order_accents)}/200]")

        initial_match_certain_order_normalized = name_matcher_certain.get_name_match_ratio(
            person.initial, person.surname_normalized,
            person.given_name_accents, person.surname_accents)
        print(
            f"Initial match, certain name order: {person.initial} {person.surname_normalized} <-> {person} [MATCH: {int(initial_match_certain_order_normalized)}/200]")

        initial_match_uncertain_order_accents = name_matcher_uncertain.get_name_match_ratio(
            person.surname_accents, person.initial,
            person.given_name_accents, person.surname_accents)
        print(
            f"Initial match, certain name order: {person.surname_accents} {person.initial} <-> {person} [MATCH: {int(initial_match_uncertain_order_accents)}/200]")

        initial_match_uncertain_order_normalized = name_matcher_uncertain.get_name_match_ratio(
            person.surname_normalized, person.initial,
            person.given_name_accents, person.surname_accents)
        print(
            f"Initial match, certain name order: {person.surname_normalized} {person.initial} <-> {person} [MATCH: {int(initial_match_uncertain_order_normalized)}/200]")


if __name__ == '__main__':
    main()