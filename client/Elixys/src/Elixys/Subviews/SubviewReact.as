package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentReact;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This react subview is an extension of the subview video base class
	public class SubviewReact extends SubviewVideoBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewReact(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentReact.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return (m_pComponent as ComponentReact).Reactor;
		}
	}
}
