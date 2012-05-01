package Elixys.Extended
{
	import Elixys.Events.ScrollClickEvent;
	
	import com.danielfreeman.madcomponents.Attributes;
	import com.danielfreeman.madcomponents.UIScrollVertical;
	
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;

	// This scroll vertical component is an extension of MadComponent's UIScrollVertical class
	public class ScrollVertical extends UIScrollVertical
	{
		/***
		 * Construction
		 **/
		
		public function ScrollVertical(screen:Sprite, xml:XML, attributes:Attributes, bDefaultHitTest:Boolean = true)
		{
			// Call the base constructor
			super(screen, xml, attributes);
			
			// Remember the default hit test flag
			m_bDefaultHitTest = bDefaultHitTest;
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

		// Overridden search hit function
		protected override function doSearchHit():void
		{
			// Call the base handler or dispatch an event
			if (m_bDefaultHitTest)
			{
				super.doSearchHit();
			}
			else
			{
				dispatchEvent(new ScrollClickEvent(_slider.mouseX, _slider.mouseY));
			}
		}

		/***
		 * Member variables
		 **/

		// Slider moved event
		public static var SLIDER_MOVED:String = "sliderMovedEvent";
		
		// Default hit test flag
		protected var m_bDefaultHitTest:Boolean;
	}
}
