package Elixys.Extended
{
	import com.danielfreeman.madcomponents.Attributes;
	import com.danielfreeman.madcomponents.UIScrollVertical;
	
	import flash.display.Sprite;
	import flash.events.Event;

	// This scroll vertical component is an extension of MadComponent's UIScrollVertical class
	public class ScrollVertical extends UIScrollVertical
	{
		/***
		 * Construction
		 **/
		
		public function ScrollVertical(screen:Sprite, xml:XML, attributes:Attributes)
		{
			// Call the base constructor
			super(screen, xml, attributes);
		}
		
		/***
		 * Member functions
		 **/

		// Detect slider movement
		protected override function sliderMoved():void
		{
			// Dispatch slider moved event
			dispatchEvent(new Event(SLIDER_MOVED));
		}
		
		// Returns the maximum slide
		public function get MaximumSlide():Number
		{
			return _maximumSlide;
		}

		/***
		 * Member variables
		 **/

		// Slider moved event
		public static var SLIDER_MOVED:String = "sliderMovedEvent";
	}
}
