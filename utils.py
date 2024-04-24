from tqdm import tqdm
import hashlib


def parse_url_from_cdx_line(line):
    # 将每一行分割成字段
    fields = line.strip().split(' ')

    url = fields[3][1:-2]

    return url


def extract_urls_from_cdx(cdx_file_path):
    urls = []
    with open(cdx_file_path, 'r', encoding='utf-8') as file:
        for line in tqdm(file):
            url = parse_url_from_cdx_line(line)
            urls.append(url)
    return urls


# 定义一个函数来生成URL的哈希码
def generate_url_hash(url):
    md5 = hashlib.md5()
    md5.update(url.encode('utf-8'))
    return md5.hexdigest()
