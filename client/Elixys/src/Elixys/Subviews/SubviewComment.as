package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentComment;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This comment subview is an extension of the subview blank base class
	public class SubviewComment extends SubviewBlankBase
	{
		/***
		 * Construction
		 **/
		
		public function SubviewComment(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentComment.COMPONENTTYPE, attributes);
		}
	}
}
