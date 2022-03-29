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
    "protein": {
        "accession": "Q93079",
        "entry_name": "H2B1H_HUMAN",
        "name": "Histone H2B type 1-H",
        "sequence": "MPDPAKSAPAPKKGSKKAVTKAQKKDGKKRKRSRKESYSVYVYKVLKQVHPDTGISSKAMGIMNSFVNDIFERIAGEASRLAHYNKRSTITSREIQTAVRLLLPGELAKHAVSEGTKAVTKYTSSK",
        "taxonomy_id": 9606,
        "proteome_id": "UP000005640",
        "is_reviewed": true
    },
    "url": "http://localhost/proteins/Q93079"
}
```

To get the included peptides as well, add the parameter `include_peptides` with value 1, e.g. `http://localhost/api/proteins/<ACCESSION>?include_peptides=1`

#### output
```json
{
    "protein": {
        "accession": "Q93079",
        "entry_name": "H2B1H_HUMAN",
        "name": "Histone H2B type 1-H",
        "sequence": "MPDPAKSAPAPKKGSKKAVTKAQKKDGKKRKRSRKESYSVYVYKVLKQVHPDTGISSKAMGIMNSFVNDIFERIAGEASRLAHYNKRSTITSREIQTAVRLLLPGELAKHAVSEGTKAVTKYTSSK",
        "taxonomy_id": 9606,
        "proteome_id": "UP000005640",
        "is_reviewed": true
    },
    "url": "http://localhost/proteins/Q93079",
    "peptides": [
        {
            "c_terminus": "K",
            "length": 17,
            "n_terminus": "J",
            "number_of_missed_cleavages": 1,
            "sequence": "JJJPGEJAKHAVSEGTK",
            "mass": 1761.998831,
        },
        ...
    ]
  }
}
```

### Digest
#### url
`http://localhost/api/proteins/digest`    
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

example:
```json
{
	"sequence": "MGLLGILCFLIFLGKTWGQEQTYVISAPKIFRVGASENIVIQVYGYTEAFDATISIKSYPDKKFSYSSGHVHLSSENKFQNSAILT...",
	"maximum_number_of_missed_cleavages": 1,
	"minimum_peptide_length": 6,
	"maximum_peptide_length": 10
}
```

## Peptides
### Lookup by sequence
#### url
`http://localhost/api/peptides/<SEQUENCE>`   

#### ouput
```json
{
  "peptide": 
    "length": 15,
    "number_of_missed_cleavages": 0,
    "sequence": "AMGJMNSFVNDJFER",
    "mass": 1742.811994
  },
  "url": "http://localhost:3000/peptides/AMGJMNSFVNDJFER"
}
```

To get the parent proteins as well, add the parameter `include_proteins` with value 1, e.g. `http://localhost/api/peptides/<SEQUENCE>?include_proteins=1`

#### output
```json
{
    "peptide": {
        "length": 15,
        "number_of_missed_cleavages": 0,
        "sequence": "AMGJMNSFVNDJFER",
        "mass": 1742.811994
    },
    "url": "http://localhost:3000/peptides/AMGJMNSFVNDJFER",
    proteins: [
        {
            "accession": "Q93079",
            "entry_name": "H2B1H_HUMAN",
            "name": "Histone H2B type 1-H",
            "sequence": "MPDPAKSAPAPKKGSKKAVTKAQKKDGKKRKRSRKESYSVYVYKVLKQVHPDTGISSKAMGIMNSFVNDIFERIAGEASRLAHYNKRSTITSREIQTAVRLLLPGELAKHAVSEGTKAVTKYTSSK",
            "taxonomy_id": 9606,
            "proteome_id": "UP000005640",
            "is_reviewed": true
        },
        ...
    ]
}
```

