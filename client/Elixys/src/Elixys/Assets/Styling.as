package Elixys.Assets
{
	// This static class contains the basic styling strings
	public class Styling
	{
		// Colors
		public static var POPUP_BACKGROUND:String = "#FFFFFF";
		public static var DATAGRID_HEADERLINE:String = "#EBEBEB";
		public static var DATAGRID_HEADERPRESSED:String = "#E3E9EE";
		public static var DATAGRID_SELECTED:String = "#B2E6F3";
		public static var TABBAR_LINE:String = "#EBEBEB";
		public static var TABBAR_PRESSED:String = "#E3E9EE";
		public static var PROGRESS_BACKGROUND:String = "#CCCCCC";
		public static var PROGRESS_FOREGROUND:String = "#FFFFFF";
		public static var APPLICATION_BACKGROUND:String = "#FFFFFF";
		public static var TEXT_BLACK:String = "#000000";
		public static var TEXT_GRAY1:String = "#3B3036";
		public static var TEXT_GRAY2:String = "#666666";
		public static var TEXT_GRAY3:String = "#7A7A7A";
		public static var TEXT_GRAY4:String = "#999999";
		public static var TEXT_GRAY5:String = "#BBBBBB";
		public static var TEXT_GRAY6:String = "#CCCCCC";
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
