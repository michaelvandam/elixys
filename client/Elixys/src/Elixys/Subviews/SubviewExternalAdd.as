package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentExternalAdd;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This external add subview is an extension of the unit operation subview class
	public class SubviewExternalAdd extends SubviewUnitOperation
	{
		public function SubviewExternalAdd(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentExternalAdd.COMPONENTTYPE, attributes);
		}
	}
}
