package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentTransfer;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This transfer subview is an extension of the unit operation subview class
	public class SubviewTransfer extends SubviewUnitOperation
	{
		public function SubviewTransfer(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentTransfer.COMPONENTTYPE, attributes);
		}
	}
}
