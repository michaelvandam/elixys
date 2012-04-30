package Elixys.Subviews
{
	import Elixys.Assets.Constants;
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	import Elixys.JSON.Components.ComponentInstall;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This install subview is an extension of the subview video message base class
	public class SubviewInstall extends SubviewVideoMessageBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewInstall(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentInstall.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/

		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return (m_pComponent as ComponentInstall).Reactor;
		}

		// Returns the message text
		protected override function GetMessage():String
		{
			return (m_pComponent as ComponentInstall).Message;
		}
	}
}
