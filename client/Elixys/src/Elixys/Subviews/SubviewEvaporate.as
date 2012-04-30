package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentEvaporate;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This evaporate subview is an extension of the subview video base class
	public class SubviewEvaporate extends SubviewVideoBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewEvaporate(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentEvaporate.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return (m_pComponent as ComponentEvaporate).Reactor;
		}
	}
}
