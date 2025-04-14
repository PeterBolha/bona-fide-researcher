from typing import List

from models.researcher import Researcher
from models.search_results.unified_search_result import UnifiedSearchResult


class SearchResultsAggregator:
    def __init__(self, researcher: Researcher, verbose: bool = False):
        self.researcher = researcher
        self.aggregated_search_results = {}
        self.verbose = verbose

    def add_results(self, search_results: List[UnifiedSearchResult]):
        total = len(search_results)
        print(f"Adding {total} search results")
        count = 0
        for search_result in search_results:
            # if count % 10 == 0:
            print(f"Processed {count}/{total} search results")

            author = search_result.matched_author
            if not author:
                print(
                    f"Author not found for result: {search_result}. Skipping.")
                continue
            print("Aggregating author")
            aggregated_search_result = self.aggregated_search_results.get(author)
            print("Aggregated author")

            if not aggregated_search_result:
                    self.aggregated_search_results[author] = {}

            # TODO - handle missing DOI
            doi = search_result.doi
            stored_article: UnifiedSearchResult = self.aggregated_search_results[author].get(doi)
            # store article from the search result if not already present
            if not stored_article:
                print("Article not present, storing article anew")
                stored_article = search_result
                self.aggregated_search_results[author][doi] = search_result
            # if article with the same DOI already exists, consolidate information with the new data source
            else:
                print("Merging article")
                debug = count == 8
                stored_article.merge_with(search_result, debug_flag=debug)
                print("Merged article")


            self.aggregated_search_results[author][doi] = stored_article
            count += 1

    def _rank_results(self):
        for result in self.aggregated_search_results:
            result.calculate_internal_rank(self.researcher)

    def _sort_results(self):
        self.aggregated_search_results = sorted(self.aggregated_search_results,
                                                reverse=True)

    def _print_search_results(self):
        for result in self.aggregated_search_results:
            result.print(self.verbose)

    def present_search_results(self):
        print("Ranking results:")
        self._rank_results()
        print("Sorting results")
        self._sort_results()
        print("Printing results")
        self._print_search_results()
        print("Done")
