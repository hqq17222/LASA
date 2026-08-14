"""Extract EXIF GPS and metadata from image files using Pillow."""
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _convert_dms_to_decimal(dms: tuple, ref: str) -> float:
    """Convert DMS (degrees, minutes, seconds) tuple to decimal degrees."""
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ('S', 'W'):
        decimal = -decimal
    return round(decimal, 8)


def extract_exif(file_path: str) -> Dict[str, Any]:
    """Extract EXIF metadata including GPS from an image file.

    Returns dict with keys:
        lon, lat, altitude, photo_time, camera_make, camera_model,
        width, height, has_gps, raw_gps_info
    """
    result = {
        "lon": None,
        "lat": None,
        "altitude": None,
        "photo_time": None,
        "camera_make": "",
        "camera_model": "",
        "width": 0,
        "height": 0,
        "has_gps": False,
        "raw_gps_info": None,
    }
    try:
        with Image.open(file_path) as img:
            result["width"] = img.width
            result["height"] = img.height
            exif = img._getexif()
            if not exif:
                return result

            # Basic EXIF tags
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":
                    try:
                        result["photo_time"] = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    except Exception:
                        pass
                elif tag_name == "DateTime":
                    if not result["photo_time"]:
                        try:
                            result["photo_time"] = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                        except Exception:
                            pass
                elif tag_name == "Make":
                    result["camera_make"] = str(value).strip()
                elif tag_name == "Model":
                    result["camera_model"] = str(value).strip()
                elif tag_name == "GPSInfo":
                    result["raw_gps_info"] = value

            # GPS Info
            if result["raw_gps_info"]:
                gps_info = {}
                for key in result["raw_gps_info"].keys():
                    gps_tag_name = GPSTAGS.get(key, key)
                    gps_info[gps_tag_name] = result["raw_gps_info"][key]

                if "GPSLatitude" in gps_info and "GPSLatitudeRef" in gps_info:
                    result["lat"] = _convert_dms_to_decimal(
                        gps_info["GPSLatitude"], gps_info["GPSLatitudeRef"]
                    )
                if "GPSLongitude" in gps_info and "GPSLongitudeRef" in gps_info:
                    result["lon"] = _convert_dms_to_decimal(
                        gps_info["GPSLongitude"], gps_info["GPSLongitudeRef"]
                    )
                if "GPSAltitude" in gps_info:
                    try:
                        alt = gps_info["GPSAltitude"]
                        if isinstance(alt, tuple):
                            result["altitude"] = round(float(alt[0]) / float(alt[1]), 2)
                        else:
                            result["altitude"] = round(float(alt), 2)
                    except Exception:
                        pass

                if result["lon"] is not None and result["lat"] is not None:
                    result["has_gps"] = True

    except Exception as e:
        # Log but don't crash
        print(f"EXIF extraction error for {file_path}: {e}")

    return result


def guess_flight_route(filename: str) -> str:
    """Guess flight route from filename patterns like 'A01_001.jpg' or 'route-B-005.jpg'."""
    import re
    name = Path(filename).stem.upper()
    # Match patterns like A01, B03, Route-A, etc.
    m = re.search(r'([A-Z]\d{1,2})', name)
    if m:
        return f"航线-{m.group(1)}"
    m = re.search(r'ROUTE[_-]?([A-Z]\d{0,2})', name)
    if m:
        return f"航线-{m.group(1)}"
    return "航线-默认"


def guess_flight_date(exif_time: Optional[datetime], filename: str) -> str:
    """Guess flight date from EXIF time or filename."""
    if exif_time:
        return exif_time.strftime("%Y-%m-%d")
    import re
    # Try to extract date from filename like 20260715_xxx.jpg
    m = re.search(r'(\d{4})[._-]?(\d{2})[._-]?(\d{2})', Path(filename).stem)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    from datetime import datetime as dt
    return dt.now().strftime("%Y-%m-%d")
