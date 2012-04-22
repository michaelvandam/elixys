package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentEluteF18;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This elute F18 subview is an extension of the unit operation subview class
	public class SubviewEluteF18 extends SubviewUnitOperation
	{
		/***
		 * Construction
		 **/
		
		public function SubviewEluteF18(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentEluteF18.COMPONENTTYPE, 
				SubviewUnitOperation.RUN_UNITOPERATION_ONEVIDEO, attributes);
		}
	}
}
