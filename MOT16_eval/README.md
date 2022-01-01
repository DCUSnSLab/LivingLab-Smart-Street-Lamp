## Run the evaluation script
```
./eval.sh
```
NOTICE! This MOT16 evaluation is performed on the train split, NOT the test split, as the test ground truth is not publicly available. However, this is not an issue as the train dataset is actually never used for training.

```

CLEAR: ch_yolor-p6_deep_sort-pedestrianMOTA      MOTP      MODA      CLR_Re    CLR_Pr    MTR       PTR       MLR       sMOTA     CLR_TP    CLR_FN    CLR_FP    IDSW      MT        PT        ML        Frag
MOT16-02                           28.324    81.266    28.694    31.049    92.949    12.963    38.889    48.148    22.507    5537      12296     420       66        7         21        26        332
MOT16-04                           38.074    84.414    38.219    42.599    90.677    12.048    45.783    42.169    31.435    20259     27298     2083      69        10        38        35        595
MOT16-05                           48.709    75.08     49.941    63.831    82.129    24.8      60.8      14.4      32.803    4352      2466      947       84        31        76        18        266
MOT16-09                           57.656    81.018    58.379    71.219    84.725    40        56        4         44.137    3744      1513      675       38        10        14        1         146
MOT16-10                           48.336    76.06     49.091    57.526    87.212    22.222    61.111    16.667    34.564    7086      5232      1039      93        12        33        9         515
MOT16-11                           46.425    83.146    46.697    67.451    76.471    40.58     26.087    33.333    35.057    6188      2986      1904      25        28        18        23        108
MOT16-13                           39.31     76.855    39.799    44.55     90.363    20.561    41.121    38.318    28.999    5101      6349      544       56        22        44        41        311
COMBINED                           40.055    81.04     40.446    47.34     87.288    23.211    47.195    29.594    31.08     52267     58140     7612      431       120       244       153       2273

Identity: ch_yolor-p6_deep_sort-pedestrianIDF1      IDR       IDP       IDTP      IDFN      IDFP
MOT16-02                           33.241    22.172    66.376    3954      13879     2003
MOT16-04                           47.749    35.091    74.693    16688     30869     5654
MOT16-05                           39.185    34.82     44.801    2374      4444      2925
MOT16-09                           54.423    50.086    59.584    2633      2624      1786
MOT16-10                           50.883    42.223    64.012    5201      7117      2924
MOT16-11                           50.388    47.417    53.757    4350      4824      3742
MOT16-13                           45.183    33.729    68.415    3862      7588      1783
COMBINED                           45.878    35.38     65.235    39062     71345     20817

Count: ch_yolor-p6_deep_sort-pedestrianDets      GT_Dets   IDs       GT_IDs
MOT16-02                           5957      17833     39        54
MOT16-04                           22342     47557     64        83
MOT16-05                           5299      6818      43        125
MOT16-09                           4419      5257      29        25
MOT16-10                           8125      12318     59        54
MOT16-11                           8092      9174      81        69
MOT16-13                           5645      11450     59        107
COMBINED                           59879     110407    374       517


```
