const MAX_ORIGINAL_BYTES = 8 * 1024 * 1024;
const MAX_UPLOAD_BYTES = 3 * 1024 * 1024;

/** Preserve the original upload policy while fitting hosted request limits. */
export async function prepareUploadImage(file: File): Promise<File> {
  if (
    !["image/jpeg", "image/png", "image/webp"].includes(file.type) ||
    file.size > MAX_ORIGINAL_BYTES
  ) {
    throw new Error("Use JPG, PNG or WebP images, up to 8 MB each.");
  }
  if (file.size <= MAX_UPLOAD_BYTES) return file;
  let bitmap: ImageBitmap;
  try {
    bitmap = await createImageBitmap(file);
  } catch {
    throw new Error(
      "This image could not be decoded. Export it as a JPG, PNG or WebP and try again.",
    );
  }
  try {
    const scale = Math.min(1, 2400 / bitmap.width, 1600 / bitmap.height);
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(bitmap.width * scale));
    canvas.height = Math.max(1, Math.round(bitmap.height * scale));
    const context = canvas.getContext("2d");
    if (!context)
      throw new Error(
        "Your browser could not prepare this image. Try an image smaller than 3 MB.",
      );
    context.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    for (const quality of [0.92, 0.82, 0.72, 0.62]) {
      const blob = await new Promise<Blob | null>((resolve) =>
        canvas.toBlob(resolve, "image/webp", quality),
      );
      if (blob && blob.type === "image/webp" && blob.size <= MAX_UPLOAD_BYTES) {
        return new File([blob], `${file.name.replace(/\.[^.]+$/, "")}.webp`, {
          type: "image/webp",
          lastModified: file.lastModified,
        });
      }
    }
    throw new Error(
      "This image could not be reduced for upload. Export a smaller image under 3 MB and try again.",
    );
  } finally {
    bitmap.close();
  }
}
