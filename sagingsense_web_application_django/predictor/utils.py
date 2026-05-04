import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from tensorflow import keras

BASE_DIR = Path(__file__).resolve().parent
MODEL_ASSETS_DIR = BASE_DIR / "model_assets"

MODEL_REGISTRY = {
    "ripeness": {
        "display_name": "Banana Ripeness Scanner",
        "title": "Banana Ripeness Classification",
        "description": "Upload a banana fruit image to classify ripeness and receive a recommendation.",
        "model_path": MODEL_ASSETS_DIR / "ripeness" / "sagingsense_best_model.keras",
        "labels_path": MODEL_ASSETS_DIR / "ripeness" / "class_labels.json",
        "metadata_path": MODEL_ASSETS_DIR / "ripeness" / "model_metadata.json",
        "default_metadata": {
            "project_title": "SagingSense: A Convolutional Neural Network-Based Banana Ripeness Classification System for Fruit Quality Assessment",
            "best_model_name": "Not yet loaded",
            "image_size": 224,
            "number_of_classes": 4,
            "class_names": ["green", "overripe", "ripe", "rotten"],
        },
        "default_labels": {
            "0": "green",
            "1": "overripe",
            "2": "ripe",
            "3": "rotten",
        },
        "upload_prompt": "Upload a clear banana fruit image.",
        "badge": "Fruit Module",
    },
    "leaf_disease": {
        "display_name": "Banana Leaf Disease Scanner",
        "title": "Banana Leaf Disease Classification",
        "description": "Upload a banana leaf image to classify disease symptoms and receive a field guidance note.",
        "model_path": MODEL_ASSETS_DIR / "leaf_disease" / "banana_leaf_disease_best_model.keras",
        "labels_path": MODEL_ASSETS_DIR / "leaf_disease" / "class_labels.json",
        "metadata_path": MODEL_ASSETS_DIR / "leaf_disease" / "model_metadata.json",
        "default_metadata": {
            "project_title": "SagingSense PH: Banana Leaf Disease Classification Using Convolutional Neural Networks",
            "best_model_name": "Not yet loaded",
            "image_size": 224,
            "number_of_classes": 7,
            "class_names": [
                "Black Sigatoka",
                "Bract Mosaic",
                "Healthy Leaf",
                "Insect Pest",
                "Moko Disease",
                "Panama Disease",
                "Yellow Sigatoka",
            ],
        },
        "default_labels": {
            "0": "Black Sigatoka",
            "1": "Bract Mosaic",
            "2": "Healthy Leaf",
            "3": "Insect Pest",
            "4": "Moko Disease",
            "5": "Panama Disease",
            "6": "Yellow Sigatoka",
        },
        "upload_prompt": "Upload a clear banana leaf image.",
        "badge": "Leaf Module",
    },
}

_MODEL_CACHE: dict[str, dict[str, Any]] = {
    key: {"model": None, "labels": None, "metadata": None}
    for key in MODEL_REGISTRY
}


def get_module_config(module_key: str) -> dict:
    if module_key not in MODEL_REGISTRY:
        raise KeyError(f"Unknown module: {module_key}")
    return MODEL_REGISTRY[module_key]


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_metadata(module_key: str) -> dict:
    cache = _MODEL_CACHE[module_key]
    if cache["metadata"] is None:
        config = get_module_config(module_key)
        cache["metadata"] = _read_json(config["metadata_path"], config["default_metadata"])
    return cache["metadata"]


def get_class_labels(module_key: str) -> dict:
    cache = _MODEL_CACHE[module_key]
    if cache["labels"] is None:
        config = get_module_config(module_key)
        labels = _read_json(config["labels_path"], config["default_labels"])
        cache["labels"] = {int(key): value for key, value in labels.items()}
    return cache["labels"]


def get_model(module_key: str):
    cache = _MODEL_CACHE[module_key]
    if cache["model"] is None:
        config = get_module_config(module_key)
        model_path = config["model_path"]
        if not model_path.exists():
            raise FileNotFoundError(
                f"Missing trained model file: {model_path.relative_to(BASE_DIR)}"
            )
        cache["model"] = keras.models.load_model(model_path)
    return cache["model"]


