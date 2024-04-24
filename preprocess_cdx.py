from tqdm import tqdm
from urllib.parse import urlparse
import random
import argparse
from utils import parse_url_from_cdx_line




def get_host_from_url(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname:
        return parsed_url.hostname
    else:
        return None


def distinct_urls_from_cdx(cdx_file_path, unique_cdx_file_path):
    domain_dict = {}
    with open(cdx_file_path, 'r', encoding='utf-8') as in_file:
        for line in tqdm(in_file):
            url = parse_url_from_cdx_line(line)
            host = get_host_from_url(url)
            if host in domain_dict:
                domain_dict[host].append(line)
            else:
                domain_dict[host] = [line]
    with open(unique_cdx_file_path, 'w', encoding='utf-8') as out_file:
        for host in tqdm(domain_dict):
            line = random.choice(domain_dict[host])
            out_file.write(line)


def main(args):
    random.seed(args.seed)
    cdx_file_path = args.cdx_file_path
    if args.unique_cdx_file_path is None:
        unique_cdx_file_path = cdx_file_path + '-unique'
    else:
        unique_cdx_file_path = args.unique_cdx_file_path
    distinct_urls_from_cdx(cdx_file_path, unique_cdx_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cdx_file_path', type=str, default='/cpfs01/user/chengkanzhi/url-base/cdx-merged')
    parser.add_argument('--unique_cdx_file_path', type=str, default=None)
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()
    main(args)
