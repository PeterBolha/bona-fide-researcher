import argparse

from models.search_results_aggregator import SearchResultsAggregator
from models.researcher import Researcher
from verification_modules.crossref_verification_module import \
    CrossrefVerificationModule
from verification_modules.orcid_verification_module import \
    OrcidVerificationModule


def print_args_overview(args):
    print("User attributes given:")
    print("----------------------")
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


    print("----------------------")

def main():
    parser = argparse.ArgumentParser(description='Verify eduperson based on the input data.')

    # arguments
    parser.add_argument("-gn", "--given-name", type=str, help="Given name of the person to be verified")
    parser.add_argument("-sn", "--surname", type=str, help="Surname of the person to be verified")
    parser.add_argument("-e", "--email", type=str, help="Email address of the person to be verified")
    parser.add_argument("-o", "--orcid", type=str, help="ORCID identifier of the person to be verified")
    parser.add_argument("-a", "--affiliation", type=str, help="(Institutional) Affiliation of the person to be verified")

    # switches
    parser.add_argument("-u", "--uncertain-name-order", action="store_true", help="Add when uncertain which name is the given name and which is the surname. Given name and Surname will be treated interchangeably.")
    parser.add_argument("-v", "--verbose", action="store_true", help="When present, all the available information about the researcher will be shown")

    args = parser.parse_args()
    print_args_overview(args)

    researcher = Researcher(args.given_name, args.surname, args.email, args.orcid, args.affiliation, args.uncertain_name_order)
    crossref_verification_module = CrossrefVerificationModule(args.verbose)
    orcid_verification_module = OrcidVerificationModule(args.verbose)
    verification_modules = [crossref_verification_module, orcid_verification_module]

    search_results_aggregator = SearchResultsAggregator(researcher, args.verbose)

    for verification_module in verification_modules:
        search_results_aggregator.search_results += verification_module.verify(researcher)

    search_results_aggregator.present_search_results()

if __name__ == '__main__':
    main()