
SPOKE graph properties: 2153759 nodes, 5475334 edges

Most nodes have no out-edges - 1791381 nodes have no out-edges.
2061691 nodes have no in-edges.

Filtering for only nodes that have edges (in or out), we only have 391775 nodes.

Node types:
{1: ':Gene',
 2: ':SideEffect',
 3: ':BiologicalProcess',
 4: ':MolecularFunction',
 5: ':Compound',
 6: ':CellularComponent',
 7: ':PharmacologicClass',
 8: ':Pathway',
 9: ':Disease',
 10: ':Symptom',
 11: ':Anatomy',
 12: ':Protein',
 13: ':Food'}

Node type counts:
{1: 21639,
 2: 6061,
 3: 13394,
 4: 3479,
 5: 1894261,
 6: 1739,
 7: 1750,
 8: 3271,
 9: 9542,
 10: 467,
 11: 14868,
 12: 182391,
 13: 897}

Node type counts only for nodes that are connected:
{1: 19576,
 2: 3874,
 3: 13321,
 4: 3459,
 5: 286735,
 6: 1737,
 7: 1748,
 8: 3163,
 9: 9537,
 10: 373,
 11: 13270,
 12: 34139,
 13: 843}


Edge types:
{1: 'EXPRESSES_AeG',
 2: 'PARTICIPATES_GpMF',
 3: 'REGULATES_GrG',
 4: 'INTERACTS_GiG',
 5: 'DOWNREGULATES_AdG',
 6: 'PARTICIPATES_GpBP',
 7: 'UPREGULATES_AuG',
 8: 'COVARIES_GcG',
 9: 'PARTICIPATES_GpPW',
 10: 'DOWNREGULATES_DdG',
 11: 'PARTICIPATES_GpCC',
 12: 'DOWNREGULATES_CdG',
 13: 'UPREGULATES_DuG',
 14: 'UPREGULATES_CuG',
 15: 'RESEMBLES_CrC',
 16: 'ASSOCIATES_DaG',
 17: 'TREATS_CtD',
 18: 'INCLUDES_PCiC',
 19: 'PALLIATES_CpD',
 20: 'LOCALIZES_DlA',
 21: 'INTERACTS_PiP',
 22: 'PRESENTS_DpS',
 23: 'ISA_AiA',
 24: 'CONTAINS_AcA',
 25: 'PARTOF_ApA',
 26: 'TRANSLATEDFROM_PtG',
 27: 'INTERACTS_CiP',
 28: 'ISA_DiD',
 29: 'CONTAINS_DcD',
 30: 'BINDS_CbP',
 31: 'CONTRAINDICATES_CcD',
 32: 'AFFECTS_CamG',
 33: 'RESEMBLES_DrD',
 34: 'CONTAINS_FcCM',
 35: 'CAUSES_CcSE'}

Edge type counts:
{1: 457170,
 2: 136616,
 7: 55364,
 3: 265226,
 4: 146754,
 5: 75295,
 6: 767490,
 8: 61629,
 9: 146316,
 10: 6978,
 11: 115904,
 12: 21076,
 16: 1085533,
 14: 18736,
 15: 6486,
 13: 6774,
 17: 32383,
 18: 31476,
 20: 39762,
 32: 3868,
 19: 190,
 31: 20640,
 21: 1069128,
 22: 24115,
 23: 18644,
 24: 18729,
 25: 9757,
 26: 33799,
 27: 2862,
 28: 10978,
 29: 11134,
 33: 64716,
 30: 545513,
 34: 121187,
 35: 43973}


Timing: 5min 54s to load graph and run pagerank three times
2min 24s to load graph
4.65 s to run pagerank on graph
The most costly operation is actually symmetrize_matrix, which takes 3min 7s. This is probably being done in a very inefficient way.

Update: 2min 54s total
