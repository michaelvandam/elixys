package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentEluteF18;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This elute F18 subview is an extension of the subview video base class
	public class SubviewEluteF18 extends SubviewVideoBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewEluteF18(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentEluteF18.COMPONENTTYPE, attributes);
		}
		
		/***
		 * Member functions
		 **/
		
		// Returns the reactor number
		protected override function GetReactor():uint
		{
			return 1;
		}
	}
}
