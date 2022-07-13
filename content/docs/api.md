---
title: API
description: Learn how to the MaCPepDB API
---

## Proteins
### Lookup by accession
#### url
`http://localhost/api/proteins/<ACCESSION>`   
#### ouput
```json
{
    "accession": "P04637",
    "entry_name": "P53_HUMAN",
    "is_reviewed": true,
    "name": "Tumor suppressor p53",
    "proteome_id": "UP000005640",
    "sequence": "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD",
    "taxonomy_id": 9606,
    "taxonomy_name": "Homo sapiens"
}
```

### Get peptides of protein
#### url
`http://localhost/api/proteins/<string:accession>/peptides`   
#### ouput
```json
{
    "peptides": [
        {
        "is_swiss_prot": true,
        "is_trembl": true,
        "mass": 588.286739698,
        "number_of_missed_cleavages": 0,
        "proteome_ids": ["UP000186942", ...],
        "sequence": "DAQAGK",
        "taxonomy_ids": [9749, ...],
        "unique_taxonomy_ids": [9534, ...]
        },
        ...
    ]
}
```

### Digest protein
#### url
`http://localhost/api/proteins/digest`   
#### method
`POST`    
#### additional headers
* Content-Type: application/json
#### body (JSON)
keys:
* accession: string
* maximum_number_of_missed_cleavages: unsigned int
* minimum_peptide_length: unsigned int
* maximum_peptide_length: unsigned int
#### ouput
```json
{
    "peptides": [
        {
            "mass": 588.286739698,
            "sequence": "DAQAGK",
            "length": 6,
            "number_of_missed_cleavages": 0,
            "metadata": null
        },
        ...
    ],
    count: 101
}
```

### Get amino acids
#### url
`http://localhost/api/proteins/amino-acids`   
#### ouput
```json
    "amino_acids": [
        {
        "name": "Alanine",
        "one_letter_code": "A"
        },
        ...
    ]
}
```
There are also ambigous amino acids present!

## Peptides
### Lookup by sequence
#### url
`http://localhost/api/peptides/<SEQUENCE>`

#### Query parameter
is_reviewed: int, option, filter for SwissProt (!=0), TrEMBL (==0) and both (not present)

#### ouput
```json
{
    "mass": 950.537157588,
    "sequence": "VRAMAIYK",
    "length": 8,
    "number_of_missed_cleavages": 1,
    "metadata": {
        "is_swiss_prot": true,
        "is_trembl": true,
        "taxonomy_ids": [34862, ...],
        "unique_taxonomy_ids": [34862, ...],
        "proteome_ids": ["UP000326062", ...]
    }
}
```

### Get proteins of peptide 
#### url
`http://localhost/api/peptides/<SEQUENCE>/proteins`   

#### ouput
```json
{
    "reviewed_proteins": [
        {
        "accession": "P41685",
        "entry_name": "P41685",
        "name": "Tumor suppressor p53",
        "sequence": "MQEPPLELTIEPPLSQETFSELWNLLPENNVLSSELSSAMNELPLSEDVANWLDEAPDDASGMSAVPAPAAPAPATPAPAISWPLSSFVPSQKTYPGAYGFHLGFLQSGTAKSVTCTYSPPLNKLFCQLAKTCPVQLWVRSPPPPGTCVRAMAIYKKSEFMTEVVRRCPHHERCPDSSDGLAPPQHLIRVEGNLHAKYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNFMCNSSCMGGMNRRPIITIITLEDSNGKLLGRNSFEVRVCACPGRDRRTEEENFRKKGEPCPEPPPGSTKRALPPSTSSTPPQKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQSGKEPGGSRAHSSHLKAKKGQSTSRHKKPMLKREGLDSD",
        "taxonomy_id": 9685,
        "proteome_id": "UP000011712",
        "is_reviewed": true
        },
        ...
    ],
    "unreviewed_proteins_rows": [
        {
        "accession": "A4GW67",
        "entry_name": "A4GW67",
        "name": "Tumor protein p53",
        "sequence": "VGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKR",
        "taxonomy_id": 9606,
        "proteome_id": "None",
        "is_reviewed": false
        },
        ...
    ]
}
```

### Check multiple sequences for existence
#### url
`http://localhost/api/peptides/lookup`
#### method
`POST`
#### body (JSON)
```json
{
    "sequences": [
        "peptide_sequence_1",
        "peptide_sequence_2",
        "peptide_sequence_3",
        ...
    ]
}
```
#### ouput (text/plain)
```txt
peptide_sequence_1
peptide_sequence_3
...
```
More output formats coming soon.

### Search by mass
#### url
`http://localhost/api/peptides/search`   
or
`http://localhost/api/peptides/search.(json|stream|txt|csv)`   
#### method
`POST`    
#### additional headers
* Content-Type: application/json
* Accept: `application/json`, `application/octet-stream`, `text/plain`  or `text/csv` (This controlls the output, see below. `application/json` is the default and is used for unknown accept-formats)

#### body (JSON) 
keys:
* precursor: float
* lower_precursor_tolerance_ppm: unsigned int
* upper_precursor_tolerance_ppm: unsigned int
* variable_modification_maximum: unsigned int
* modifications: array of modifications, each modification is a dictionary with keys
    * amino_acid: string containing the amino acid one letter code
    * position: string (anywhere|n_terminus|c_terminus)
    * is_static: bool, marks modification as static or variable
    * delta: float, the mass change which is applied by this modification
