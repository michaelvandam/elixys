package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentMove;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This move subview is an extension of the subview video base class
	public class SubviewMove extends SubviewVideoBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewMove(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentMove.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return (m_pComponent as ComponentMove).Reactor;
		}
	}
}
