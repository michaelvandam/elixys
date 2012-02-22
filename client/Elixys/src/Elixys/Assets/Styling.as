package Elixys.Assets
{
	// This static class contains the basic styling strings
	public class Styling
	{
		// Colors
		public static var PROGRESS_BACKGROUND:String = "#CCCCCC";
		public static var PROGRESS_FOREGROUND:String = "#FFFFFF";
		public static var APPLICATION_BACKGROUND:String = "#FFFFFF";
		public static var TEXT_GRAY:String = "#3B3036";
		public static var TEXT_LIGHTGRAY:String = "#BBBBBB";
		
		// Get the HTML color as an Actionscript value
		public static function AS3Color(sColor:String):uint
		{
			sColor = sColor.replace("#", "0x");
			return uint(sColor);
		}
	}
}
