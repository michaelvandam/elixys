package Elixys.Objects
{
	// This class provides a set of static functions for working with Elixys times.  The format used in the system
	// for a tme is "HH:MM.SS"
	public class TimeUtils
	{
		// Returns the total number of minutes in the time string (includes hours, excludes seconds)
		public static function GetMinutes(sTime:String):uint
		{
			// Ignore if empty
			if (sTime == "")
			{
				return 0;
			}
			
			// Break into components
			var pComponents:Object = new Object();
			if (!ProcessTime(sTime, pComponents))
			{
				throw Error("Invalid time format");
			}
			
			// Calculate and return minutes
			return ((pComponents.hours * 60) + pComponents.minutes);
		}

		// Returns the total number of seconds in the time string (excludes hours and minutes)
		public static function GetSeconds(sTime:String):uint
		{
			// Ignore if empty
			if (sTime == "")
			{
				return 0;
			}
			
			// Break into components
			var pComponents:Object = new Object();
			if (!ProcessTime(sTime, pComponents))
			{
				throw Error("Invalid time format");
			}
			
			// Return seconds
			return (pComponents.seconds);
		}
		
		// Format a time string with the given number of minutes and seconds
		public static function FormatTime(nMinutes:uint, nSeconds:uint):String
		{
			// Break the hours component out of minutes
			var nHours:uint = 0;
			if (nMinutes > 59)
			{
				nHours = (nMinutes - (nMinutes % 60)) / 60;
				nMinutes = nMinutes % 60;
			}
			
			// Format
			var sTime:String = "";
			if (nHours <= 9)
			{
				sTime += "0";
			}
			sTime += nHours.toString() + ":";
			if (nMinutes <= 9)
			{
				sTime += "0";
			}
			sTime += nMinutes.toString() + ".";
			if (nSeconds <= 9)
			{
				sTime += "0";
			}
			sTime += nSeconds.toString();
			return sTime;
		}
		
		// Validates and separates the time string
		private static function ProcessTime(sTime:String, pReturn:Object):Boolean
		{
			// Validate
			if (sTime.length != 8)
			{
				return false;
			}
			if ((sTime.charAt(0) < '0') || (sTime.charAt(0) > '9') ||
				(sTime.charAt(1) < '0') || (sTime.charAt(1) > '9') ||
				(sTime.charAt(2) != ':') ||
				(sTime.charAt(3) < '0') || (sTime.charAt(3) > '9') ||
				(sTime.charAt(4) < '0') || (sTime.charAt(4) > '9') ||
				(sTime.charAt(5) != '.') ||
				(sTime.charAt(6) < '0') || (sTime.charAt(6) > '9') ||
				(sTime.charAt(7) < '0') || (sTime.charAt(7) > '9'))
			{
				return false;
			}
			
			// Parse
			pReturn.hours = parseInt(sTime.substr(0, 2));
			pReturn.minutes = parseInt(sTime.substr(3, 2));
			pReturn.seconds = parseInt(sTime.substr(6, 2));
			return true;
		}
	}
}