package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentMix;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This mix subview is an extension of the subview video base class
	public class SubviewMix extends SubviewVideoBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewMix(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentMix.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return (m_pComponent as ComponentMix).Reactor;
		}
	}
}
