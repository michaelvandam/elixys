package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentReact;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This react subview is an extension of the unit operation subview class
	public class SubviewReact extends SubviewUnitOperation
	{
		public function SubviewReact(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentReact.COMPONENTTYPE, attributes);
		}
	}
}
