package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentAdd;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This add subview is an extension of the subview video base class
	public class SubviewAdd extends SubviewVideoBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewAdd(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentAdd.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return (m_pComponent as ComponentAdd).Reactor;
		}
	}
}
