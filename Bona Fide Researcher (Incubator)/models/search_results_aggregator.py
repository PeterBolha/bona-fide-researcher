import math
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
        count = 0
        # How often to print processing updates
        print_update_interval = math.ceil(len(search_results) / 10)
        for search_result in search_results:
            author = search_result.matched_author
            if not author:
                print(
                    f"Author not found for result: {search_result}. Skipping.")
                continue
            aggregated_search_result = self.aggregated_search_results.get(author)

            if not aggregated_search_result:
                    self.aggregated_search_results[author] = {"articles": {},
                                                              "internal_rank": 0}

            # TODO - handle missing DOI
            doi = search_result.doi
            # TODO - check correctness of .get("articles")
            stored_article: UnifiedSearchResult = self.aggregated_search_results[author].get("articles", {}).get(doi)
            # store article from the search result if not already present
            if not stored_article:
                stored_article = search_result
                self.aggregated_search_results[author]["articles"][doi] = search_result
            # if article with the same DOI already exists, consolidate information with the new data source
            else:
                stored_article.merge_with(search_result)


            self.aggregated_search_results[author]["articles"][doi] = stored_article

            count += 1
            if count % print_update_interval == 0:
                print(f"Processed {count}/{total} search results")

    # TODO - prevent double scoring of inner structures
    def _rank_results(self):
        for author, results in self.aggregated_search_results.items():
            article_scores = 0
            for search_result in results["articles"].values():
                article_scores += search_result.calculate_internal_rank(self.researcher)

            author_score = author.calculate_internal_rank(self.researcher)
            self.aggregated_search_results[author]["internal_rank"] = author_score + article_scores

    def _sort_results(self):
        # Sort results overall (authors displayed in order of relevance)
        # Sorting based on author's rank
        self.aggregated_search_results = dict(sorted(
            self.aggregated_search_results.items(),
            key=lambda result: result[0].internal_rank,
            reverse=True))

        # Sort articles within author's records in order of relevance
        for author, result in self.aggregated_search_results.items():
            articles = result["articles"]
            self.aggregated_search_results[author]["articles"] = dict(sorted(
            articles.items(),
            key=lambda result: result[1].internal_rank,
            reverse=True))

    def _print_search_results(self, limit_results: int):
        for index, (author, results) in enumerate(self.aggregated_search_results.items()):
            if index == limit_results:
                break

            print(f"#{index + 1} (INDEX) - {results["internal_rank"]:.2f} (RESULT RANK)")
            print(author)
            print("Collected works:")
            for doi, search_result in results["articles"].items():
                search_result.print(verbose=self.verbose)


    def present_search_results(self, limit_results: int):
        self._rank_results()
        self._sort_results()
        self._print_search_results(limit_results)
