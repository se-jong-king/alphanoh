#현재 시간 알려주는 기능

import json
from datetime import datetime
import pytz

def now(tz:str="Asia/Seoul"):
  """Get the current date and time.
  """
  return json.dumps({
    "timezone": tz,
    "time": datetime.now(pytz.timezone(tz)).strftime("%Y-%m-%d %H:%M:%S"),
  })