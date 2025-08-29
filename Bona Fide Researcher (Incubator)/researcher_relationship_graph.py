import json
from argparse import Namespace

from arxiv_api.core.graph_generator import GraphGenerator

from enums.result_presentation_mode import ResultPresentationMode


def get_researcher_relationship_graph_data(args: Namespace = None,
                                           presentation_mode:
                                           ResultPresentationMode =
                                           ResultPresentationMode.API) -> dict:

    g = GraphGenerator()
    json_result = g.generate_graph(args.full_name, args.max_relationship_depth)
    decoded_result = json.loads(json_result)

    if presentation_mode == ResultPresentationMode.CLI:
        print(f"Researcher relationship graph data for "
              f"{args.full_name}: {decoded_result}")

    return decoded_result