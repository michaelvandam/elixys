package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentEvaporate;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This evaporate subview is an extension of the unit operation subview class
	public class SubviewEvaporate extends SubviewUnitOperation
	{
		public function SubviewEvaporate(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentEvaporate.COMPONENTTYPE, attributes);
		}
	}
}
