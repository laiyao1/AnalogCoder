# AnalogCoder: Analog Circuit Design via Training-Free Code Generation

<p align="center">
  <img src="AnalogCoder_label.png" alt="alt text"width="150">
</p>

The code implement for paper **AnalogCoder: Analog Circuit Design via Training-Free Code Generation**. 

[[Paper](https://arxiv.org/pdf/2405.14918)]

# Introduction

<p align="center">
  <img src="teaser.png" alt="alt text"width="600">
</p>

**Analog circuit design** is a significant task in modern chip technology, focusing on selecting component types, connectivity, and parameters to ensure proper circuit functionality. Despite advances made by Large Language Models (LLMs) in digital circuit design, the **complexity** and **scarcity of data** in analog circuitry pose significant challenges. To mitigate these issues, we introduce **AnalogCoder**, the *first* training-free LLM agent for designing analog circuits that converts tasks into **Python code generation**. 

Main advantages of AnalogCoder: 
- AnalogCoder features a feedback-enhanced flow with crafted domain-specific prompts, enabling effective and automated design of analog circuits with a high success rate. 
- It proposes a circuit skill library to archive successful designs as reusable modular sub-circuits, simplifying composite circuit creation. 
- Extensive testing on a custom-designed benchmark of 24 analog circuit design tasks of varying difficulty shows that AnalogCoder successfully designed 20 circuits, outperforming existing methods. AnalogCoder can significantly improve the labor-intensive chip design process, enabling non-experts to efficiently design analog circuits.


# Installation
AnalogCoder requires Python ≥ 3.10, PySpice ≥ 1.5, and openai >= 1.16.1. 

## Python Install
```
git clone https://github.com/anonyanalog/AnalogCoder
conda env create -f environment.yml
conda activate analog
```

## Environment Check
To ensure the current environment is functional, the following tests can be performed:

```
cd sample_design
python test_all_sample_design.py
```

When the program finishes running, if `All tasks passed` is displayed, it indicates that the environment is normal.

Otherwise, it will display `Please check your environment and try again`. It means you should check the configuration of the current Python environment, especially the settings related to PySpice.





# Quick Start
You can directly run the following code for quick start.
```
python gpt_run.py --task_id=1 --api_key="[OPENAI_API]" --num_per_task=1
```
which will generate one circuit based on task 1.


# Benchmark
- Task descriptions are in `problem_set.tsv`.
- Sample circuits are in directory `sample_design`.
- Test-benches are in directory `problem_check`.

# Citation
If you find our work beneficial, we would be grateful if you considered citing our paper.


```
@misc{lai2024analogcoder,
      title={AnalogCoder: Analog Circuit Design via Training-Free Code Generation}, 
      author={Yao Lai and Sungyoung Lee and Guojin Chen and Souradip Poddar and Mengkang Hu and David Z. Pan and Ping Luo},
      year={2024},
      eprint={2405.14918},
      archivePrefix={arXiv},
      primaryClass={cs.LG}
}
```