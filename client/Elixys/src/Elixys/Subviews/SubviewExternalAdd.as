package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentExternalAdd;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This external add subview is an extension of the unit operation subview class
	public class SubviewExternalAdd extends SubviewUnitOperation
	{
		/***
		 * Construction
		 **/
		
		public function SubviewExternalAdd(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentExternalAdd.COMPONENTTYPE, 
				RUN_UNITOPERATION_EXTERNALADD, attributes);
		}
		
		/***
		 * Member variables
		 **/
		
		// External add XML
		protected static const RUN_UNITOPERATION_EXTERNALADD:XML = 
			<frame id="unitoperationcontainer" background="#FFFF00" />;
	}
}
