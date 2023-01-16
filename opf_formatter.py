from pathlib import Path
import re

from openpecha.formatters.hfml import HFMLFormatter
from openpecha.core.pecha import OpenPechaFS
from openpecha.core.ids import get_initial_pecha_id
from openpecha.core.layer import Layer, LayerEnum
from openpecha.core.annotations import Pagination, Span
from openpecha.utils import load_yaml
from extract_text import get_pages

BDRC_OUTLINE = load_yaml(Path('./data/non_derge_outline.yml'))

def get_source_metadata(old_bdrc_id, new_bdrc_id):
    text_info = BDRC_OUTLINE.get(old_bdrc_id, {})
    if text_info:
        source_metadata = {
            'text_title': text_info['pedurma_title'],
            'pedurma_volume_number': text_info['vol'],
            'bdrc_rid': new_bdrc_id
        }
    return source_metadata, text_info['vol']

def get_page_annotation(char_walker, page_text, img_number, img_grp):
    img_reference = f"{img_grp}{int(img_number):04}.jpg"
    page_end = char_walker + len(page_text)
    pg_ann = Pagination(
        span=Span(start=char_walker, end=page_end),
        imgnum=int(img_number),
        reference=img_reference,
    )
    return pg_ann

def parse_hfml(hfml, img_grp):
    base_text = ""
    char_walker = 0
    pagination = Layer(annotation_type=LayerEnum.pagination)

    pages = get_pages(hfml)

    for img_number, page_text in pages.items():
        page_text = re.sub('〔[𰵀-󴉱]?\d+〕', "", page_text)
        page_text = page_text.strip()
        page_text += "\n\n\n"
        base_text += page_text
        page_annotation = get_page_annotation(char_walker, page_text, img_number, img_grp)
        pagination.set_annotation(page_annotation)
        char_walker = len(base_text)
    return base_text, pagination

def rm_noise(hfml):
    noises = [
        "'",
        "∶", 
        "‘", 
        "|", 
        "¯", 
        "—", 
        "༼", 
        "༽",
        "\/",
        ]

    for noise in noises:
        hfml = re.sub(noise, "", hfml)
    return hfml

def get_img_grp(volume_number):
    img_grp = f"I1PD9{5845+int(volume_number)}"
    return img_grp


def get_opf(pecha_path, hfml_path, old_bdrc_id, new_bdrc_id):
    pecha = OpenPechaFS(path=pecha_path)
    if new_bdrc_id:
        base_name = new_bdrc_id
    else:
        base_name = old_bdrc_id
    hfml = hfml_path.read_text(encoding='utf-8')
    hfml = rm_noise(hfml)
    pecha.meta.source_metadata, vol_number = get_source_metadata(old_bdrc_id, new_bdrc_id)
    img_grp = get_img_grp(vol_number)
    base_text, pagination = parse_hfml(hfml, img_grp)
    pecha.bases[base_name] = base_text
    pecha.layers[base_name][pagination.annotation_type] = pagination
    pecha.meta.bases[base_name] = {
        'base_file': f"{base_name}.txt",
        'statistics': {
            'ocr_word_median_confidence_index': 0.9999999,
            'ocr_word_mean_confidence_index': 0.9755740258134236

        }        
        }
    
    pecha.save()

def get_bdrc_ids(file_name):
    old_bdrc_id = ""
    new_bdrc_id = ""
    file_name_parts = re.split("-", file_name)
    if len(file_name_parts) >1:
        old_bdrc_id= file_name_parts[0]
        new_bdrc_id=file_name_parts[1]
    else:
        old_bdrc_id=file_name_parts[0]
    return old_bdrc_id, new_bdrc_id



if __name__ == "__main__":
    opf_dir = './data/non_derge_opfs'
    hfml_paths = list(Path('./data/non_derge_texts').iterdir())
    hfml_paths.sort()
    for hfml_path in hfml_paths:
        old_bdrc_id, new_bdrc_id = get_bdrc_ids(hfml_path.stem)
        pecha_id = get_initial_pecha_id()
        opf_path = f"{opf_dir}/{pecha_id}/{pecha_id}.opf"
        get_opf(opf_path,hfml_path,old_bdrc_id,new_bdrc_id)
        break


