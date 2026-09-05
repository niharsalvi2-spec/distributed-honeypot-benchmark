"""
Timestamp Normalizer.
Converts heterogeneous timestamp formats (ISO-8601, epoch float, RFC 3339)
into standardized UTC ISO-8601 strings with millisecond precision.
"""
from datetime import datetime, timezone
from typing import Any
import dateutil.parser

class TimestampNormalizer:
    @staticmethod
    def normalize(raw_ts: Any) -> str:
        """Parses any timestamp representation and returns YYYY-MM-DDTHH:MM:SS.fffZ."""
        if not raw_ts:
            return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        # Float or int epoch
        if isinstance(raw_ts, (int, float)):
            dt = datetime.fromtimestamp(raw_ts, tz=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            
        if isinstance(raw_ts, str):
            try:
                # Try dateutil parser
                dt = dateutil.parser.parse(raw_ts)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            except Exception:
                pass
                
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
