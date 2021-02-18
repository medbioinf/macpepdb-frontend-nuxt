# API usage

## Proteins
### Lookup by accession
#### url
`http://localhost/api/proteins/<ACCESSION>`   
#### ouput
```json
{
    "protein": {
        "id": 2063,
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
        "id": 2063,
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
            "a_count": 2,
            "c_count": 0,
            "c_terminus": "K",
            "d_count": 0,
            "e_count": 2,
            "f_count": 0,
            "g_count": 2,
            "h_count": 1,
            "id": 275088,
            "j_count": 4,
            "k_count": 2,
            "length": 17,
            "m_count": 0,
            "n_count": 0,
            "n_terminus": "J",
            "number_of_missed_cleavages": 1,
            "o_count": 0,
            "p_count": 1,
            "q_count": 0,
            "r_count": 0,
            "s_count": 1,
            "sequence": "JJJPGEJAKHAVSEGTK",
            "t_count": 1,
            "u_count": 0,
            "v_count": 1,
            "w_count": 0,
            "weight": 1761.998831,
            "y_count": 0
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
  "peptide": {
    "a_count": 1,
    "c_count": 0,
    "c_terminus": "R",
    "d_count": 1,
    "e_count": 1,
    "f_count": 2,
    "g_count": 1,
    "h_count": 0,
    "id": 275019,
    "j_count": 2,
    "k_count": 0,
    "length": 15,
    "m_count": 2,
    "n_count": 2,
    "n_terminus": "A",
    "number_of_missed_cleavages": 0,
    "o_count": 0,
    "p_count": 0,
    "q_count": 0,
    "r_count": 1,
    "s_count": 1,
    "sequence": "AMGJMNSFVNDJFER",
    "t_count": 0,
    "u_count": 0,
    "v_count": 1,
    "w_count": 0,
    "weight": 1742.811994,
    "y_count": 0
  },
  "url": "http://localhost:3000/peptides/AMGJMNSFVNDJFER"
}
```

To get the parent proteins as well, add the parameter `include_proteins` with value 1, e.g. `http://localhost/api/peptides/<SEQUENCE>?include_proteins=1`

#### output
```json
{
    "peptide": {
        "a_count": 1,
        "c_count": 0,
        "c_terminus": "R",
        "d_count": 1,
        "e_count": 1,
        "f_count": 2,
        "g_count": 1,
        "h_count": 0,
        "id": 275019,
        "j_count": 2,
        "k_count": 0,
        "length": 15,
        "m_count": 2,
        "n_count": 2,
        "n_terminus": "A",
        "number_of_missed_cleavages": 0,
        "o_count": 0,
        "p_count": 0,
        "q_count": 0,
        "r_count": 1,
        "s_count": 1,
        "sequence": "AMGJMNSFVNDJFER",
        "t_count": 0,
        "u_count": 0,
        "v_count": 1,
        "w_count": 0,
        "weight": 1742.811994,
        "y_count": 0
    },
    "url": "http://localhost:3000/peptides/AMGJMNSFVNDJFER",
    proteins: [
        {
            "id": 2063,
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

### Search by weight
#### url
`http://localhost/api/peptides/search`    
#### method
`POST`    
#### additional headers
* Content-Type: application/json
* Accept: `application/json`, `application/octet-stream` or `text/plain` (This controlls the output, see below. `application/json` is the default and is used for unknown accept-formats)

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
* order_by: string, default: weight, possible values: `weight` `length` `number_of_missed_cleavages` `sequence`, default: `weight`, optional (ignored for `text/plain`-output)
* order_descendent: bool, default: false, optional

