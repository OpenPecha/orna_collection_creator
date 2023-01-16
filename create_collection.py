import csv

from pathlib import Path

from openpecha.core.ids import get_id
from openpecha.core.pecha import OpenPechaFS
from openpecha.utils import dump_yaml

class Views:

    def __init__(self, description, serializer) -> None:
        self.description = description
        self.serializer = serializer

    
class Pecha:

    def __init__(self, id, title, bdrc_id, volume_number, base_name) -> None:
        self.id = id
        self.title = title
        self.bdrc_id = bdrc_id
        self.volume_number = volume_number
        self.base_name = base_name

class Collection:

    def __init__(self, id, title, pechas, views, collection_dir) -> None:
        self.id = id
        self.title = title
        self.views = views
        self.pechas = pechas
        self.collection_dir = collection_dir

    def save_catalog(self, view_name):
        catalog_file_path = self.collection_dir / f"Catelog_{view_name}.csv"
        field_names = ['FILE NAME', 'TITLE', 'OP ID', 'BDRC ID', 'VOLUME NUMBER']
        pechas = []
        for pecha in self.pechas:
            cur_pecha_infos = [
                pecha.base_name,
                pecha.title,
                pecha.id,
                pecha.bdrc_id,
                pecha.image_group_id,
                pecha.volume_number
            ]
            pechas.append(cur_pecha_infos)
        with open(catalog_file_path, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)   
            csvwriter.writerow(field_names) 
        
            # writing the data rows 
            csvwriter.writerows(pechas)
    
    def save_collection_file(self):
        collection_file_path = self.collection_dir / f"{self.id}.yml"
        collection = {
            'views': self.views,
            'collection': {
                'id': self.id,
                'title': self.title,
                'pechas': self.pechas
            }
        }
        dump_yaml(collection, collection_file_path)







def get_views():
    views = [
        Views(description='Plain base', serializer=None),
        Views(description='HFML', serializer='https://github.com/OpenPecha/Toolkit/blob/master/openpecha/serializers/hfml.py')
    ]
    return views

def get_pecha(opf):
    
    pecha = Pecha(
        id = opf.id,
        title = opf.meta.source_metadata['text_title'],
        bdrc_id = opf.meta.source_metadata['bdrc_id'],
        volume_number = opf.meta.source_metadata['pedurma_volume_number'],
        base_name = opf.bases[0]
    )

    return pecha


def get_pechas():
    pechas = []
    pecha_paths = list(Path('./data/non_derge_opfs/').iterdir())
    pecha_paths.sort()
    for pecha_path in pecha_paths:
        opf =OpenPechaFS(path=pecha_path)
        pechas.append(get_pecha(opf))
    return pechas


def get_collection(collection_title):
    collection_id = get_id(prefix="C", length=8)
    views = get_views()
    pechas = get_pechas()

    collection = Collection(
        id=collection_id,
        title=collection_title,
        views=views,
        pechas=pechas
    )
    
    return collection


def save_collection(collection, collection_path):
    dump_yaml(collection.dict(exclude_none=True), collection_path)
    return collection_path


