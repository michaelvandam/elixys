package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentBase;
	import Elixys.JSON.Components.ComponentPrompt;
	import Elixys.JSON.State.RunState;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This prompt subview is an extension of the subview message base class
	public class SubviewPrompt extends SubviewMessageBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewPrompt(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentPrompt.COMPONENTTYPE, attributes);
		}

		/***
		 * Member functions
		 **/
		
		// Returns the message text
		protected override function GetMessage():String
		{
			return (m_pComponent as ComponentPrompt).Message;
		}
	}
}
