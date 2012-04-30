package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentInitialize;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This initialize subview is an extension of the subview blank base class
	public class SubviewInitialize extends SubviewBlankBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewInitialize(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentInitialize.COMPONENTTYPE, attributes);
		}
	}
}
