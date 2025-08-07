from argparse import ArgumentParser, Namespace

from enums.result_presentation_mode import ResultPresentationMode
from models.researcher import Researcher
from models.search_results_aggregator import SearchResultsAggregator
from utils.formatting import print_delimiter_large
from verification_modules.composable.arxiv_verification_module import \
    ArxivVerificationModule
from verification_modules.composable.crossref_verification_module import \
    CrossrefVerificationModule
from verification_modules.composable.eosc_verification_module import \
    EoscVerificationModule
from verification_modules.composable.orcid_verification_module import \
    OrcidVerificationModule
from verification_modules.self_contained.ror_verification_module import \
    RorVerificationModule


def print_args_overview(args):
    print("User attributes given:")
    print_delimiter_large()

    if args.given_name:
        print("Given name:", args.given_name)

    if args.surname:
        print("Surname:", args.surname)

    if args.email:
        print("Email:", args.email)

    if args.orcid:
        print("ORCID:", args.given_name)

    if args.uncertain_name_order:
        print("Uncertain name order")
    else:
        print("Fixed name order")

    print_delimiter_large()


def get_args_from_cli() -> Namespace:
    parser = ArgumentParser(
        description='Verify eduperson based on the input data.')

    # arguments
    parser.add_argument("-gn", "--given-name", type=str,
                        help="Given name of the person to be verified")
    parser.add_argument("-sn", "--surname", type=str,
                        help="Surname of the person to be verified")
    parser.add_argument("-e", "--email", type=str,
                        help="Email address of the person to be verified")
    parser.add_argument("-o", "--orcid", type=str,
                        help="ORCID identifier of the person to be verified")
    parser.add_argument("-a", "--affiliation", type=str,
                        help="(Institutional) Affiliation of the person to be "
                             "verified (ROR, ISNI or name)")
    parser.add_argument("-l", "--limit-results", type=int, default=-1,
                        help="Limit the output results to first N by rank")

    # switches
    parser.add_argument("-u", "--uncertain-name-order", action="store_true",
                        help="Add when uncertain which name is the given name "
                             "and which is the surname. Given name and "
                             "Surname will be treated interchangeably.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="When present, all the available information "
                             "about the researcher will be shown.")
    parser.add_argument("-d", "--verify-email-domain", action="store_true",
                        help="When present, email domain will be verified "
                             "through ROR. Email must be provided.")

    return parser.parse_args()

def verify_eduperson(args: Namespace = None, presentation_mode:
ResultPresentationMode = ResultPresentationMode.CLI):
    if args is None:
        args = get_args_from_cli()

    print_args_overview(args)

    researcher = Researcher(args.given_name, args.surname, args.email,
                            args.orcid, args.affiliation,
                            args.uncertain_name_order)

    # Self-contained verification modules
    # - produce individual results published once at the beginning
    ror_verification_module = RorVerificationModule(args.verbose,
                                                    is_active=args.verify_email_domain)

    self_contained_verification_modules = [ror_verification_module]

    # Composable verification modules
    # - produce results that need to be composed together before publishing
    crossref_verification_module = CrossrefVerificationModule(args.verbose)
    orcid_verification_module = OrcidVerificationModule(args.verbose)
    eosc_verification_module = EoscVerificationModule(args.verbose)
    arxiv_verification_module = ArxivVerificationModule(args.verbose)

    composable_verification_modules = [crossref_verification_module,
                                       orcid_verification_module,
                                       eosc_verification_module,
                                       arxiv_verification_module]

    search_results_aggregator = SearchResultsAggregator(researcher,
                                                        args.verbose)

    for verification_module in composable_verification_modules:
        verification_results = verification_module.verify(researcher)
        search_results_aggregator.add_results(verification_results)

    if presentation_mode == ResultPresentationMode.CLI:
        # print results to console standard output
        for verification_module in self_contained_verification_modules:
            verification_module.verify(researcher)

        search_results_aggregator.present_search_results_cli(args.limit_results)
    elif presentation_mode == ResultPresentationMode.API:
        # return results in a structured (JSON) format that can be passed to
        # the API response
        results = {}
        for verification_module in self_contained_verification_modules:
            if not verification_module.is_active:
                continue
            api_name = verification_module.api_name
            results[api_name] = verification_module.verify(researcher)
        composed_results = search_results_aggregator.get_search_results_dict(
            args.limit_results)
        results["researcher_info"] = composed_results
        return results
    else:
        raise ValueError("Invalid presentation mode chosen for data "
                         f"presentation: {presentation_mode}.")


if __name__ == '__main__':
    verify_eduperson()
