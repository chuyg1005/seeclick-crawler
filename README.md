## GUI Grounding Pre-training Data for SeeClick

> This project is the GUI Grounding Pre-training dataset construction project for SeeClick, using the Common Crawl dataset as the source of URLs, crawling web page data using Selenium, and extracting web element grounding data for continuous pre-training of SeeClick.

This is the English introduction of the project.

[中文 README](README_zh.md)

### Project Structure

* preprocess_cdx.py: Extract URLs from the Common Crawl dataset and remove duplicates.
* crawel.py: Implementation of crawling logic, crawling web page data using Selenium, and extracting grounding data.
* main.py: Main program for the web crawler, parallel crawling of data using a divide-and-conquer strategy.
* utils.py: Utility code.

### How to Use

1. Preparing the [Common Crawl dataset](https://commoncrawl.org/) in advance, and unzip it to a specific directory.
2. Install Chrome browser and the corresponding version of ChromeDriver.
3. Install Python dependencies.

```bash
pip install -r requirements.txt
``` 

4. Run preprocess_cdx.py to extract URLs and remove duplicates.

```bash
python preprocess_cdx.py --cdx_file_path /path/to/cdx --unique_cdx_file_path /path/to/unique_cdx
```

5. Run main.py to crawl data.

```bash
python main.py --cdx_file_path /path/to/unique_cdx --out_root /path/to/output --num_workers 20
```