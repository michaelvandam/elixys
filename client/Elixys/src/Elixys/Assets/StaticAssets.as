package Elixys.Assets
{
	// This static class embeds the project assets
	public class StaticAssets
	{
		[Embed(source="../../../../Elixys/res/Gotham-Light.otf", 
			fontWeight="light",
			fontName="GothamLight",
    	    fontFamily="Gotham",
			advancedAntiAliasing="true",
			embedAsCFF="false")]
		public static var GothamLight:Class;

		[Embed(source="../../../../Elixys/res/Gotham-Medium.otf", 
			fontWeight="medium",
			fontName="GothamMedium",
    	    fontFamily="Gotham",
			advancedAntiAliasing="true",
			embedAsCFF="false")]
		public static var GothamMedium:Class;
	}
}
