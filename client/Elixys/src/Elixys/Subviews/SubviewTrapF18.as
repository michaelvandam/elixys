package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentTrapF18;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This trap F18 subview is an extension of the unit operation subview class
	public class SubviewTrapF18 extends SubviewUnitOperation
	{
		public function SubviewTrapF18(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentTrapF18.COMPONENTTYPE, attributes);
		}
	}
}
