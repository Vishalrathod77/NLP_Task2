from datetime import datetime
import pytz
from typing import AnyStr, Any
from pydantic import BaseModel, Field
from gentopia.tools.basetool import *


class ConvertTimeArgs(BaseModel):
    from_timezone: str = Field(..., description="The source time zone, e.g., America/Los_Angeles")
    to_timezone: str = Field(..., description="The target time zone, e.g., Europe/London")
    date_time: str = Field(..., description="The date and time to be converted in YYYY-MM-DD HH:MM:SS format, e.g., 2024-10-11 15:30:00")


class ConvertTime(BaseTool):
    """Tool that converts the time from one time zone to another using pytz."""

    name = "convert_time"
    description = (
        "A tool to convert the time from one time zone to another. "
        "Input should include the source time zone, target time zone, and the time to convert."
    )
    args_schema: Optional[Type[BaseModel]] = ConvertTimeArgs

    def _run(self, from_timezone: AnyStr, to_timezone: AnyStr, date_time: AnyStr) -> AnyStr:
        try:
            # Input data string
            input_time = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
            
            # Time zone for the source
            from_tz = pytz.timezone(from_timezone)
            input_time = from_tz.localize(input_time)

            # Target time zone
            to_tz = pytz.timezone(to_timezone)
            converted_time = input_time.astimezone(to_tz)

            # Output
            output = f"Converting time from {from_timezone} to {to_timezone} is {converted_time.strftime('%Y-%m-%d %H:%M:%S')}."
            return output

        except pytz.UnknownTimeZoneError:
            return f"Error: Time zone given ('{from_timezone}' or '{to_timezone}') is not recognized."
        except ValueError:
            return f"Error: The time provided ('{date_time}') is not in the correct format. Please use 'YYYY-MM-DD HH:MM:SS'."
        except Exception as e:
            return f"An error occurred: {e}"

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    # Example usage: Convert time from America/Los_Angeles to Europe/London
    ans = ConvertTime()._run("America/Los_Angeles", "Europe/London", "2024-10-11 15:30:00")
    print(ans)
