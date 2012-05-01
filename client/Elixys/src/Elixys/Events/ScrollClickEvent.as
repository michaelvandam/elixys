package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used to relay scroll click messages
	public class ScrollClickEvent extends Event
	{
		// Constructor
		public function ScrollClickEvent(nX:Number, nY:Number, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			x = nX;
			y = nY;
			super(CLICK, bubbles, cancelable);
		}

		// Event name
		static public var CLICK:String = "ScrollClickEvent";
		
		// Click position
		public var x:Number = 0;
		public var y:Number = 0;
	}
}