If `taxonomy_id`, `proteome_id`, `is_reviewed` are used together they will concanted with `and`.

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
    "is_reviewed": 1
}
```

#### output (application/json)
```json
{
    "count": 77,
    "peptides": [
        {
            "a_count": 0,
            "c_count": 0,
            "c_terminus": "K",
            "d_count": 0,
            "e_count": 0,
            "f_count": 0,
            "g_count": 0,
            "h_count": 1,
            "id": 7740,
            "j_count": 0,
            "k_count": 2,
            "length": 7,
            "m_count": 0,
            "n_count": 0,
            "n_terminus": "Y",
            "number_of_missed_cleavages": 1,
            "o_count": 0,
            "p_count": 0,
            "q_count": 0,
            "r_count": 0,
            "s_count": 1,
            "sequence": "YKHSVVK",
            "t_count": 0,
            "u_count": 0,
            "v_count": 2,
            "w_count": 0,
            "weight": 859.491573,
            "y_count": 1
        },
        ...
    ]
}
```
#### output (application/octet-stream)
Bytestream which contains one peptide in JSON-format per line.
```
{"sequence":"JJAMVWK","length":7,"number_of_missed_cleavages":0,"weight":859.498981153,"a_count":1,"c_count":0,"d_count":0,"e_count":0,"f_count":0,"g_count":0,"h_count":0,"j_count":2,"k_count":1,"m_count":1,"n_count":0,"o_count":0,"p_count":0,"q_count":0,"r_count":0,"s_count":0,"t_count":0,"u_count":0,"v_count":1,"w_count":1,"y_count":0,"n_terminus":"J","c_terminus":"K","id":1504140498,"peff_notation_of_modifications":""}
{"sequence":"WMAJJKV","length":7,"number_of_missed_cleavages":1,"weight":859.498981153,"a_count":1,"c_count":0,"d_count":0,"e_count":0,"f_count":0,"g_count":0,"h_count":0,"j_count":2,"k_count":1,"m_count":1,"n_count":0,"o_count":0,"p_count":0,"q_count":0,"r_count":0,"s_count":0,"t_count":0,"u_count":0,"v_count":1,"w_count":1,"y_count":0,"n_terminus":"W","c_terminus":"V","id":273131111,"peff_notation_of_modifications":""}
{"sequence":"MVJAJWK","length":7,"number_of_missed_cleavages":0,"weight":859.498981153,"a_count":1,"c_count":0,"d_count":0,"e_count":0,"f_count":0,"g_count":0,"h_count":0,"j_count":2,"k_count":1,"m_count":1,"n_count":0,"o_count":0,"p_count":0,"q_count":0,"r_count":0,"s_count":0,"t_count":0,"u_count":0,"v_count":1,"w_count":1,"y_count":0,"n_terminus":"M","c_terminus":"K","id":137426664,"peff_notation_of_modifications":""}
{"sequence":"AJWJVMK","length":7,"number_of_missed_cleavages":0,"weight":859498981153,"a_count":1,"c_count":0,"d_count":0,"e_count":0,"f_count":0,"g_count":0,"h_count":0,"j_count":2,"k_count":1,"m_count":1,"n_count":0,"o_count":0,"p_count":0,"q_count":0,"r_count":0,"s_count":0,"t_count":0,"u_count":0,"v_count":1,"w_count":1,"y_count":0,"n_terminus":"A","c_terminus":"K","id":3831436491,"peff_notation_of_modifications":""}
```
#### output (text/plain))
Text stream in fasta format.
```
>lcl|PEPTIDE_<ID>
JJAMVWK
>lcl|PEPTIDE_<ID>
WMAJJKV
>lcl|PEPTIDE_<ID>
MVJAJWK
>lcl|PEPTIDE_<ID>
AJWJVMK
```

### Calculate theoretical mass
#### url
`http://localhost/api/peptides/weight/<SEQUENCE>`
#### additional headers
* Content-Type: application/json
#### example
`http://localhost/api/peptides/weight/VQDDTK`
#### output
```json
{
    "weight": 704.334083868
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
  "id": 71399,
  "name": "Pallaviciniaceae",
  "parent": 186795
}
```

#### note
If the given ID was merged with another one, the resulting ID will differ. The ID `56884` from the example was merged with `71399`. So `71399` is reported.