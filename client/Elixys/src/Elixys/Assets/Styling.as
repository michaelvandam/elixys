package Elixys.Assets
{
	// This static class contains the basic styling strings
	public class Styling
	{
		// Colors
		public static var PROGRESS_BACKGROUND:String = "#CCCCCC";
		public static var PROGRESS_FOREGROUND:String = "#FFFFFF";
		public static var APPLICATION_BACKGROUND:String = "#FFFFFF";
		public static var TEXT_BLACK:String = "#000000";
		public static var TEXT_DARKERGRAY:String = "#3B3036";
		public static var TEXT_DARKGRAY:String = "#666666";
		public static var TEXT_GRAY:String = "#7A7A7A";
		public static var TEXT_LIGHTGRAY:String = "#BBBBBB";
		public static var TEXT_LIGHTERGRAY:String = "#CCCCCC";
		public static var TEXT_WHITE:String = "#FFFFFF";
		public static var TEXT_RED:String = "#FF3333";
		
		// Get the HTML color as an Actionscript value
		public static function AS3Color(sColor:String):uint
		{
			sColor = sColor.replace("#", "0x");
			return uint(sColor);
		}
	}
}
