package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used by the Elixys SWF to inform the container when the user logs out
	public class LogoutEvent extends Event
	{
		// Constructor
		public function LogoutEvent(sError:String, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			error = sError;
			super(LOGOUT, bubbles, cancelable);
		}

		// Event name
		static public var LOGOUT:String = "LogoutEvent";
		
		// Error string
		public var error:String = "";
	}
}
