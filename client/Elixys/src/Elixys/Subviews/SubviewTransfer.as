package Elixys.Subviews
{
	import Elixys.JSON.Components.ComponentTransfer;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Sprite;

	// This transfer subview is an extension of the unit operation subview class
	public class SubviewTransfer extends SubviewUnitOperation
	{
		/***
		 * Construction
		 **/
		
		public function SubviewTransfer(screen:Sprite, sMode:String, pElixys:Elixys, nButtonWidth:Number,
										attributes:Attributes)
		{
			super(screen, sMode, pElixys, nButtonWidth, ComponentTransfer.COMPONENTTYPE, 
				RUN_UNITOPERATION_TRANSFER, attributes);
		}
		
		/***
		 * Member variables
		 **/
		
		// Install XML
		protected static const RUN_UNITOPERATION_TRANSFER:XML = 
			<frame id="unitoperationcontainer" background="#FFFF00" />;
	}
}
