import unittest
import requests
import json
import math

from macpepdb.models.peptide import Peptide

class ApiPeptideControllerTestCase(unittest.TestCase):
    def test_peptide_limit_offset_for_octet_stream(self):
        URL = "http://localhost:3000/api/peptides/search"
        LIMIT = 50

        request_body = {
            "modifications": [
                {
                    "amino_acid": "C",
                    "position": "anywhere",
                    "is_static": True,
                    "delta": 57.021464
                }
            ],
            "lower_precursor_tolerance_ppm": 5,
            "upper_precursor_tolerance_ppm": 5,
            "variable_modification_maximum": 0,
            "precursor": 859.49506802369,
            "order_by": "mass",
            "order_direction": "asc"
        }

        headers = {
            "Conent-Type": "application/json",
            "Accept": "application/octet-stream"
        }

        all_results = []

        # Fetch all peptides
        res = requests.post(URL, json=request_body, headers=headers, stream=True)
        self.assertTrue(res.ok)
        for line in res.iter_lines():
            all_results.append(json.loads(line))

        request_body['limit'] = LIMIT

        number_of_iterations = math.ceil(len(all_results) / LIMIT)

        # Fetch the same peptides in chunks of 50 peptides
        for i in range(number_of_iterations):
            offset = i * LIMIT
            request_body['offset'] = offset

            chunk = []
            res = requests.post(URL, json=request_body, headers=headers, stream=True)
            self.assertTrue(res.ok)
            for line in res.iter_lines(): 
                chunk.append(json.loads(line))

            # Separate peptides within the same offset/limit from alle requests
            chunk_from_all_results = all_results[offset:offset+LIMIT]

            # Test if bot chunks have th same length
            self.assertEqual(len(chunk), len(chunk_from_all_results))
            
            # Test if peptides on position j are the same
            for j in range(len(chunk_from_all_results)):
                self.assertEqual(chunk[j]['sequence'], chunk_from_all_results[j]['sequence'])
                self.assertEqual(chunk[j]['mass'], chunk_from_all_results[j]['mass'])

    def test_peptide_limit_offset_for_json(self):
        URL = "http://localhost:3000/api/peptides/search"
        LIMIT = 50

        request_body = {
            "modifications": [
                {
                    "amino_acid": "C",
                    "position": "anywhere",
                    "is_static": True,
                    "delta": 57.021464
                }
            ],
            "lower_precursor_tolerance_ppm": 5,
            "upper_precursor_tolerance_ppm": 5,
            "variable_modification_maximum": 0,
            "precursor": 859.49506802369,
            "order_by": "mass",
            "order_direction": "asc"
        }

        headers = {
            "Conent-Type": "application/json",
            "Accept": "application/json"
        }

        all_results = []

        # Fetch all peptides
        res = requests.post(URL, json=request_body, headers=headers)
        self.assertTrue(res.ok)
        all_results = res.json()['peptides']

        request_body['limit'] = LIMIT

        number_of_iterations = math.ceil(len(all_results) / LIMIT)

        # Fetch the same peptides in chunks of 50 peptides
        for i in range(number_of_iterations):
            offset = i * LIMIT
            request_body['offset'] = offset

            res = requests.post(URL, json=request_body, headers=headers)
            self.assertTrue(res.ok)
            chunk = res.json()['peptides']
            
            # Separate peptides within the same offset/limit from alle requests
            chunk_from_all_results = all_results[offset:offset+LIMIT]

            # Test if bot chunks have th same length
            self.assertEqual(len(chunk), len(chunk_from_all_results))

            # Test if peptides on position j are the same
            for j in range(len(chunk_from_all_results)):
                self.assertEqual(chunk[j]['sequence'], chunk_from_all_results[j]['sequence'])
                self.assertEqual(chunk[j]['mass'], chunk_from_all_results[j]['mass'])

    def test_peptide_limit_offset_for_plain_text(self):
        URL = "http://localhost:3000/api/peptides/search"
        LIMIT = 50

        request_body = {
            "modifications": [
                {
                    "amino_acid": "C",
                    "position": "anywhere",
                    "is_static": True,
                    "delta": 57.021464
                }
            ],
            "lower_precursor_tolerance_ppm": 5,
            "upper_precursor_tolerance_ppm": 5,
            "variable_modification_maximum": 0,
            "precursor": 859.49506802369,
            "order_by": "mass",
            "order_direction": "asc"
        }

        headers = {
            "Conent-Type": "application/json",
            "Accept": "text/plain"
        }

        all_results = []

        # Fetch all peptides
        res = requests.post(URL, json=request_body, headers=headers, stream=True)
        self.assertTrue(res.ok)
        for line in res.iter_lines():
            if not line.startswith(b'>'):
                line = line.decode('utf-8')
                all_results.append(Peptide(line.strip(), 0))

        request_body['limit'] = LIMIT

        number_of_iterations = math.ceil(len(all_results) / LIMIT)

        # Fetch the same peptides in chunks of 50 peptides
        for i in range(number_of_iterations):
            offset = i * LIMIT
            request_body['offset'] = offset

            chunk = []
            res = requests.post(URL, json=request_body, headers=headers, stream=True)
            self.assertTrue(res.ok)
            for line in res.iter_lines():
                if not line.startswith(b'>'):
                    line = line.decode('utf-8')
                    chunk.append(Peptide(line.strip(), 0))

            # Separate peptides within the same offset/limit from alle requests
            chunk_from_all_results = all_results[offset:offset+LIMIT]

            # Test if bot chunks have th same length
            self.assertEqual(len(chunk), len(chunk_from_all_results))
            
            # Test if peptides on position j are the same (fasta format does not contains the length or id, so we have to compare the sequence)
            for j in range(len(chunk_from_all_results)):
                self.assertEqual(chunk[j].sequence, chunk_from_all_results[j].sequence)

    def test_count(self):
        """
        Tests if the reported count is equals the actual number of results with different filters. `limit` and `offset` are not considered, because they are not applied to the actual query.
        """
        URL = "http://localhost:3000/api/peptides/search"

        NO_MODIFICATION_REQUEST_BODY = {
            "include_count": True,
            "modifications": [],
            "lower_precursor_tolerance_ppm": 5,
            "upper_precursor_tolerance_ppm": 5,
            "variable_modification_maximum": 0,
            "precursor": 859.49506802369,
            "order_by": "mass",
            "order_direction": "asc"
        }

        MODIFICATION_REQUEST_BODY = {
            "include_count": True,
            "modifications": [
                {
                    "amino_acid": "C",
                    "position": "anywhere",
                    "is_static": True,
                    "delta": 57.021464
                }
            ],
            "lower_precursor_tolerance_ppm": 5,
            "upper_precursor_tolerance_ppm": 5,
            "variable_modification_maximum": 0,
            "precursor": 859.49506802369,
            "order_by": "mass",
            "order_direction": "asc"
        }

        TAXONOMY_REQUEST_BODY = {
            "include_count": True,
            "taxonomy_id": 9606,
            "modifications": [],
            "lower_precursor_tolerance_ppm": 5,
            "upper_precursor_tolerance_ppm": 5,
            "variable_modification_maximum": 0,
            "precursor": 859.49506802369,
            "order_by": "mass",
            "order_direction": "asc"
        }

        MODIFICATION_AND_TAXONOMY_REQUEST_BODY = {
            "include_count": True,
            "taxonomy_id": 9606,
            "modifications": [
                {
                    "amino_acid": "C",
                    "position": "anywhere",
                    "is_static": True,
                    "delta": 57.021464
                }
            ],
            "lower_precursor_tolerance_ppm": 5,
            "upper_precursor_tolerance_ppm": 5,
            "variable_modification_maximum": 0,
            "precursor": 859.49506802369,
            "order_by": "mass",
            "order_direction": "asc"
        }

        for request_body in [NO_MODIFICATION_REQUEST_BODY, MODIFICATION_REQUEST_BODY, TAXONOMY_REQUEST_BODY, MODIFICATION_AND_TAXONOMY_REQUEST_BODY]:
            res = requests.post(URL, json=request_body, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
            self.assertTrue(res.ok)
            response_body = res.json()
            self.assertEqual(response_body['count'], len(response_body['peptides']))

