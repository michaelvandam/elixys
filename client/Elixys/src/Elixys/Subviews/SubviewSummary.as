package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentSummary;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;
	import flash.text.TextFieldAutoSize;

	// This summary subview is an extension of the subview message base class
	public class SubviewSummary extends SubviewMessageBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewSummary(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentSummary.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the message text
		protected override function GetMessage():String
		{
			return (m_pComponent as ComponentSummary).Message;
		}
	}
}
