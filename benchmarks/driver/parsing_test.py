from unittest import TestCase

import pytest
import json
import re

from esrally.driver import runner

class ParsingBenchmarks(TestCase):

    def test_all_candidates(self):
        """
        Quick utility test to ensure all benchmark cases are correct
        """

        sort = sort_parsing_candidate_reverse_and_regexp(self.small_page)
        self.assertEqual("[1609780186, \"2\"]", sort)

        pit_id = pit_id_parsing_candidate_regexp(self.small_page)
        self.assertEqual("fedcba9876543210", pit_id)

        pit_id, sort = combined_parsing_candidate_json_loads(self.small_page)
        self.assertEqual([1609780186, "2"], sort)
        self.assertEqual("fedcba9876543210", pit_id)

    small_page = """
    {
            "pit_id": "fedcba9876543210",
            "took": 10,
            "timed_out": false,
            "hits": {
                "total": 2,
                "hits": [
                    {
                        "_id": "1",
                         "timestamp": 1609780186,
                         "sort": [1609780186, "1"]
                    },
                    {
                        "_id": "2",
                         "timestamp": 1609780186,
                         "sort": [1609780186, "2"]
                    }
                ]
            }
        }
    """.replace("\n", " ")

@pytest.mark.benchmark(
    group="parse",
    warmup="on",
    warmup_iterations=10000,
    disable_gc=True
)
def test_sort_reverse_and_regexp_small(benchmark):
    benchmark(sort_parsing_candidate_reverse_and_regexp, ParsingBenchmarks.small_page)

def sort_parsing_candidate_reverse_and_regexp(response):
    reversed_response = response[::-1]
    sort_pattern = r"(\][^\]]*\[) :\"tros\""
    x = re.search(sort_pattern, reversed_response)
    return x.group(1)[::-1]

@pytest.mark.benchmark(
    group="parse",
    warmup="on",
    warmup_iterations=10000,
    disable_gc=True
)
def test_pit_id_regexp_small(benchmark):
    benchmark(pit_id_parsing_candidate_regexp, ParsingBenchmarks.small_page)

def pit_id_parsing_candidate_regexp(response):
    pit_id_pattern = r'"pit_id": "([^"]*)"'
    x = re.search(pit_id_pattern, response)
    return x.group(1)

@pytest.mark.benchmark(
    group="parse",
    warmup="on",
    warmup_iterations=10000,
    disable_gc=True
)
def test_combined_json_small(benchmark):
    benchmark(combined_parsing_candidate_json_loads, ParsingBenchmarks.small_page)

def combined_parsing_candidate_json_loads(response):
    parsed_response = json.loads(response)
    pit_id = parsed_response.get("pit_id")
    sort = parsed_response.get("hits").get("hits")[-1].get("sort")
    return pit_id, sort