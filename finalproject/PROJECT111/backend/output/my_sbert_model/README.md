---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- dense
- generated_from_trainer
- dataset_size:1000
- loss:CosineSimilarityLoss
base_model: snunlp/KR-SBERT-V40K-klueNLI-augSTS
widget:
- source_sentence: '충청북도 거주, 3년차 개발자, 스택: Spring Boot. 추가: 혼합'
  sentences:
  - '부산광역시 지역 프로젝트, 요구 스택: JPA, 필요 경력: 5년차 이상. 특이사항: CS 전공자 필수, 팀 협업'
  - '충청북도 지역 프로젝트, 요구 스택: JPA, 필요 경력: 1년차 이상. 특이사항: 프로젝트 중심'
  - '제주특별자치도 지역 프로젝트, 요구 스택: Next.js, 필요 경력: 4년차 이상. 특이사항: 프로젝트 중심'
- source_sentence: '전라북도 거주, 7년차 이상 개발자, 스택: Java. 추가: 스터디, 온라인 중심'
  sentences:
  - '전라북도 지역 프로젝트, 요구 스택: React, 필요 경력: 4년차 이상. 특이사항: 리서치 중심, 팀 협업'
  - '부산광역시 지역 프로젝트, 요구 스택: JPA, 필요 경력: 4년차 이상. 특이사항: CS 전공자 필수, 프로젝트 중심'
  - '경기도 지역 프로젝트, 요구 스택: Python (Pandas), 필요 경력: 4년차 이상. 특이사항: 토이 프로젝트, 팀 협업'
- source_sentence: '재택 거주, 1년차 개발자, 스택: Django. 추가: 오프라인 중심'
  sentences:
  - '재택 지역 프로젝트, 요구 스택: React, 필요 경력: 5년차 이상. 특이사항: 비전공자 환영, 프로젝트 중심'
  - '경상남도 지역 프로젝트, 요구 스택: Flask, 필요 경력: 7년차 이상 이상. 특이사항: CS 전공자 필수, 팀 협업'
  - '대구광역시 지역 프로젝트, 요구 스택: React, 필요 경력: 3년차 이상. 특이사항: 스터디, 프로젝트 중심'
- source_sentence: '제주특별자치도 거주, 1년차 개발자, 스택: Django. 추가: 리서치 중심, 오프라인 중심'
  sentences:
  - '제주특별자치도 지역 프로젝트, 요구 스택: Java, 필요 경력: 5년차 이상. 특이사항: 리서치 중심, 팀 협업'
  - '서울특별시 지역 프로젝트, 요구 스택: React, 필요 경력: 5년차 이상. 특이사항: 스터디, 팀 협업'
  - '경기도 지역 프로젝트, 요구 스택: HTML/CSS/JS, 필요 경력: 4년차 이상. 특이사항: 프로덕트 중심, 프로젝트 중심'
- source_sentence: '경상북도 거주, 2년차 개발자, 스택: Java. 추가: 비전공자, 온라인 중심'
  sentences:
  - '제주특별자치도 지역 프로젝트, 요구 스택: React, 필요 경력: 5년차 이상. 특이사항: 리서치 중심, 팀 협업'
  - '강원도 지역 프로젝트, 요구 스택: JPA, 필요 경력: 2년차 이상. 특이사항: 비전공자 환영, 프로젝트 중심'
  - '경상북도 지역 프로젝트, 요구 스택: Java, 필요 경력: 1년차 이상. 특이사항: 스터디, 프로젝트 중심'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer based on snunlp/KR-SBERT-V40K-klueNLI-augSTS

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [snunlp/KR-SBERT-V40K-klueNLI-augSTS](https://huggingface.co/snunlp/KR-SBERT-V40K-klueNLI-augSTS). It maps sentences & paragraphs to a 768-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [snunlp/KR-SBERT-V40K-klueNLI-augSTS](https://huggingface.co/snunlp/KR-SBERT-V40K-klueNLI-augSTS) <!-- at revision 92c6c2c7032f680bff0f9f0c63fadd3f97e635b2 -->
- **Maximum Sequence Length:** 128 tokens
- **Output Dimensionality:** 768 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/UKPLab/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 128, 'do_lower_case': False, 'architecture': 'BertModel'})
  (1): Pooling({'word_embedding_dimension': 768, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    '경상북도 거주, 2년차 개발자, 스택: Java. 추가: 비전공자, 온라인 중심',
    '경상북도 지역 프로젝트, 요구 스택: Java, 필요 경력: 1년차 이상. 특이사항: 스터디, 프로젝트 중심',
    '강원도 지역 프로젝트, 요구 스택: JPA, 필요 경력: 2년차 이상. 특이사항: 비전공자 환영, 프로젝트 중심',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 768]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.9891, 0.0492],
#         [0.9891, 1.0000, 0.0300],
#         [0.0492, 0.0300, 1.0000]])
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 1,000 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                         | sentence_1                                                                         | label                                                          |
  |:--------|:-----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                             | string                                                                             | float                                                          |
  | details | <ul><li>min: 19 tokens</li><li>mean: 25.76 tokens</li><li>max: 33 tokens</li></ul> | <ul><li>min: 26 tokens</li><li>mean: 32.16 tokens</li><li>max: 42 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.42</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                       | sentence_1                                                                             | label            |
  |:-----------------------------------------------------------------|:---------------------------------------------------------------------------------------|:-----------------|
  | <code>경기도 거주, 1년 이하 개발자, 스택: Django. 추가: CS 전공자, 오프라인 중심</code>  | <code>대구광역시 지역 프로젝트, 요구 스택: Flask, 필요 경력: 4년차 이상. 특이사항: 팀 협업</code>                    | <code>0.4</code> |
  | <code>충청북도 거주, 7년차 이상 개발자, 스택: React. 추가: 비전공자 환영, 온라인 중심</code> | <code>충청북도 지역 프로젝트, 요구 스택: Spring Boot, 필요 경력: 4년차 이상. 특이사항: CS 전공자 필수, 프로젝트 중심</code> | <code>0.0</code> |
  | <code>경기도 거주, 1년 이하 개발자, 스택: Flask. 추가: 토이 프로젝트, 오프라인 중심</code>  | <code>경기도 지역 프로젝트, 요구 스택: Spring Boot, 필요 경력: 3년차 이상. 특이사항: 리서치 중심, 프로젝트 중심</code>     | <code>0.0</code> |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `num_train_epochs`: 4
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: no
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 4
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `use_ipex`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: False
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Framework Versions
- Python: 3.12.7
- Sentence Transformers: 5.1.1
- Transformers: 4.56.2
- PyTorch: 2.8.0
- Accelerate: 1.11.0
- Datasets: 4.3.0
- Tokenizers: 0.22.1

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->