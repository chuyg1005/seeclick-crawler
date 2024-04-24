## GUI Grounding Pre-training Data for SeeClick

> 该项目是Seeclick的GUI Grounding Pre-training数据集构建项目，以Common Crawl数据集作为URL来源，通过selenium爬取网页数据，提取其中的网页元素Grounding数据，用于Seeclick的持续预训练

这是项目的中文介绍。

[English README](README.md) 

### 项目结构

* preprocess_cdx.py: 从Common Crawl数据集中提取URL并去重
* crawel.py: 爬取逻辑实现，通过selenium爬取网页数据并提取Grounding数据
* main.py: 爬虫主程序，通过分治策略并行爬取数据
* utils.py: 工具代码

### 如何使用

1. 预先准备好[Common Crawl数据集](https://commoncrawl.org/) ，将其解压到特定目录
2. 安装Chrome浏览器和相应版本的ChromeDriver
3. 安装python依赖

```shell
pip install -r requirements.txt
```

4. 运行preprocess_cdx.py，提取URL并去重

```shell
python preprocess_cdx.py --cdx_file_path /path/to/cdx --unique_cdx_file_path /path/to/unique_cdx
```

5. 运行main.py，爬取数据

```shell
python main.py --cdx_file_path /path/to/unique_cdx --out_root /path/to/output --num_workers 20
``` 