package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentMix;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This mix subview is an extension of the unit operation subview class
	public class SubviewMix extends SubviewUnitOperation
	{
		public function SubviewMix(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentMix.COMPONENTTYPE, attributes);
		}
	}
}
