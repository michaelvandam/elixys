package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentComment;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This comment subview is an extension of the unit operation subview class
	public class SubviewComment extends SubviewUnitOperation
	{
		/***
		 * Construction
		 **/
		
		public function SubviewComment(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentComment.COMPONENTTYPE, 
				SubviewUnitOperation.RUN_UNITOPERATION_BLANK, attributes);
		}
	}
}
