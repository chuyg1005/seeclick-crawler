from tqdm import tqdm


def extract_urls_from_cdx(cdx_file_path):
    urls = []
    with open(cdx_file_path, 'r', encoding='utf-8') as file:
        for line in tqdm(file):
            # 将每一行分割成字段
            fields = line.strip().split(' ')

            url = fields[3][1:-2]

            urls.append(url)
    return urls


