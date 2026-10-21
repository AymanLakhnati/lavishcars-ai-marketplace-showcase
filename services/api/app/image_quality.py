"""Local, explainable image checks; never infer vehicle identity or specifications."""

from PIL import ImageFilter, ImageStat


def inspect_image(image):
    width, height = image.size
    sample = image.convert("L")
    sample.thumbnail((400, 400))
    brightness = ImageStat.Stat(sample).mean[0]
    edges = sample.filter(ImageFilter.FIND_EDGES)
    if edges.width > 4 and edges.height > 4:
        edges = edges.crop((2, 2, edges.width - 2, edges.height - 2))
    edge_variance = ImageStat.Stat(edges).var[0]
    warnings = []
    if min(width, height) < 400:
        warnings.append("Low resolution: use a photo at least 400 pixels on each side.")
    if brightness < 35:
        warnings.append(
            "This image is very dark. Check whether vehicle details are visible."
        )
    if brightness > 235:
        warnings.append("This image is very bright. Check for lost highlight detail.")
    if edge_variance < 25:
        warnings.append(
            "Low edge detail: this may be a blurred or very plain image. Review it yourself."
        )
    score = round(
        min(40, width * height / 30000)
        + max(0, 30 - abs(brightness - 125) / 4)
        + min(30, edge_variance / 20)
    )
    return {
        "mode": "local-image-heuristics",
        "width": width,
        "height": height,
        "brightness": round(brightness, 1),
        "edge_variance": round(edge_variance, 1),
        "cover_candidate_score": max(0, min(100, score)),
        "score_explanation": "Resolution contributes up to 40, balanced brightness 30, edge detail 30. This compares photo quality only; it does not verify a vehicle.",
        "warnings": warnings,
    }
