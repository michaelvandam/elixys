package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentInstall;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This install subview is an extension of the unit operation subview class
	public class SubviewInstall extends SubviewUnitOperation
	{
		public function SubviewInstall(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentInstall.COMPONENTTYPE, attributes);
		}
	}
}
