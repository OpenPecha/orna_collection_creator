from openpecha.utils import load_yaml, dump_yaml


from pathlib import Path
from strsimpy.cosine import Cosine



BDRC_OUTLINE = load_yaml(Path('./MW1PD95844.yaml'))

def get_similarity(title1, title2):
    cosine = Cosine(2)
    title1_profile = cosine.get_profile(title1)
    title2_profile = cosine.get_profile(title2)
    return cosine.similarity_profiles(title1_profile, title2_profile)

def is_same_text(old_outline_text, new_outline_text):
    old_outline_text_title = old_outline_text['pedurma_title']
    new_outline_text_title = new_outline_text['pref_title']
    title_similarity = get_similarity(old_outline_text_title, new_outline_text_title)
    old_outline_text_span = f"{old_outline_text['vol']}/{old_outline_text['img_loc_start']}"
    new_outline_text_span = f"{new_outline_text['outline_span']['vol']['start']}/{new_outline_text['outline_span']['image_span']['start']}"
    if title_similarity > 0.9 or old_outline_text_span==new_outline_text_span:
        return True
    return False

def get_text(old_outline_text):
    bdrc_rid = ''
    for uuid, new_outline_text in BDRC_OUTLINE.items():
        if is_same_text(old_outline_text, new_outline_text):
            bdrc_rid = new_outline_text['bdrc_rid']
            break
    old_outline_text['bdrc_id'] = bdrc_rid
    return old_outline_text

def filter_non_derge_vol_outline(outline, non_derge_vols):
    non_derge_text_vol_outline = {}
    for uuid, text in outline.items():
        if text['vol'] in non_derge_vols:
            if text['rkts_id'] and "D" in text['rkts_id']:
                continue
            non_derge_text_vol_outline[uuid] = get_text(text)
    return non_derge_text_vol_outline

if __name__ == "__main__":
    pedurma_outline = load_yaml(Path('./data/tengyur_pedurma_outline.yml'))
    non_derge_vols = Path('./data/non_derge_vols.txt').read_text(encoding='utf=8').splitlines()
    non_derge_text_outline = filter_non_derge_vol_outline(pedurma_outline, non_derge_vols)
    dump_yaml(non_derge_text_outline, Path('./data/non_derge_outline.yml'))
