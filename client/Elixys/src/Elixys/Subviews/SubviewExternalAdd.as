package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentExternalAdd;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This external add subview is an extension of the sunview video message base class
	public class SubviewExternalAdd extends SubviewVideoMessageBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewExternalAdd(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentExternalAdd.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return (m_pComponent as ComponentExternalAdd).Reactor;
		}
		
		// Returns the message text
		protected override function GetMessage():String
		{
			return (m_pComponent as ComponentExternalAdd).Message;
		}
	}
}
