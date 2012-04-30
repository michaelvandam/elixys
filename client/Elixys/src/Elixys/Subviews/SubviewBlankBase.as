package Elixys.Subviews
{
	import Elixys.Assets.Styling;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This subview blank base is an extension of the subview unit operation base class
	public class SubviewBlankBase extends SubviewUnitOperationBase
	{
		/***
		 * Construction
		 **/

		public function SubviewBlankBase(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										 sComponentType:String, attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, sComponentType, RUN_BLANK, attributes);
		}

		/***
		 * Member variables
		 **/
		
		// Run XML
		protected static const RUN_BLANK:XML = 
			<frame id="unitoperationcontainer" background={Styling.APPLICATION_BACKGROUND} />;
	}
}
