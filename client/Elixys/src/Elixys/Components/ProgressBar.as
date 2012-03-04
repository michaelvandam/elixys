package Elixys.Components
{
	import Elixys.Assets.Styling;
	import Elixys.Extended.Form;
	
	import com.danielfreeman.madcomponents.*;
	
	import flash.display.Shape;
	import flash.display.Sprite;
	import flash.events.Event;
	
	// This progress bar component is an extension of our extended Form class
	public class ProgressBar extends Form
	{
		/***
		 * Construction
		 **/
		
		public function ProgressBar(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, PROGRESS, attributes);
			
			// Initialize the progress bar
			SetProgress(0);
		}
		
		/***
		 * Member functions
		 **/

		// Sets the progress bar to the specified percentage
		public function SetProgress(fPercent:Number):void
		{
			// Clear the progress area
			graphics.clear();

			// Draw the background rectangle
			graphics.beginFill(Styling.AS3Color(Styling.PROGRESS_BACKGROUND));
			graphics.drawRect(40, 38, width - 40, 8);
			graphics.endFill();

			// Draw the fill rectangle
			graphics.beginFill(Styling.AS3Color(Styling.PROGRESS_FOREGROUND));
			var nWidth:uint = (width - 42) * fPercent;
			if (nWidth > width)
			{
				nWidth = width;
			}
			graphics.drawRect(41, 39, nWidth, 6);
			graphics.endFill();
		}

		/***
		 * Member variables
		 **/
		
		// Progress component XML
		protected static const PROGRESS:XML = 
			<frame visible="false">
				<columns gapH="0" widths="40,100%,40">
					<frame />
					<rows gapV="0" heights="38,8">
						<label useEmbedded="true" alignH="left" alignV="top">
							<font face="GothamMedium" color={Styling.TEXT_GRAY1} size="18">
								LOADING
							</font>
						</label>
					</rows>
					<frame />
				</columns>
			</frame>;
	}
}
