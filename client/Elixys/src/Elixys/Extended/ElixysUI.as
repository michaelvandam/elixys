package Elixys.Extended
{
	import com.danielfreeman.madcomponents.*;
		
	import Elixys.Extended.Form;
	import Elixys.Views.*;
	import Elixys.Components.*;

	// This ElixysUI class is an extension of MadComponent's UI class
	public class ElixysUI extends com.danielfreeman.madcomponents.UI
	{
		// Initialize the extended class
		public static function Initialize():void
		{
			// Set the form class to our extended version
			UI["_FormClass"] = Form;
			var nIndex:int = UI["_tokens"].indexOf("frame");
			if (nIndex != -1)
			{
				UI["_classes"][nIndex] = Form;
			}

			// Extend the UI tokens with our custom classes
			var pNewTokens:Array = ["loading", "login", "logo", "progress", "navigationbar"];
			var pNewClasses:Array = [Loading, Login, Logo, Progress, NavigationBar];
			UI.extend(pNewTokens, pNewClasses);
		}
	}
}
