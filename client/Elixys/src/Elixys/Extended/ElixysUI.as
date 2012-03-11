package Elixys.Extended
{
	import Elixys.Components.*;
	import Elixys.Extended.Form;
	import Elixys.Views.*;
	
	import com.danielfreeman.madcomponents.*;

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
			var pNewTokens:Array = ["loading", "login", "logo", "progressbar", "navigationbar", "tabbar",
				"datagrid", "datagridbody", "datagridheader", "popup", "sequencer", "sequencerheader",
				"sequencerbody"];
			var pNewClasses:Array = [Loading, Login, Logo, ProgressBar, NavigationBar, TabBar,
				DataGrid, DataGridBody, DataGridHeader, Popup, Sequencer, SequencerHeader,
				SequencerBody];
			UI.extend(pNewTokens, pNewClasses);
		}
	}
}
