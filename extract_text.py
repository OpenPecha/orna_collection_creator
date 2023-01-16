import re
from pathlib import Path

from openpecha.utils import load_yaml

def get_vol_text(text_info):
    base_name = f"I1PD9{(int(text_info['vol'])+5845):04}"
    base_text = Path(f"./data/I9B2646BE_hfml/{base_name}.txt").read_text(encoding='utf-8')
    return base_text

def get_pages(vol_text):
    vol_text = re.sub("〕.+", "〕", vol_text)
    pages = {}
    cur_page = ""
    chunks = re.split("(〔.+?〕)", vol_text)
    for chunk in chunks[1:]:
        if re.search("〔(.+?)〕", chunk):
            img_number = re.search("〔(.+?)〕", chunk).group(1)
            cur_page += chunk
        else:
            cur_page += chunk
            pages[img_number] = cur_page
            cur_page = ""
    return pages


def get_text(text_info):
    text = ""
    vol_text = get_vol_text(text_info)
    pages = get_pages(vol_text)
    for img_number, page in pages.items():
        if int(img_number) >= int(text_info['img_loc_start']) and int(img_number) <= int(text_info['img_loc_end']):
            text += page
    return text


if __name__ == "__main__":
    non_derge_text_outline = load_yaml(Path('./data/non_derge_outline.yml'))
    for uuid,text_info in non_derge_text_outline.items():
        text = get_text(text_info)
        bdrc_id = text_info.get('bdrc_id', "")
        Path(f'./data/non_derge_texts/{uuid}-{bdrc_id}.txt').write_text(text, encoding='utf-8')

