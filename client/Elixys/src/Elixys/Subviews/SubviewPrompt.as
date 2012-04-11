package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentPrompt;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This prompt subview is an extension of the unit operation subview class
	public class SubviewPrompt extends SubviewUnitOperation
	{
		public function SubviewPrompt(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentPrompt.COMPONENTTYPE, attributes);
		}
	}
}
