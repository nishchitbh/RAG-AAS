import re
import csv
from io import StringIO
from typing import Dict, List, Any
from fastapi.responses import StreamingResponse
from api.shared.domain.exceptions import InvalidInputException


class SharedServices:
    @staticmethod
    def dict_to_streaming_response(
        data: Dict[str, List[Any]],
        filename: str = "data.csv",
        media_type: str = "text/csv",
    ) -> StreamingResponse:
        lengths = {len(v) for v in data.values()}
        if len(lengths) != 1:
            raise InvalidInputException(
                f"All columns must have the same length, got lengths: {lengths}"
            )
        output = StringIO()
        writer = csv.writer(output)
        headers = list(data.keys())
        writer.writerow(headers)
        for row in zip(*data.values()):
            writer.writerow(row)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @staticmethod
    def filename_sanitizer(filename: str) -> str:
        illegal_pattern = r'[<>:"/\\|?*@\x00-\x1F]'
        sanitized = re.sub(illegal_pattern, "_", filename)
        return sanitized.split("_")[0]
