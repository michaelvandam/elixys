package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used to relay button click messages
	public class ButtonEvent extends Event
	{
		// Constructor
		public function ButtonEvent(sButton:String, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			button = sButton;
			super(CLICK, bubbles, cancelable);
		}

		// Event name
		static public var CLICK:String = "ButtonClick";
		
		// Button name
		public var button:String = "";
	}
}
