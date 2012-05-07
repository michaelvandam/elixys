package Elixys.Events
{
	import flash.events.Event;

	// This custom event is used to relay status messages
	public class StatusEvent extends Event
	{
		// Constructor
		public function StatusEvent(sStatus:String, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			status = sStatus;
			super(STATUS, bubbles, cancelable);
		}

		// Event name
		static public const STATUS:String = "ElixysStatusEvent";
		
		// Status
		public var status:String = "";
		
		// Status types
		static public const SERVERNOTRESPONDING:String = "ServerNotResponding";
		static public const SERVERRESPONDED:String = "ServerResponded";
	}
}