### Lookup multiple sequences
#### url
`http://localhost/api/peptides/lookup`
#### method
`POST`
#### body (JSON)
```json
{
    "seqeunces": [
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
peptide_sequence_2
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
* order_by: string, default: mass, possible values: `mass` `length` `number_of_missed_cleavages` `sequence`, default: `mass`, optional (ignored for `text/plain`-output)
* order_descendent: bool, default: false, optional
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
            "mass": 859.494958413,
            "sequence": "RAMELLK",
            "is_swiss_prot": true,
            "is_trembl": true,
            "taxonomy_ids": [
                8032,
                30455,
                ...
            ],
            "unique_taxonomy_ids": [
                30455,
                194338,
                ...
            ],
            "proteome_ids": [
                "UP000261480",
                "UP000001038",
                ...
            ]
        },
        {
            "mass": 859.494958414,
            "sequence": "TVMVVVGR",
            "is_swiss_prot": true,
            "is_trembl": true,
            "taxonomy_ids": [
                48701,
                173247,
                ...
            ],
            "unique_taxonomy_ids": [
                48701,
                64144,
                ...
            ],
            "proteome_ids": [
                "UP000053641",
                "UP000264800",
                ...
            ]
        },
        {
            "mass": 859.498798203,
            "sequence": "RSSRQVK",
            "is_swiss_prot": true,
            "is_trembl": true,
            "taxonomy_ids": [
                1608454,
                586833,
                ...
            ],
            "unique_taxonomy_ids": [
                60296,
                41447,
                ...
            ],
            "proteome_ids": [
                "UP000504639",
                "UP000265160",
                ...
            ]
        },
        {
            "mass": 859.498798203,
            "sequence": "SSRQVKR",
            "is_swiss_prot": true,
            "is_trembl": true,
            "taxonomy_ids": [
                1608454,
                586833,
                ...
            ],
            "unique_taxonomy_ids": [
                60296,
                41447,
                ...
            ],
            "proteome_ids": [
                "UP000504639",
                "UP000265160",
                ...
            ]
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
{"mass":859.494958414,"sequence":"TVMVVVGR","is_swiss_prot":true,"is_trembl":true,"taxonomy_ids":[48701,173247,...],"unique_taxonomy_ids":[48701,64144,...],"proteome_ids":["UP000053641","UP000264800",...]}
{"mass":859.498798203,"sequence":"RSSRQVK","is_swiss_prot":true,"is_trembl":true,"taxonomy_ids":[1608454,586833,...],"unique_taxonomy_ids":[60296,41447,...],"proteome_ids":["UP000504639","UP000265160",...]}
{"mass":859.498798203,"sequence":"SSRQVKR","is_swiss_prot":true,"is_trembl":true,"taxonomy_ids":[1608454,586833,...],"unique_taxonomy_ids":[60296,41447,...],"proteome_ids":["UP000504639","UP000265160",...]}
```

#### output (text/plain))
Text stream in fasta format.
```
>lcl|859494958413_RAMELLK
RAMELLK
>lcl|859494958414_TVMVVVGR
TVMVVVGR
>lcl|859498798203_RSSRQVK
RSSRQVK
>lcl|859498798203_SSRQVKR
SSRQVKR
```

#### output (application/octet-stream)
```
"mass","sequence","in_swiss_prot","in_trembl","taxonomy_ids","unique_for_taxonomy_ids","proteome_ids"
859.491587572,"AAFPQKKA","false","true","61819,8014","8014","None,UP000261340"
859.491587572,"AAFQPKAK","true","true","10090,230844,56216,10089,10116,10036","56216,10089,10116,10036","UP000000589,UP000515126,UP000092124,UP000504601,UP000189706,UP000002494"
859.491587572,"AAKKWEK","false","true","48278","48278","UP000559068"
859.491587572,"AAKWKEK","false","true","545262,205130","545262,205130","UP000557230,UP000261640"
859.491587572,"AAWEKKK","false","true","176057","176057","UP000053840"
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
  "children": [
    37401,
    56938,
    242118,
    242111,
    269534,
    269532,
    304441,
    984492
  ],
  "name": "Pallaviciniaceae",
  "parent": 186795
}
```

#### note
If the given ID was merged with another one, the resulting ID will differ. The ID `56884` from the example was merged with `71399`. So `71399` is reported.