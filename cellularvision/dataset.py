import numpy as np

from torch.utils.data import Dataset
from datasets import load_dataset, concatenate_datasets # type: ignore
from PIL import Image

from typing import Optional, Callable, List, Tuple, Any
from PIL.PngImagePlugin import PngImageFile

class PanNukeSegmentation(Dataset):
    def __init__(
        self, root: str, split: str,
        transform: Optional[Callable] = None,
        target_transform: Optional[Callable] = None
    ) -> None:
        self.root = root
        dataset = load_dataset("RationAI/PanNuke", cache_dir=self.root)
        if split == "train":
            self.dataset = concatenate_datasets([dataset["fold1"], dataset["fold2"]])
        elif split == "test": self.dataset = dataset["fold3"]
        else:
            raise ValueError(f"split `{split}` is not supported")
        
        self.categories = {
            0: "background",
            1: "neoplastic",
            2: "inflammatory",
            3: "connective",
            4: "dead",
            5: "epithelial"
        }
        
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self) -> int:
        return len(self.dataset)

    def __getitem__(self, index: int) -> Tuple[Any, Any]:
        image = self.dataset[index]["image"]
        segmentation = self._create_segmentation(
            self.dataset[index]["instances"], self.dataset["categories"]
        )
        if self.transform: image = self.transform(image)
        if self.target_transform:
            segmentation = self.target_transform(segmentation)

        return image, segmentation
    
    def _create_segmentation(
        self, instances: List[PngImageFile], categories: List[int]
    ) -> Image.Image:
        segmentation_mask = np.zeros(instances[0].size, dtype=np.uint8)
        for instance, category in zip(instances, categories):
            indices = (np.array(instance) == 1)
            segmentation_mask[indices] = category+1

        return Image.fromarray(segmentation_mask)
