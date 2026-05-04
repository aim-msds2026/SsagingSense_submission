from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import ImageUploadForm
from .utils import get_all_module_statuses, get_module_config, get_status_summary, predict_image


def validate_module_key(module_key: str) -> None:
    try:
        get_module_config(module_key)
    except KeyError as error:
        raise Http404(f"Unknown scanner module: {module_key}") from error


def home(request):
    return render(
        request,
        "predictor/home.html",
        {
            "modules": get_all_module_statuses(),
        },
    )


def scanner(request, module_key: str):
    validate_module_key(module_key)
    status = get_status_summary(module_key)
    return render(
        request,
        "predictor/scanner.html",
        {
            "form": ImageUploadForm(),
            "status": status,
            "module_key": module_key,
        },
    )


def predict_module(request, module_key: str):
    validate_module_key(module_key)
    status = get_status_summary(module_key)

    if request.method != "POST":
        return redirect("predictor:scanner", module_key=module_key)

    form = ImageUploadForm(request.POST, request.FILES)

    if not form.is_valid():
        messages.error(request, "Please upload a valid image file.")
        return render(
            request,
            "predictor/scanner.html",
            {
                "form": form,
                "status": status,
                "module_key": module_key,
            },
        )

    uploaded_image = form.cleaned_data["image"]
    upload_dir = Path(settings.MEDIA_ROOT) / module_key
    upload_dir.mkdir(parents=True, exist_ok=True)

    extension = Path(uploaded_image.name).suffix.lower() or ".jpg"
    safe_name = f"{uuid4().hex}{extension}"
    saved_path = upload_dir / safe_name

    with open(saved_path, "wb+") as destination:
        for chunk in uploaded_image.chunks():
            destination.write(chunk)

    image_url = settings.MEDIA_URL + f"{module_key}/{safe_name}"

    try:
        prediction = predict_image(module_key, saved_path)
    except FileNotFoundError as error:
        messages.error(request, str(error))
        return render(
            request,
            "predictor/scanner.html",
            {
                "form": ImageUploadForm(),
                "status": status,
                "module_key": module_key,
                "uploaded_preview_url": image_url,
                "setup_error": str(error),
            },
        )
    except Exception as error:
        messages.error(request, f"Prediction failed: {error}")
        return render(
            request,
            "predictor/scanner.html",
            {
                "form": ImageUploadForm(),
                "status": status,
                "module_key": module_key,
                "uploaded_preview_url": image_url,
                "setup_error": f"Prediction failed: {error}",
            },
        )

    sorted_probabilities = sorted(
        prediction["all_probabilities"].items(),
        key=lambda item: item[1],
        reverse=True,
    )

    return render(
        request,
        "predictor/result.html",
        {
            "prediction": prediction,
            "image_url": image_url,
            "probabilities": sorted_probabilities,
            "status": status,
            "module_key": module_key,
        },
    )
