from typing import Set

from abstracts.rankable import Rankable
from interfaces.imergeable import IMergeable
from models.institution import Institution
from models.researcher import Researcher


class Author(IMergeable["Author"], Rankable):
    def __init__(self, given_name: str, surname: str,
                 affiliations: Set[Institution] = None, emails: Set[str] = None,
                 orcid: str = "") -> None:
        super().__init__()
        self._MAX_NAME_MATCH_RATIO = 200
        self.given_name = given_name
        self.given_name_alternatives = set()

        self.surname = surname
        self.surname_alternatives = set()

        if not affiliations:
            affiliations = set()
        self.affiliations = affiliations

        if not emails:
            emails = set()
        self.emails = emails
        self._email_rank_value_presence_multiplier = 0.1
        self._email_rank_value_match_multiplier = 1
        self._email_rank_value_match = 100

        self.orcid = orcid
        self._orcid_rank_value_presence_multiplier = 0.1
        self._orcid_rank_value_match_multiplier = 1
        self._orcid_rank_value_match = 500

        self.orcid_alternatives = set()

        self.name_match_ratio = 0
        self.perfect_match_attrs_count = 0
        self.rank_breakdown = {}

    def merge_with(self, other: "Author", debug_flag: bool = False) -> None:
        if not self.given_name and other.given_name:
            self.given_name = other.given_name
        elif (self.given_name and other.given_name and self.given_name !=
              other.given_name):
            self.given_name_alternatives.add(other.given_name)

        if not self.surname and other.surname:
            self.surname = other.surname
        elif self.surname and other.surname and self.surname != other.surname:
            self.surname_alternatives.add(other.surname)

        # TODO - refine this merging, remove/join duplicate institutions
        self.affiliations.update(other.affiliations)

        self.emails.update(other.emails)

        if not self.orcid and other.orcid:
            self.orcid = other.orcid
        # should not happen ever
        elif self.orcid and other.orcid and self.orcid != other.orcid:
            self.orcid_alternatives.add(other.orcid)

    def __eq__(self, other):
        if self.orcid and other.orcid:
            return self.orcid == other.orcid
        else:
            return (self.given_name == other.given_name and self.surname ==
                    other.surname)

    def __hash__(self) -> int:
        return hash((self.given_name, self.surname))

    def __str__(self) -> str:
        affiliations_str = "Affiliations: \n" + "\n".join(
            f"\t - {str(institution)}" for institution in
            self.affiliations) if self.affiliations \
            else "?"
        return (
            f"Author: {self.given_name or "?"} (given name), "
            f"{self.surname or "?"} (surname) [NAME MATCH - "
            f"{int(self.name_match_ratio)}/200]\n"
            f"{affiliations_str}\n"
            f"ORCID: {self.orcid or "?"}\n"
            f"Email: {self.emails or "?"}"
        )

    def to_dict(self) -> dict:
        serialized_affiliations = [aff.to_dict() for aff in self.affiliations]

        return {
            "given_name": self.given_name,
            "surname": self.surname,
            "affiliations": serialized_affiliations,
            "emails": list(self.emails),
            "orcid": self.orcid,
            "attributes_with_perfect_match": self.perfect_match_attrs_count,
        }

    # TODO - reevaluate rank calculation & rank values
    def calculate_internal_rank(self, researcher: Researcher) -> float:
        self.internal_rank = 0
        self.perfect_match_attrs_count = 0

        self.rank_breakdown["affiliations"] = {"count": len(self.affiliations),
                                               "perfect_match": 0
                                               }
        affiliations_cumulative_rank = 0
        for affiliation in self.affiliations:
            affiliation_rank = affiliation.calculate_internal_rank(
                researcher)
            affiliations_cumulative_rank += affiliation_rank
            if affiliation.has_perfect_match:
                self.perfect_match_attrs_count += 1
                self.rank_breakdown["affiliations"]["perfect_match"] += 1

        self.rank_breakdown["affiliations"]["cumulative_rank"] = affiliations_cumulative_rank

        if len(self.affiliations) > 0:
            self.rank_breakdown["affiliations"]["avg_rank_per_affiliation"] = (
                round(affiliations_cumulative_rank / len(self.affiliations), 2))

        self.internal_rank += affiliations_cumulative_rank

        self.rank_breakdown["emails"] = {"count": len(self.emails),
                                         "perfect_match": 0}
        emails_cumulative_rank = 0
        for email in self.emails:
            if email == researcher.email:
                self.perfect_match_attrs_count += 1
                self.rank_breakdown["emails"]["perfect_match"] += 1
                emails_cumulative_rank += (
                        self._email_rank_value_match_multiplier *
                        self._email_rank_value_match)
            else:
                emails_cumulative_rank += (
                        self._email_rank_value_presence_multiplier *
                        self._email_rank_value_match)

        self.rank_breakdown["emails"][
            "cumulative_rank"] = emails_cumulative_rank

        if len(self.emails) > 0:
            self.rank_breakdown["emails"]["avg_rank_per_email"] = (
                round(emails_cumulative_rank / len(self.emails), 2))

        self.internal_rank += emails_cumulative_rank

        if self.orcid:
            self.rank_breakdown["orcid"] = {"rank": 0, "perfect_match": 0}
            orcid_rank = 0
            if self.orcid == researcher.orcid:
                self.perfect_match_attrs_count += 1
                self.rank_breakdown["orcid"]["perfect_match"] += 1
                orcid_rank += (
                        self._orcid_rank_value_match_multiplier *
                        self._orcid_rank_value_match)
            else:
                orcid_rank += (
                        self._orcid_rank_value_presence_multiplier *
                        self._orcid_rank_value_match)

            self.rank_breakdown["orcid"]["rank"] = orcid_rank
            self.internal_rank += orcid_rank

        self.internal_rank += self.name_match_ratio

        self.rank_breakdown["name"] = {"rank": round(self.name_match_ratio, 2),
                                       "max_value": self._MAX_NAME_MATCH_RATIO,
                                       "perfect_match": 0}
        if self.name_match_ratio == self._MAX_NAME_MATCH_RATIO:
            self.perfect_match_attrs_count += 1
            self.rank_breakdown["name"]["perfect_match"] += 1

        self.rank_breakdown[
            "attributes_with_perfect_match"] = self.perfect_match_attrs_count

        self.rank_breakdown["cumulative_rank"] = round(self.internal_rank, 2)
        return self.internal_rank
