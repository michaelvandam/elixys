package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentMove;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This move subview is an extension of the unit operation subview class
	public class SubviewMove extends SubviewUnitOperation
	{
		public function SubviewMove(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentMove.COMPONENTTYPE, attributes);
		}
	}
}
