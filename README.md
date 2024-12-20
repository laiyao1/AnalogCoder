# AnalogCoder: Analog Circuit Design via Training-Free Code Generation

New: Our paper has been accepted by **AAAI'25**.

<p align="center">
  <img src="AnalogCoder_label.png" alt="alt text"width="100">
</p>

The code implemented for AAAI'25 paper **AnalogCoder: Analog Circuit Design via Training-Free Code Generation**. 

[Yao Lai](https://laiyao1.github.io/)<sup>1</sup>, [Sungyoung Lee](https://brianlsy98.github.io/)<sup>2</sup>, [Guojin Chen](https://gjchen.me/)<sup>3</sup>, [Souradip Poddar](https://www.linkedin.com/in/souradip-poddar-52376212a/)<sup>2</sup>, [Mengkang Hu](https://aaron617.github.io/)<sup>1</sup>, [David Z. Pan](https://users.ece.utexas.edu/~dpan/)<sup>2</sup>, [Ping Luo](http://luoping.me/)<sup>1</sup>.

<sup>1</sup> The University of Hong Kong,
<sup>2</sup> The University of Texas at Austin,
<sup>3</sup> The Chinese University of Hong Kong.

  <a href="https://mmlab-hku.com/" target="_blank">
    <img src="hkummlab.png" alt="Image 1" style="width: 30%;"/>
  </a>

  <a href="https://www.cerc.utexas.edu/utda/" target="_blank">
    <img src="utda.jpg" alt="Image 2" style="width: 20%;"/>
  </a>



[[Paper](https://arxiv.org/pdf/2405.14918)]

# Introduction

<p align="center">
  <img src="teaser.png" alt="alt text"width="800">
</p>

**Analog circuit design** is a significant task in modern chip technology, focusing on selecting component types, connectivity, and parameters to ensure proper circuit functionality. Despite advances made by Large Language Models (LLMs) in digital circuit design, the **complexity** and **scarcity of data** in analog circuitry pose significant challenges. To mitigate these issues, we introduce **AnalogCoder**, the *first* training-free LLM agent for designing analog circuits that converts tasks into **Python code generation**. 

Main advantages of AnalogCoder: 
- AnalogCoder features a feedback-enhanced flow with crafted domain-specific prompts, enabling effective and automated design of analog circuits with a high success rate. 
- It proposes a circuit skill library to archive successful designs as reusable modular sub-circuits, simplifying composite circuit creation. 
- Extensive testing on a custom-designed benchmark of 24 analog circuit design tasks of varying difficulty shows that AnalogCoder successfully designed 20 circuits, outperforming existing methods. 


In summary, AnalogCoder can significantly improve the labor-intensive chip design process, enabling non-experts to efficiently design analog circuits.

# Evaluation of LLMs

**Ranking method**: # of solved (number of successfully solved circuit design problems) takes priority. If tied, higher average Pass@1 takes priority.

| LLM Model                              |      Avg. Pass@1 |      Avg. Pass@5 |     # of Solved |
|----------------------------------------|-----------------:|-----------------:|----------------:|
| Llama2-7B                              |              0.0 |              0.0 |               0 |
| Llama2-13B                             |              0.0 |              0.0 |               0 |
| SemiKong-8B*                           |              0.1 |              0.7 |               1 |
| Llama3-8B                              |              0.1 |              0.7 |               1 |
| Phi3-14B                               |              0.3 |              1.3 |               1 |
| Qwen-1.5-110B                          |              0.3 |              1.4 |               2 |
| CodeLlama-13B                          |              0.6 |              2.5 |               2 |
| Mistral-7B                             |              3.3 |              7.7 |               2 |
| Llama 2-70B                            |              5.1 |              9.8 |               3 |
| CodeQwen-1.5-7B                        |              1.1 |              5.6 |               4 |
| CodeLlama-34B                          |              1.9 |              7.4 |               4 |
| CodeLlama-7B                           |              2.4 |              9.0 |               4 |
| DeepSeek-Coder-33B                     |              4.0 |             10.2 |               4 |
| Llama3.1-8B                            |              4.9 |             12.9 |               4 |
| Magicoder-7B                           |              3.8 |             8.6 |               5 |
| Mixtral-8×7B                           |              5.6 |             12.4 |               5 |
| StarCoder2-15B-Instuct                 |              5.6 |             12.4 |               5 |
| CodeGeeX4-9B*                          |              10.6 |             20.3 |               6 |
| CodeLlama-70B                          |              3.2 |             12.2 |               7 |
| CodeGemma-7B                           |              6.9 |             17.0 |               7 |
| WizardCoder-33B                        |              7.1 |             16.9 |               7 |
| GPT-3.5 (w/o context)                  |              8.1 |             18.5 |               7 |
| GPT-3.5 (w/o flow)                     |             12.8 |             25.3 |               8 |
| Codestral-22B                          |             16.4 |             29.1 |               8 |
| GPT-3.5 (w/o CoT)                      |             19.4 |             26.3 |               8 |
| GLM-4                                  |             22.8 |             31.2 |               8 |
| GPT-3.5 (SPICE)                        |             13.9 |             26.9 |               9 |
| GPT-3.5                                |             21.4 |             35.0 |              10 |
| GPT-3.5 (fine-tune)                    |             28.1 |             39.6 |              10 |
| Llama3-70B                             |             28.8 |             36.4 |              11 |
| Gemini-1.0-Pro                         |             28.9 |             41.2 |              11 |
| Gemini-1.5-Flash                       |             35.7 |             40.6 |              11 |
| Qwen-2-72B                       |             9.3 |             26.6 |              12 |
| GPT-4o-mini                       |             34.9 |             41.7 |              12 |
| DeepSeek-V2-Chat                       |             38.6 |             44.3 |              13 |
| GPT-4 (w/o tool)                       |             51.1 |             57.7 |              14 |
| Llama3.1-70B                           |             25.4 |             42.6 |             14 |
| GPT-4o (w/o tool)                      |             54.2 |             58.9 |              15 |
| Claude-3.5-Sonnet (w/o tool)           |             58.1 |             60.7 |              15 |
| Mistral-Large-2                         |             28.6 |             51.0 |              17 |
| Gemini-1.5-Pro                         |             33.9 |             44.6 |              17 |
| DeepSeek-V2-Coder                      |             56.5 |             69.2 |              19 |
| Llama3.1-405B                           |             56.9 |             70.7 |             20 |
| AnalogCoder (GPT 4o-based)             |             66.1 |             75.9 |              20 |
| AnalogCoder (Claude 3.5 Sonnet-based)  |             76.1 |             86.3 |              22 |

\* without CoT (prompt to directly generate codes rather than devices) due to token limitations or its primary design for code generation.


Note:
1. All our results are reproducible.
2. The configuration of the environment does NOT require sudo privileges.




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
