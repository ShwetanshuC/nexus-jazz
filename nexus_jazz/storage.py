from __future__ import annotations
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

MAX_PX = 3840


def _process(content):
    try:
        from PIL import Image, ImageOps
        content.seek(0)
        original_ext = None
        if hasattr(content, 'name') and '.' in content.name:
            original_ext = content.name.rsplit('.', 1)[1].lower()
        img = Image.open(content)
        img = ImageOps.exif_transpose(img)
        w, h = img.size
        needs_resize = max(w, h) > MAX_PX
        if original_ext == 'jpg' and not needs_resize and img.mode == 'RGB':
            content.seek(0)
            return content, ".jpg"
        if needs_resize:
            if w >= h:
                img = img.resize((MAX_PX, round(h * MAX_PX / w)), Image.LANCZOS)
            else:
                img = img.resize((round(w * MAX_PX / h), MAX_PX), Image.LANCZOS)
        if img.mode in ("RGBA", "P", "LA"):
            bg = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode in ("RGBA", "LA"):
                bg.paste(img, mask=img.split()[-1])
            else:
                bg.paste(img)
            img = bg
        elif img.mode != "RGB":
            img = img.convert("RGB")
        out = BytesIO()
        img.save(out, format="JPEG", quality=85, progressive=True, optimize=False)
        out.seek(0)
        return ContentFile(out.read()), ".jpg"
    except Exception:
        try:
            content.seek(0)
        except Exception:
            pass
        return content, None


class ResizingFileSystemStorage(FileSystemStorage):
    def _save(self, name: str, content):
        if name and self.exists(name):
            try:
                self.delete(name)
            except Exception:
                pass
        new_content, ext = _process(content)
        if ext and "." in name:
            name = name.rsplit(".", 1)[0] + ext
        return super()._save(name, new_content)


def _make_resizing_s3():
    try:
        from storages.backends.s3boto3 import S3Boto3Storage
    except ImportError:
        return None

    class ResizingS3Storage(S3Boto3Storage):
        def _save(self, name, content):
            new_content, ext = _process(content)
            if ext and "." in name:
                name = name.rsplit(".", 1)[0] + ext
            saved_name = super()._save(name, new_content)
            # Mirror to local disk so nginx serves it instantly, no S3 round-trip.
            try:
                from pathlib import Path
                from django.conf import settings
                local_path = Path(settings.MEDIA_ROOT) / saved_name
                local_path.parent.mkdir(parents=True, exist_ok=True)
                new_content.seek(0)
                local_path.write_bytes(new_content.read())
            except Exception:
                pass
            return saved_name

    return ResizingS3Storage


try:
    ResizingS3Storage = _make_resizing_s3()
except Exception:
    ResizingS3Storage = None