* limit: unsigned int (optional)
* offset: unsigned int (optional)
* taxonomy_id: unsigned int (Uniprot Taxonomy Identifier)
* proteome_id: string (Uniprot Proteome Identifier: UP...)
* is_reviewed: bool, default: not set, optional (selects from which database the peptides will be from, not set: Swiss-Prot + TrEMBL, true: SwissProt, false: TrEMBL)
* include_count: bool, default: false, optional (includes the peptides count without limit or offset. setting this to false cut the response time by 50%, only accounted for `application/json`-output)
* order_by: string, default: `mass`, optional (ignored for `text/plain`-output), possible values: `mass` `length` `number_of_missed_cleavages` `sequence`, default: `mass`, 
* order_direction: bool, must be present when `order_by` is set, possible values: `asc` & `desc`
* include_metadata: bool, default: false, optional

If `taxonomy_id`, `proteome_id`, `is_reviewed` are used together they will concanted with `and`.

#### body (Form) 
The search parameter can also be submitted as content type `application/x-www-form-urlencoded`. In this case provide the parameters as JSON-string in a form parameter called `search_params`.

#### output format
The output format can also be changed by prepanding a file extension
| file extension | output format |
| --- | --- |
| `json` | `application/json` |
| `stream` | `application/octet-stream` |
| `txt` | `text/plain` |
| `csv` | `text/csv` | 

example:
```json
{
	"precursor": 859.49506802369,
	"lower_precursor_tolerance_ppm": 5,
	"upper_precursor_tolerance_ppm": 5,
	"variable_modification_maximum": 0,
	"modifications": [
		{
			"amino_acid": "C",
			"position": "anywhere",
			"is_static": true,
			"delta": 57.021464
		},
		...
	],
    "limit": 10,
    "offset": 10,
    "taxonomy_id": 7955,
    "proteome_id": "UP000000437",
    "is_reviewed": true
}
```

#### output (application/json)
```json
{
    "peptides": [
        {
            "mass": 950.537157588,
            "sequence": "VRAMAIYK",
            "length": 8,
            "number_of_missed_cleavages": 1,
            "metadata": {
                "is_swiss_prot": true,
                "is_trembl": true,
                "taxonomy_ids": [34862, ...],
                "unique_taxonomy_ids": [34862, ...],
                "proteome_ids": ["UP000326062", ...]
            }
        },
        ...
    ],
    "count": 19
}
```
#### output (application/octet-stream)
Bytestream which contains one peptide in JSON-format per line.
```
{"mass":859.494958413,"sequence":"RAMELLK","is_swiss_prot":true,"is_trembl":true,"taxonomy_ids":[8032,30455,...],"unique_taxonomy_ids":[30455,194338,...],"proteome_ids":["UP000261480","UP000001038",...]}
....
```

#### output (text/plain))
Text stream in fasta format.
```
>macpepdb|859494958413_RAMELLK
RAMELLK
...
```

#### output (text/csv)
```
"mass","sequence","in_swiss_prot","in_trembl","taxonomy_ids","unique_for_taxonomy_ids","proteome_ids"
859.491587572,"AAFPQKKA","false","true","61819,8014","8014","None,UP000261340"
...
```

### Calculate theoretical mass
####
`http://localhost/api/peptides/mass/<SEQUENCE>`
#### additional headers
* Content-Type: application/json
#### example
`http://localhost/api/peptides/mass/VQDDTK`
#### output
```json
{
    "mass": 704.334083868
}
```

### Digest peptide
#### url
`http://localhost/api/peptides/digest`   
#### method
`POST`    
#### additional headers
* Content-Type: application/json
#### body (JSON)
keys:
* sequence: string
* maximum_number_of_missed_cleavages: unsigned int
* minimum_peptide_length: unsigned int
* maximum_peptide_length: unsigned int
* do_database_search: bool, if true the resulting peptides will be matched against the database
#### ouput
```json
{
    "database": [
        {
            "mass": 588.286739698,
            "sequence": "DAQAGK",
            "length": 6,
            "number_of_missed_cleavages": 0,
            "metadata": null
        },
        ...
    "digestion": [
        ...
    ],
    "
Body
Cookies
Headers
(6)
Test Results
Status:
": 101
}
```

## Taxonomies
### Search
#### url
`http://localhost/api/taxonomies/search`
#### method
`POST`
#### additional headers
* Content-Type: application/json
#### body (JSON)
keys:
* query: int|string (If this is an integer, the API searches for an exact ID. If this is a string, the API search for a scientific name. You can use '*' as wildcard.)

example:
```json
{
    "query": 71399
}
```
or
```json
{
    "query": "*laviciniaceae"
}
```

#### output
Both examples will lead to
```json
[
    {
        "id": 71399,
        "name": "Pallaviciniaceae"
    }
]
```

#### note
If the given ID was merged with another one, only the new ID will reported. For example a search for ID `56884` would result in the same output, because it was merged with `71399`.


### Lookup by ID
#### url
`http://localhost/api/taxonomies/<ID>`
#### example
`http://localhost/api/taxonomies/56884`
#### output
```json
{
    "id": 71399,
    "name": "Pallaviciniaceae",
    "parent": 186795,
    "rank": 4
}
```

#### note
If the given ID was merged with another one, the resulting ID will differ. The ID `56884` from the example was merged with `71399`. So `71399` is reported.

### Lookup sub species of taxonomy
#### url
`http://localhost/api/taxonomies/<ID>/sub-species`
#### example
`http://localhost/api/taxonomies/71399/sub-species`
#### output
```json
{
    "sub_species": [
        {
            "id": 53033,
            "name": "Symphyogyna brongniartii",
            "parent": 37401,
            "rank": 23
        },
        ...
    ]
}
```
