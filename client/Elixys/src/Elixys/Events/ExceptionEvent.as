package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used to relay error messages
	public class ExceptionEvent extends Event
	{
		// Constructor
		public function ExceptionEvent(sException:String, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			exception = sException;
			super(EXCEPTION, bubbles, cancelable);
		}

		// Event name
		static public var EXCEPTION:String = "ElixysExceptionEvent";
		
		// Error string
		public var exception:String = "";
	}
}