def preprocess_image(image_path: str | Path, module_key: str) -> np.ndarray:
    metadata = get_metadata(module_key)
    image_size = int(metadata.get("image_size", 224))

    image = Image.open(image_path).convert("RGB")
    image = image.resize((image_size, image_size))
    image_array = np.array(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def get_ripeness_recommendation(predicted_class: str) -> str:
    class_name = predicted_class.lower()

    if "unripe" in class_name or "green" in class_name:
        return "The banana may not be ready for immediate consumption. It is better for storage or later use."
    if "ripe" in class_name and "over" not in class_name:
        return "The banana appears suitable for immediate consumption or selling."
    if "overripe" in class_name or "over ripe" in class_name:
        return "The banana should be consumed soon. It may be suitable for smoothies, baking, or processing."
    if "rotten" in class_name or "bad" in class_name or "decay" in class_name:
        return "The banana may no longer be suitable for consumption."

    return "The banana ripeness stage was classified. Please inspect the image and confidence score before making a final decision."


def get_leaf_recommendation(predicted_class: str) -> str:
    name = predicted_class.lower()

    if "healthy" in name:
        return "The leaf appears healthy based on the trained model."
    if "sigatoka" in name:
        return "The leaf shows symptoms similar to Sigatoka. Field verification and disease management are recommended."
    if "mosaic" in name:
        return "The leaf shows mosaic-like symptoms. Inspect surrounding plants and verify possible viral spread."
    if "panama" in name or "fusarium" in name:
        return "The model suggests Panama or Fusarium-related symptoms. Immediate field inspection is recommended."
    if "moko" in name:
        return "The leaf may be associated with Moko disease. Check plant condition and nearby spread indicators."
    if "pest" in name or "insect" in name:
        return "The model suggests pest-related damage. Inspect for feeding marks and visible insect activity."

    return "The leaf shows abnormal symptoms. Manual inspection is recommended."


def get_recommendation(module_key: str, predicted_class: str) -> str:
    if module_key == "ripeness":
        return get_ripeness_recommendation(predicted_class)
    if module_key == "leaf_disease":
        return get_leaf_recommendation(predicted_class)
    return "Prediction complete."


def predict_image(module_key: str, image_path: str | Path) -> dict:
    model = get_model(module_key)
    labels = get_class_labels(module_key)

    image_array = preprocess_image(image_path, module_key)
    prediction = model.predict(image_array, verbose=0)[0]

    predicted_index = int(np.argmax(prediction))
    predicted_class = labels.get(predicted_index, f"Class {predicted_index}")
    confidence = float(np.max(prediction))

    all_probabilities = {
        labels.get(index, f"Class {index}"): float(probability)
        for index, probability in enumerate(prediction)
    }

    return {
        "predicted_class": predicted_class,
        "confidence": confidence,
        "all_probabilities": all_probabilities,
        "recommendation": get_recommendation(module_key, predicted_class),
    }


def get_status_summary(module_key: str) -> dict:
    config = get_module_config(module_key)
    metadata = get_metadata(module_key)
    labels = get_class_labels(module_key)

    return {
        "module_key": module_key,
        "display_name": config["display_name"],
        "title": config["title"],
        "description": config["description"],
        "badge": config["badge"],
        "upload_prompt": config["upload_prompt"],
        "model_file_exists": config["model_path"].exists(),
        "labels_file_exists": config["labels_path"].exists(),
        "metadata_file_exists": config["metadata_path"].exists(),
        "best_model_name": metadata.get("best_model_name", metadata.get("model_name", "Unknown")),
        "image_size": metadata.get("image_size", 224),
        "class_names": metadata.get("class_names", list(labels.values())),
        "asset_dir": str(config["model_path"].parent.relative_to(BASE_DIR)),
        "model_filename": config["model_path"].name,
    }


def get_all_module_statuses() -> list[dict]:
    return [get_status_summary(module_key) for module_key in MODEL_REGISTRY]
