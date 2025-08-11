---
language:
- ne
- en
license: mit
size_categories:
- 10K<n<100K
task_categories:
- translation
tags:
- translation
- transliteration
dataset_info:
  features:
  - name: unique_identifier
    dtype: string
  - name: native word
    dtype: string
  - name: english word
    dtype: string
  splits:
  - name: train
    num_bytes: 148156341
    num_examples: 2397414
  - name: validation
    num_bytes: 158422
    num_examples: 2804
  download_size: 86200245
  dataset_size: 148314763
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
  - split: validation
    path: data/validation-*
---
